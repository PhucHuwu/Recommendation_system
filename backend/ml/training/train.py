"""
Training Pipeline for New Recommendation Models

Trains User-Based CF, Item-Based CF, and Hybrid models with:
- Stratified user-based data splitting
- Comprehensive evaluation
- Hyperparameter optimization for hybrid weights
"""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.models.user_based import UserBasedCF
from ml.models.item_based import ItemBasedCF
from ml.models.hybrid import HybridWeightedCF
from ml.models.neural_cf import NeuralCF
from ml.training.evaluate import evaluate_model, compare_models
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

# Load environment variables
load_dotenv()


def get_db_connection():
    """Get MongoDB database connection"""
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    mongodb_db = os.getenv('MONGODB_DB', 'anime_recommendation')
    client = MongoClient(mongodb_uri)
    return client[mongodb_db]


def load_data_from_mongodb() -> Tuple[List[dict], List[dict]]:
    """Load ratings and animes data from MongoDB"""
    print("Loading data from MongoDB...")
    
    db = get_db_connection()
    ratings_collection = db['ratings']
    animes_collection = db['animes']
    
    # Load ratings
    ratings_cursor = ratings_collection.find({}, {
        '_id': 0,
        'user_id': 1,
        'anime_id': 1,
        'rating': 1
    })
    ratings_data = list(ratings_cursor)
    
    # Load animes
    animes_cursor = animes_collection.find({})
    animes_data = list(animes_cursor)
    
    print(f"  Loaded {len(ratings_data):,} ratings")
    print(f"  Loaded {len(animes_data):,} animes")
    
    return ratings_data, animes_data


def split_by_user(ratings_data: List[dict], test_ratio: float = 0.2, 
                  min_ratings: int = 5, seed: int = 42) -> Tuple[List[dict], List[dict]]:
    """
    Stratified split by user - chia ratings của MỖI user theo train/test ratio
    
    Benefits:
    - All users in test also in train (no cold start)
    - Preserves user rating patterns
    - Fair evaluation
    
    Args:
        ratings_data: List of rating dicts
        test_ratio: Fraction for test set (0-1)
        min_ratings: Min ratings per user to include in  test
        seed: Random seed
        
    Returns:
        (train_data, test_data)
    """
    random.seed(seed)
    np.random.seed(seed)
    
    print(f"\nSplitting data (Stratified by User, {int((1-test_ratio)*100)}/{int(test_ratio*100)})...")
    
    # Group by user
    user_ratings = defaultdict(list)
    for rating in ratings_data:
        user_ratings[rating['user_id']].append(rating)
    
    train_data = []
    test_data = []
    
    for user_id, ratings in user_ratings.items():
        # Shuffle user's ratings
        random.shuffle(ratings)
        
        # If user has enough ratings, split them
        if len(ratings) >= min_ratings:
            split_point = int(len(ratings) * (1 - test_ratio))
            train_data.extend(ratings[:split_point])
            test_data.extend(ratings[split_point:])
        else:
            # Too few ratings, put all in train
            train_data.extend(ratings)
    
    print(f"  Train: {len(train_data):,} ratings ({len(set([r['user_id'] for r in train_data])):,} users)")
    print(f"  Test: {len(test_data):,} ratings ({len(set([r['user_id'] for r in test_data])):,} users)")
    
    return train_data, test_data


