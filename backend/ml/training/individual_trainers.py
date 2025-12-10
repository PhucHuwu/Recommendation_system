"""
Individual Model Trainers

Each function trains a specific model independently with fresh data from MongoDB.
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.models.user_based import UserBasedCF
from ml.models.item_based import ItemBasedCF
from ml.models.hybrid import HybridWeightedCF
from ml.models.neural_cf import NeuralCF
from ml.training.evaluate import evaluate_model
from ml.training.train import (
    load_data_from_mongodb, 
    split_by_user,
    update_model_registry,
    optimize_hybrid_weights
)
from typing import Dict, Tuple, Optional
import torch


def get_models_dir() -> str:
    """Get models directory path"""
    return os.path.join(os.path.dirname(__file__), '../../ml/saved_models')


def train_user_based_cf(progress_callback=None) -> Tuple[UserBasedCF, Dict[str, float]]:
    """
    Train User-Based Collaborative Filtering model
    
    Args:
        progress_callback: Function(progress: int, step: str) to report progress
        
    Returns:
        (model, metrics)
    """
    if progress_callback:
        progress_callback(5, "Loading data from MongoDB...")
    
    # Load data
    ratings_data, animes_data = load_data_from_mongodb()
    
    if progress_callback:
        progress_callback(15, "Splitting train/test data...")
    
    # Split data
    train_data, test_data = split_by_user(ratings_data, test_ratio=0.2)
    
    if progress_callback:
        progress_callback(25, "Training User-Based CF model...")
    
    # Train model
    model = UserBasedCF(k_neighbors=50, similarity='cosine')
    model.fit(train_data)
    
    if progress_callback:
        progress_callback(60, "Evaluating model...")
    
    # Evaluate
    metrics = evaluate_model(model, train_data, test_data, k=10)
    
    if progress_callback:
        progress_callback(80, "Saving model...")
    
    # Save model
    models_dir = get_models_dir()
    os.makedirs(models_dir, exist_ok=True)
    model.save(os.path.join(models_dir, 'user_based_cf.pkl'))
    
    if progress_callback:
        progress_callback(90, "Updating model registry...")
    
    # Update registry
    update_model_registry('user_based_cf', metrics, is_active=False)
    
    return model, metrics


def train_item_based_cf(progress_callback=None) -> Tuple[ItemBasedCF, Dict[str, float]]:
    """
    Train Item-Based Collaborative Filtering model
    
    Args:
        progress_callback: Function(progress: int, step: str) to report progress
        
    Returns:
        (model, metrics)
    """
    if progress_callback:
        progress_callback(5, "Loading data from MongoDB...")
    
    ratings_data, animes_data = load_data_from_mongodb()
    
    if progress_callback:
        progress_callback(15, "Splitting train/test data...")
    
    train_data, test_data = split_by_user(ratings_data, test_ratio=0.2)
    
    if progress_callback:
        progress_callback(25, "Training Item-Based CF model...")
    
    model = ItemBasedCF(k_similar=30, similarity='adjusted_cosine', min_ratings=100)
    model.fit(train_data)
    
    if progress_callback:
        progress_callback(60, "Evaluating model...")
    
    metrics = evaluate_model(model, train_data, test_data, k=10)
    
    if progress_callback:
        progress_callback(80, "Saving model...")
    
    models_dir = get_models_dir()
    os.makedirs(models_dir, exist_ok=True)
    model.save(os.path.join(models_dir, 'item_based_cf.pkl'))
    
    if progress_callback:
        progress_callback(90, "Updating model registry...")
    
    update_model_registry('item_based_cf', metrics, is_active=False)
    
    return model, metrics


def train_hybrid(progress_callback=None) -> Tuple[HybridWeightedCF, Dict[str, float]]:
    """
    Train Hybrid model (requires User-Based and Item-Based to be trained first)
    
    Args:
        progress_callback: Function(progress: int, step: str) to report progress
        
    Returns:
        (model, metrics)
    """
    if progress_callback:
        progress_callback(5, "Loading data from Mongolia...")
    
    ratings_data, animes_data = load_data_from_mongodb()
    
    if progress_callback:
        progress_callback(10, "Splitting train/test data...")
    
    train_data, test_data = split_by_user(ratings_data, test_ratio=0.2)
    
    if progress_callback:
        progress_callback(15, "Training User-Based CF...")
    
    # Train base models
    user_model = UserBasedCF(k_neighbors=50, similarity='cosine')
    user_model.fit(train_data)
    
    if progress_callback:
        progress_callback(35, "Training Item-Based CF...")
    
    item_model = ItemBasedCF(k_similar=30, similarity='adjusted_cosine', min_ratings=100)
    item_model.fit(train_data)
    
    if progress_callback:
        progress_callback(55, "Optimizing hybrid weights...")
    
    # Optimize weights
    best_alpha = optimize_hybrid_weights(user_model, item_model, train_data, test_data)
    
    # Create hybrid model
    model = HybridWeightedCF(
        user_model, item_model,
        user_weight=best_alpha,
        item_weight=1-best_alpha
    )
    
    if progress_callback:
        progress_callback(70, "Evaluating hybrid model...")
    
    metrics = evaluate_model(model, train_data, test_data, k=10)
    
    if progress_callback:
        progress_callback(85, "Saving models...")
    
    # Save all models
    models_dir = get_models_dir()
    os.makedirs(models_dir, exist_ok=True)
    user_model.save(os.path.join(models_dir, 'user_based_cf.pkl'))
    item_model.save(os.path.join(models_dir, 'item_based_cf.pkl'))
    model.save(os.path.join(models_dir, 'hybrid.pkl'))
    
    if progress_callback:
        progress_callback(95, "Updating model registry...")
    
    # Update registries
    update_model_registry('hybrid', metrics, is_active=False)
    
    return model, metrics


def train_neural_cf(progress_callback=None) -> Tuple[NeuralCF, Dict[str, float]]:
    """
    Train Neural Collaborative Filtering model
    
    Args:
        progress_callback: Function(progress: int, step: str) to report progress
        
    Returns:
        (model, metrics)
    """
    if progress_callback:
        progress_callback(5, "Loading data from MongoDB...")
    
    ratings_data, animes_data = load_data_from_mongodb()
    
    if progress_callback:
        progress_callback(10, "Splitting train/test data...")
    
    train_data, test_data = split_by_user(ratings_data, test_ratio=0.2)
    
    if progress_callback:
        progress_callback(15, "Preparing NCF training data...")
    
    # Create ID mappings
    user_ids = set(r['user_id'] for r in train_data)
    item_ids = set(r['anime_id'] for r in train_data)
    
    user_id_map = {uid: idx for idx, uid in enumerate(sorted(user_ids))}
    item_id_map = {iid: idx for idx, iid in enumerate(sorted(item_ids))}
    
    # Map training data
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
    
    if progress_callback:
        progress_callback(20, "Initializing Neural CF model...")
    
    # Initialize model
    model = NeuralCF(
        num_users=len(user_id_map),
        num_items=len(item_id_map),
        embedding_dim=64,
        mlp_layers=[128, 64, 32],
        dropout=0.2
    )
    
    if progress_callback:
        progress_callback(25, "Training Neural CF (this may take 30-60 minutes)...")
    
    # Train
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
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
    
    if progress_callback:
        progress_callback(75, "Evaluating Neural CF...")
    
    # Evaluate
    metrics = evaluate_model(model, train_data, test_data, k=10)
    
    if progress_callback:
        progress_callback(90, "Saving model...")
    
    # Save model
    models_dir = get_models_dir()
    os.makedirs(models_dir, exist_ok=True)
    model.save(os.path.join(models_dir, 'neural_cf.pt'))
    
    if progress_callback:
        progress_callback(95, "Updating model registry...")
    
    # Update registry
    update_model_registry('neural_cf', metrics, is_active=False)
    
    return model, metrics


# Mapping of model names to training functions
TRAINERS = {
    'user_based_cf': train_user_based_cf,
    'item_based_cf': train_item_based_cf,
    'hybrid': train_hybrid,
    'neural_cf': train_neural_cf
}


def get_trainer(model_name: str):
    """Get training function for a model"""
    if model_name not in TRAINERS:
        raise ValueError(f"Unknown model: {model_name}. Valid models: {list(TRAINERS.keys())}")
    return TRAINERS[model_name]
