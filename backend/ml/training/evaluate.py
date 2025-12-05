"""
Evaluation Metrics for Recommendation Models

Calculate RMSE, MAE, Precision@K, Recall@K
"""

import numpy as np
from typing import List, Tuple, Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Root Mean Square Error
    
    Args:
        actual: Actual ratings
        predicted: Predicted ratings
        
    Returns:
        RMSE value
    """
    return np.sqrt(np.mean((actual - predicted) ** 2))


def mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error
    
    Args:
        actual: Actual ratings
        predicted: Predicted ratings
        
    Returns:
        MAE value
    """
    return np.mean(np.abs(actual - predicted))


def precision_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    """
    Calculate Precision@K
    
    Args:
        recommended: List of recommended item IDs (top K)
        relevant: List of relevant item IDs (ground truth)
        k: Number of recommendations
        
    Returns:
        Precision@K value (0-1)
    """
    if k == 0:
        return 0.0
    
    recommended_k = recommended[:k]
    relevant_set = set(relevant)
    
    hits = len([item for item in recommended_k if item in relevant_set])
    
    return hits / k


def recall_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    """
    Calculate Recall@K
    
    Args:
        recommended: List of recommended item IDs (top K)
        relevant: List of relevant item IDs (ground truth)
        k: Number of recommendations
        
    Returns:
        Recall@K value (0-1)
    """
    if len(relevant) == 0:
        return 0.0
    
    recommended_k = recommended[:k]
    relevant_set = set(relevant)
    
    hits = len([item for item in recommended_k if item in relevant_set])
    
    return hits / len(relevant)


def evaluate_model(model, test_data: List[dict], train_data: List[dict] = None, k: int = 10) -> Dict[str, float]:
    """
    Evaluate a recommendation model with RMSE, MAE, Precision@K, Recall@K
    
    Args:
        model: Trained model with predict() and recommend() methods
        test_data: Test ratings data
        train_data: Train ratings data (to exclude from recommendations)
        k: K for Precision@K and Recall@K
        
    Returns:
        Dictionary of metrics
    """
    print(f"Evaluating model on {len(test_data):,} test samples...")
    
    # ===== RMSE & MAE =====
    # Sample test data for faster evaluation (10K samples instead of full 1.5M)
    import random
    sampled_test_data = random.sample(test_data, min(10000, len(test_data)))
    print(f"  Sampled {len(sampled_test_data):,} ratings for RMSE/MAE evaluation")
    
    actual_ratings = []
    predicted_ratings = []
    
    for i, rating in enumerate(sampled_test_data):
        if i % 1000 == 0:
            print(f"    Progress: {i}/{len(sampled_test_data)}", end='\r')
        
        actual = rating['rating']
        predicted = model.predict(rating['user_id'], rating['anime_id'])
        
        if predicted > 0:  # Only evaluate if prediction was made
            actual_ratings.append(actual)
            predicted_ratings.append(predicted)
    
    actual_ratings = np.array(actual_ratings)
    predicted_ratings = np.array(predicted_ratings)
    
    if len(actual_ratings) == 0:
        print("  Warning: No predictions made")
        return {
            'rmse': 0.0,
            'mae': 0.0,
            'precision_at_k': 0.0,
            'recall_at_k': 0.0,
            'coverage': 0.0
        }
    
    rmse_value = rmse(actual_ratings, predicted_ratings)
    mae_value = mae(actual_ratings, predicted_ratings)
    coverage = len(actual_ratings) / len(sampled_test_data)  # Coverage on sampled data
    
    print(f"  RMSE: {rmse_value:.4f}")
    print(f"  MAE: {mae_value:.4f}")
    print(f"  Coverage: {coverage:.2%} (on sampled data)")
    
    # ===== Precision@K & Recall@K =====
    precision_k = 0.0
    recall_k = 0.0
    
    if hasattr(model, 'recommend'):
        # Build user's train items set (to exclude from recommendations)
        user_train_items = {}
        if train_data:
            for r in train_data:
                uid = r['user_id']
                if uid not in user_train_items:
                    user_train_items[uid] = set()
                user_train_items[uid].add(r['anime_id'])
        
        # Group test data by user - relevant items are those with high ratings
        user_test_relevant = {}
        for rating in test_data:
            user_id = rating['user_id']
            if rating['rating'] >= 7:  # Consider rating >= 7 as relevant
                if user_id not in user_test_relevant:
                    user_test_relevant[user_id] = []
                user_test_relevant[user_id].append(rating['anime_id'])
        
        # Calculate Precision@K and Recall@K for each user
        precisions = []
        recalls = []
        evaluated_users = 0
        
        # Sample users who have relevant items in test set
        users_with_relevant = [u for u, items in user_test_relevant.items() if len(items) > 0]
        
        # CRITICAL: Only evaluate users that are also in train_data
        # Otherwise model.recommend() will fail for unseen users
        if train_data:
            train_users = set(r['user_id'] for r in train_data)
            users_with_relevant = [u for u in users_with_relevant if u in train_users]
        
        sample_users = users_with_relevant[:50]  # Sample up to 50 users (reduced from 200)
        print(f"  Evaluating Precision@K and Recall@K on {len(sample_users)} users (from train set)...")
        
        for idx, user_id in enumerate(sample_users):
            if idx % 10 == 0:
                print(f"    Evaluating user {idx}/{len(sample_users)}", end='\r')
            
            relevant_animes = user_test_relevant[user_id]
            
            try:
                # Get recommendations, excluding items user has in train set
                recommendations = model.recommend(user_id, n=k + 50, exclude_rated=False)
                
                # Filter out items that are in user's train set
                train_items = user_train_items.get(user_id, set())
                filtered_recs = [(aid, score) for aid, score in recommendations if aid not in train_items]
                recommended_ids = [rec[0] for rec in filtered_recs[:k]]
                
                if recommended_ids and relevant_animes:
                    prec = precision_at_k(recommended_ids, relevant_animes, k)
                    rec = recall_at_k(recommended_ids, relevant_animes, k)
                    precisions.append(prec)
                    recalls.append(rec)
                    evaluated_users += 1
            except Exception as e:
                if idx < 5:  # Only print first 5 errors
                    print(f"\n    Error for user {user_id}: {e}")
                pass
        
        if precisions:
            precision_k = np.mean(precisions)
            recall_k = np.mean(recalls)
            print(f"  Precision@{k}: {precision_k:.4f} (evaluated on {evaluated_users} users)")
            print(f"  Recall@{k}: {recall_k:.4f}")
        else:
            print(f"  Precision@{k}: N/A (no users with relevant items)")
            print(f"  Recall@{k}: N/A")
    
    return {
        'rmse': float(rmse_value),
        'mae': float(mae_value),
        'precision_at_k': float(precision_k),
        'recall_at_k': float(recall_k),
        'coverage': float(coverage)
    }