def optimize_hybrid_weights(user_model: UserBasedCF, item_model: ItemBasedCF,
                           train_data: List[dict], test_data: List[dict]) -> float:
    """
    Find optimal weight for hybrid model using grid search
    
    Strategy:
    - Try different weights (0.0 to 1.0)
    - Evaluate on validation set (sample of test)
    - Pick weight with best RMSE
    
    Args:
        user_model: Trained user-based model
        item_model: Trained item-based model
        train_data: Training data
        test_data: Testing data
        
    Returns:
        Optimal user_weight (alpha)
    """
    print(f"\n{'='*60}")
    print("OPTIMIZING HYBRID WEIGHTS")
    print(f"{'='*60}")
    
    # Sample validation set (smaller for speed)
    val_size = min(1000, len(test_data))
    val_data = random.sample(test_data, val_size)
    
    best_alpha = 0.5
    best_rmse = float('inf')
    
    # Grid search
    alphas = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    print(f"\nTrying {len(alphas)} different weights on {val_size} validation samples...")
    
    for alpha in alphas:
        hybrid = HybridWeightedCF(user_model, item_model, 
                                  user_weight=alpha, item_weight=1-alpha)
        
        # Compute RMSE on validation
        errors = []
        for rating in val_data:
            pred = hybrid.predict(rating['user_id'], rating['anime_id'])
            if pred > 0:
                errors.append((rating['rating'] - pred) ** 2)
        
        if len(errors) > 0:
            rmse = np.sqrt(np.mean(errors))
            print(f"  α={alpha:.1f}: RMSE={rmse:.4f} ({len(errors)} predictions)")
            
            if rmse < best_rmse:
                best_rmse = rmse
                best_alpha = alpha
    
    print(f"\nBest weight: α={best_alpha:.1f} (RMSE={best_rmse:.4f})")
    
    return best_alpha


def update_model_registry(model_name: str, metrics: Optional[Dict[str, float]] = None, is_active: bool = False):
    """Update model registry in database"""
    db = get_db_connection()
    registry = db['model_registry']
    
    from datetime import datetime
    
    # If activating this model, deactivate all others first
    if is_active:
        registry.update_many({}, {'$set': {'is_active': False}})
    
    update_data = {
        'model_name': model_name,
        'trained_at': datetime.now(),
        'is_active': is_active
    }
    
    if metrics:
        update_data['metrics'] = metrics
    
    registry.update_one(
        {'model_name': model_name},
        {'$set': update_data},
        upsert=True
    )


def train_neural_cf(train_data: List[dict], test_data: List[dict]) -> Tuple[NeuralCF, Dict[str, float]]:
    """
    Train Neural Collaborative Filtering model
    
    Args:
        train_data: Training ratings
        test_data: Test ratings for validation
        
    Returns:
        (trained_model, metrics)
    """
    print("\nPreparing NCF training data...")
    
    # Get unique user and item IDs
    all_data = train_data + test_data
    user_ids = set(r['user_id'] for r in all_data)
    item_ids = set(r['anime_id'] for r in all_data)
    
    # Create user/item ID mappings (NCF expects continuous IDs from 0)
    user_id_map = {uid: idx for idx, uid in enumerate(sorted(user_ids))}
    item_id_map = {iid: idx for idx, iid in enumerate(sorted(item_ids))}
    
    # Map IDs in data
    mapped_train = []
    for r in train_data:
        if r['user_id'] in user_id_map and r['anime_id'] in item_id_map:
            mapped_train.append({
                'user_id': user_id_map[r['user_id']],
                'anime_id': item_id_map[r['anime_id']],
                'rating': r['rating']
            })
    
    mapped_test = []
    for r in test_data:
        if r['user_id'] in user_id_map and r['anime_id'] in item_id_map:
            mapped_test.append({
                'user_id': user_id_map[r['user_id']],
                'anime_id': item_id_map[r['anime_id']],
                'rating': r['rating']
            })
    
    print(f"  Mapped {len(mapped_train):,} train ratings")
    print(f"  Mapped {len(mapped_test):,} test ratings")
    print(f"  Users: {len(user_id_map):,}")
    print(f"  Items: {len(item_id_map):,}")
    
    # Initialize model
    print("\nInitializing Neural CF model...")
    model = NeuralCF(
        num_users=len(user_id_map),
        num_items=len(item_id_map),
        embedding_dim=64,
        mlp_layers=[128, 64, 32],
        dropout=0.2
    )
    
    # Train
    print("\nTraining Neural CF...")
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"  Device: {device}")
    
    model.fit(
        train_data=mapped_train,
        val_data=mapped_test,
        epochs=30,
        batch_size=256,
        lr=0.001,
        early_stopping=5,
        device=device
    )
    
    # Save ID mappings with model
    model.user_id_map = user_id_map
    model.item_id_map = item_id_map
    model.reverse_user_map = {v: k for k, v in user_id_map.items()}
    model.reverse_item_map = {v: k for k, v in item_id_map.items()}
    
    # Evaluate
    print("\nEvaluating Neural CF...")
    metrics = evaluate_model(model, train_data, test_data, k=10)
    
    return model, metrics


