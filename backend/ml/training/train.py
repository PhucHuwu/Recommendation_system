"""
Training Pipeline for ML Models

Train all recommendation models and save them.
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from ml.models.user_based import UserBasedCF
from ml.models.item_based import ItemBasedCF
from ml.models.content_based import ContentBasedCF
from ml.training.evaluate import evaluate_model

# Load environment
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'anime_recommendation')

# Paths
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'saved_models')
os.makedirs(MODELS_DIR, exist_ok=True)


def load_data_from_mongodb():
    """Load training data from MongoDB"""
    print("=" * 60)
    print("Loading data from MongoDB...")
    print("=" * 60)
    
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    
    # Load ratings
    print("Loading ratings...")
    ratings_cursor = db.ratings.find({}, {'_id': 0, 'user_id': 1, 'anime_id': 1, 'rating': 1})
    ratings_data = list(ratings_cursor)
    print(f"  Loaded {len(ratings_data):,} ratings")
    
    # Load animes
    print("Loading animes...")
    animes_cursor = db.animes.find({}, {'_id': 0, 'mal_id': 1, 'name': 1, 'genres': 1, 'synopsis': 1})
    animes_data = list(animes_cursor)
    print(f"  Loaded {len(animes_data):,} animes")
    
    client.close()
    
    return ratings_data, animes_data


def split_by_user(ratings_data, test_ratio=0.2, min_ratings=5):
    """
    Stratified split by user - chia ratings của MỖI user theo tỷ lệ 80/20
    Đảm bảo mọi user trong test set đều có data trong train set (tránh cold start)
    
    Args:
        ratings_data: List of rating dicts
        test_ratio: Tỷ lệ test (default 0.2)
        min_ratings: Số ratings tối thiểu để user được split (default 5)
    
    Returns:
        train_data, test_data
    """
    import random
    random.seed(42)
    
    # Group ratings by user
    user_ratings = {}
    for r in ratings_data:
        user_id = r['user_id']
        if user_id not in user_ratings:
            user_ratings[user_id] = []
        user_ratings[user_id].append(r)
    
    train_data = []
    test_data = []
    
    for user_id, ratings in user_ratings.items():
        n = len(ratings)
        
        if n >= min_ratings:
            # Shuffle ratings của user này
            random.shuffle(ratings)
            
            # Split 80/20
            split_idx = int(n * (1 - test_ratio))
            train_data.extend(ratings[:split_idx])
            test_data.extend(ratings[split_idx:])
        else:
            # User có ít ratings -> toàn bộ vào train
            train_data.extend(ratings)
    
    print(f"  Stratified split by USER (each user's ratings 80/20):")
    print(f"    Users with >= {min_ratings} ratings: {sum(1 for u, r in user_ratings.items() if len(r) >= min_ratings):,}")
    print(f"    Train ratings: {len(train_data):,}")
    print(f"    Test ratings: {len(test_data):,}")
    print(f"    Test users in train: {len(set(r['user_id'] for r in test_data) & set(r['user_id'] for r in train_data)):,}")
    
    return train_data, test_data


def split_by_item(ratings_data, test_ratio=0.2, min_ratings=5):
    """
    Stratified split by item - chia ratings của MỖI anime theo tỷ lệ 80/20
    Đảm bảo mọi anime trong test set đều có data trong train set
    
    Args:
        ratings_data: List of rating dicts
        test_ratio: Tỷ lệ test (default 0.2)
        min_ratings: Số ratings tối thiểu để anime được split (default 5)
    
    Returns:
        train_data, test_data
    """
    import random
    random.seed(42)
    
    # Group ratings by anime
    anime_ratings = {}
    for r in ratings_data:
        anime_id = r['anime_id']
        if anime_id not in anime_ratings:
            anime_ratings[anime_id] = []
        anime_ratings[anime_id].append(r)
    
    train_data = []
    test_data = []
    
    for anime_id, ratings in anime_ratings.items():
        n = len(ratings)
        
        if n >= min_ratings:
            # Shuffle ratings của anime này
            random.shuffle(ratings)
            
            # Split 80/20
            split_idx = int(n * (1 - test_ratio))
            train_data.extend(ratings[:split_idx])
            test_data.extend(ratings[split_idx:])
        else:
            # Anime có ít ratings -> toàn bộ vào train
            train_data.extend(ratings)
    
    print(f"  Stratified split by ANIME (each anime's ratings 80/20):")
    print(f"    Animes with >= {min_ratings} ratings: {sum(1 for a, r in anime_ratings.items() if len(r) >= min_ratings):,}")
    print(f"    Train ratings: {len(train_data):,}")
    print(f"    Test ratings: {len(test_data):,}")
    print(f"    Test animes in train: {len(set(r['anime_id'] for r in test_data) & set(r['anime_id'] for r in train_data)):,}")
    
    return train_data, test_data


def split_by_genre(animes_data, test_ratio=0.2):
    """
    Split animes by genres for Content-Based CF
    80% genres for training, 20% genres for testing
    This prevents domain shift in content-based models
    """
    import random
    random.seed(42)
    
    # Get all unique genres
    all_genres = set()
    for anime in animes_data:
        genres = anime.get('genres', [])
        if isinstance(genres, list):
            all_genres.update(genres)
        elif isinstance(genres, str):
            all_genres.update([g.strip() for g in genres.split(',')])
    
    unique_genres = list(all_genres)
    random.shuffle(unique_genres)
    
    split_idx = int(len(unique_genres) * (1 - test_ratio))
    train_genres = set(unique_genres[:split_idx])
    test_genres = set(unique_genres[split_idx:])
    
    # Assign anime to train or test based on primary genre
    train_data = []
    test_data = []
    
    for anime in animes_data:
        genres = anime.get('genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        
        # Check if primary genre is in test set
        if genres:
            primary_genre = genres[0]
            if primary_genre in test_genres:
                test_data.append(anime)
            else:
                train_data.append(anime)
        else:
            train_data.append(anime)  # No genre = train
    
    print(f"  Split by GENRE:")
    print(f"    Train genres: {len(train_genres):,}, Train animes: {len(train_data):,}")
    print(f"    Test genres: {len(test_genres):,}, Test animes: {len(test_data):,}")
    
    return train_data, test_data, train_genres, test_genres


def train_user_based_cf(train_data, test_data):
    """Train User-Based Collaborative Filtering"""
    print("\n" + "=" * 60)
    print("TRAINING: User-Based CF")
    print("=" * 60)
    
    model = UserBasedCF(k_neighbors=50)
    model.fit(train_data)
    
    # Evaluate model with train_data for Precision@K, Recall@K
    print("\nEvaluating User-Based CF...")
    metrics = evaluate_model(model, test_data, train_data=train_data, k=10)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'user_based_cf.pkl')
    model.save(model_path)
    
    return model, metrics


def train_item_based_cf(train_data, test_data):
    """Train Item-Based Collaborative Filtering"""
    print("\n" + "=" * 60)
    print("TRAINING: Item-Based CF")
    print("=" * 60)
    
    model = ItemBasedCF(k_similar=30)
    model.fit(train_data)
    
    # Evaluate model with train_data for Precision@K, Recall@K
    print("\nEvaluating Item-Based CF...")
    metrics = evaluate_model(model, test_data, train_data=train_data, k=10)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'item_based_cf.pkl')
    model.save(model_path)
    
    return model, metrics


def train_content_based(animes_data, train_ratings, test_ratings):
    """Train Content-Based Filtering"""
    print("\n" + "=" * 60)
    print("TRAINING: Content-Based")
    print("=" * 60)
    
    model = ContentBasedCF(use_synopsis=True, use_genres=True)
    model.fit(animes_data)  # Fit on all animes to build similarity matrix
    
    # Evaluate content-based model using user ratings
    print("\nEvaluating Content-Based...")
    metrics = evaluate_content_based(model, train_ratings, test_ratings, k=10)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'content_based.pkl')
    model.save(model_path)
    
    return model, metrics


def evaluate_content_based(model, train_ratings, test_ratings, k=10):
    """
    Evaluate Content-Based model using user ratings
    
    For each user:
    1. Get their liked animes from train set (rating >= 7)
    2. Recommend similar animes based on content
    3. Check if recommendations match their test set likes
    """
    import numpy as np
    import random
    
    print(f"  Evaluating on user ratings...")
    
    # Build user train/test item mappings
    user_train_items = {}
    user_train_liked = {}  # Items with rating >= 7
    for r in train_ratings:
        uid = r['user_id']
        if uid not in user_train_items:
            user_train_items[uid] = set()
            user_train_liked[uid] = []
        user_train_items[uid].add(r['anime_id'])
        if r['rating'] >= 7:
            user_train_liked[uid].append(r['anime_id'])
    
    user_test_relevant = {}  # Test items with rating >= 7
    for r in test_ratings:
        uid = r['user_id']
        if r['rating'] >= 7:
            if uid not in user_test_relevant:
                user_test_relevant[uid] = []
            user_test_relevant[uid].append(r['anime_id'])
    
    # Sample users who have both train likes and test relevant items
    valid_users = [u for u in user_test_relevant if u in user_train_liked and len(user_train_liked[u]) > 0]
    sample_users = random.sample(valid_users, min(200, len(valid_users)))
    
    precisions = []
    recalls = []
    
    for user_id in sample_users:
        liked_animes = user_train_liked[user_id]
        train_items = user_train_items[user_id]
        relevant_animes = user_test_relevant[user_id]
        
        try:
            # Get content-based recommendations based on user's liked animes
            all_recommendations = {}
            for liked_id in liked_animes[:5]:  # Use top 5 liked animes
                if liked_id in model.anime_id_map:
                    similar = model.get_similar_animes(liked_id, n=k * 3)
                    for anime_id, score in similar:
                        if anime_id not in train_items:  # Exclude already seen
                            if anime_id not in all_recommendations:
                                all_recommendations[anime_id] = 0
                            all_recommendations[anime_id] += score
            
            # Sort and get top K
            sorted_recs = sorted(all_recommendations.items(), key=lambda x: x[1], reverse=True)
            recommended_ids = [r[0] for r in sorted_recs[:k]]
            
            if recommended_ids and relevant_animes:
                # Calculate precision and recall
                hits = len(set(recommended_ids) & set(relevant_animes))
                precision = hits / k
                recall = hits / len(relevant_animes) if relevant_animes else 0
                
                precisions.append(precision)
                recalls.append(recall)
        except Exception as e:
            continue
    
    if precisions:
        precision_k = np.mean(precisions)
        recall_k = np.mean(recalls)
        print(f"  Precision@{k}: {precision_k:.4f} (evaluated on {len(precisions)} users)")
        print(f"  Recall@{k}: {recall_k:.4f}")
    else:
        precision_k = 0.0
        recall_k = 0.0
        print(f"  No valid users for evaluation")
    
    return {
        'rmse': None,  # Content-based doesn't predict ratings directly
        'mae': None,
        'precision_at_k': float(precision_k),
        'recall_at_k': float(recall_k),
        'coverage': len(precisions) / max(1, len(sample_users)),
        'note': 'Content-based evaluated using user preference similarity'
    }


def update_model_registry(model_name, metrics=None):
    """Update model registry in MongoDB"""
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    
    model_path = os.path.join(MODELS_DIR, f'{model_name}.pkl')
    
    db.models.update_one(
        {'name': model_name},
        {
            '$set': {
                'name': model_name,
                'trained_at': datetime.utcnow(),
                'file_path': model_path,
                'status': 'trained',
                'metrics': metrics or {}
            },
            '$setOnInsert': {
                'created_at': datetime.utcnow(),
                'is_active': False
            }
        },
        upsert=True
    )
    
    client.close()
    print(f"  Updated model registry for {model_name}")


def main():
    """Main training pipeline"""
    print("\n" + "=" * 60)
    print("RECOMMENDATION SYSTEM - TRAINING PIPELINE")
    print("=" * 60)
    
    try:
        # Load data
        ratings_data, animes_data = load_data_from_mongodb()
        
        # ===== COMMON SPLIT: Stratified by User =====
        # All models use the same train/test split for fair comparison
        print("\n" + "-" * 40)
        print("Splitting data (Stratified by User - 80/20)...")
        train_data, test_data = split_by_user(ratings_data, test_ratio=0.2)
        
        # ===== User-Based CF =====
        user_based_model, user_based_metrics = train_user_based_cf(train_data, test_data)
        update_model_registry('user_based_cf', metrics=user_based_metrics)
        
        # ===== Item-Based CF =====
        # Use same split as User-Based for fair comparison
        item_based_model, item_based_metrics = train_item_based_cf(train_data, test_data)
        update_model_registry('item_based_cf', metrics=item_based_metrics)
        
        # ===== Content-Based =====
        # Train on all animes, evaluate with user ratings
        content_based_model, content_based_metrics = train_content_based(
            animes_data, train_data, test_data
        )
        update_model_registry('content_based', metrics=content_based_metrics)
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE!")
        print("=" * 60)
        print(f"\nModels saved to: {MODELS_DIR}")
        print("\nTrained models:")
        print("  - user_based_cf.pkl")
        print("  - item_based_cf.pkl")
        print("  - content_based.pkl")
        
        print("\n" + "=" * 60)
        print("METRICS SUMMARY (All models use same stratified user split)")
        print("=" * 60)
        print("\nUser-Based CF:")
        for k, v in user_based_metrics.items():
            if v is None:
                print(f"  {k}: N/A")
            elif isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")
        print("\nItem-Based CF:")
        for k, v in item_based_metrics.items():
            if v is None:
                print(f"  {k}: N/A")
            elif isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")
        print("\nContent-Based:")
        for k, v in content_based_metrics.items():
            if v is None:
                print(f"  {k}: N/A")
            elif isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")
        
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()