def main():
    """Main training pipeline"""
    print("\n" + "="*80)
    print("TRAINING PIPELINE - NEW MODELS")
    print("="*80)
    
    # Load data
    ratings_data, animes_data = load_data_from_mongodb()
    
    # Split data (stratified by user)
    train_data, test_data = split_by_user(ratings_data, test_ratio=0.2)
    
    # ===== USER-BASED CF =====
    print(f"\n{'='*80}")
    print("PHASE 1: USER-BASED COLLABORATIVE FILTERING")
    print(f"{'='*80}")
    
    user_model = UserBasedCF(k_neighbors=50, similarity='cosine')
    user_model.fit(train_data)
    
    user_metrics = evaluate_model(user_model, train_data, test_data, k=10)
    
    # Save model
    models_dir = os.path.join(os.path.dirname(__file__), '../saved_models')
    os.makedirs(models_dir, exist_ok=True)
    user_model.save(os.path.join(models_dir, 'user_based_cf.pkl'))
    
    update_model_registry('user_based_cf', user_metrics, is_active=False)
    
    # ===== ITEM-BASED CF =====
    print(f"\n{'='*80}")
    print("PHASE 2: ITEM-BASED COLLABORATIVE FILTERING")
    print(f"{'='*80}")
    
    item_model = ItemBasedCF(k_similar=30, similarity='adjusted_cosine', min_ratings=100)
    item_model.fit(train_data)
    
    item_metrics = evaluate_model(item_model, train_data, test_data, k=10)
    
    # Save model
    item_model.save(os.path.join(models_dir, 'item_based_cf.pkl'))
    
    update_model_registry('item_based_cf', item_metrics, is_active=False)
    
    # ===== HYBRID MODEL =====
    print(f"\n{'='*80}")
    print("PHASE 3: HYBRID MODEL")
    print(f"{'='*80}")
    
    # Optimize weights
    best_alpha = optimize_hybrid_weights(user_model, item_model, train_data, test_data)
    
    # Create hybrid with optimal weights
    hybrid_model = HybridWeightedCF(
        user_model, item_model,
        user_weight=best_alpha,
        item_weight=1-best_alpha
    )
    
    # Evaluate hybrid
    hybrid_metrics = evaluate_model(hybrid_model, train_data, test_data, k=10)
    
    # Save hybrid config
    hybrid_model.save(os.path.join(models_dir,'hybrid.pkl'))
    
    # Activate hybrid model (best combined model)
    update_model_registry('hybrid', hybrid_metrics, is_active=False)  # Will compare with NCF first
    
    # ===== NEURAL CF MODEL =====
    print(f"\n{'='*80}")
    print("PHASE 4: NEURAL COLLABORATIVE FILTERING")
    print(f"{'='*80}")
    
    ncf_model, ncf_metrics = train_neural_cf(train_data, test_data)
    
    # Save NCF model
    ncf_model.save(os.path.join(models_dir, 'neural_cf.pt'))
    
    # Activate NCF if it's better than Hybrid
    is_active = ncf_metrics.get('rmse', float('inf')) < hybrid_metrics.get('rmse', float('inf'))
    update_model_registry('neural_cf', ncf_metrics, is_active=is_active)
    
    if is_active:
        print("\n[OK] NCF is the best model! Activated.")
    else:
        print("\n[OK] Hybrid remains the best model.")
        update_model_registry('hybrid', hybrid_metrics, is_active=True)
    
    # ===== COMPARISON =====
    print(f"\n{'='*80}")
    print("FINAL COMPARISON")
    print(f"{'='*80}")
    
    compare_models({
        'User-Based CF': user_metrics,
        'Item-Based CF': item_metrics,
        'Hybrid': hybrid_metrics,
        'Neural CF': ncf_metrics
    })
    
    print("\nTraining complete! Models saved to ml/saved_models/")
    

if __name__ == "__main__":
    main()
