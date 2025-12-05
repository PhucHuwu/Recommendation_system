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


def evaluate_model(model, test_data: List[dict], k: int = 10) -> Dict[str, float]:
    """
    Evaluate a recommendation model
    
    Args:
        model: Trained model with predict() method
        test_data: Test ratings data
        k: K for Precision@K and Recall@K
        
    Returns:
        Dictionary of metrics
    """
    print(f"Evaluating model on {len(test_data):,} test samples...")
    
    actual_ratings = []
    predicted_ratings = []
    
    # Calculate RMSE and MAE
    for rating in test_data:
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
    coverage = len(actual_ratings) / len(test_data)
    
    print(f"  RMSE: {rmse_value:.4f}")
    print(f"  MAE: {mae_value:.4f}")
    print(f"  Coverage: {coverage:.2%}")
    
    # Calculate Precision@K and Recall@K (if model has recommend method)
    precision_k = 0.0
    recall_k = 0.0
    
    if hasattr(model, 'recommend'):
        # Group test data by user
        user_test_animes = {}
        for rating in test_data:
            user_id = rating['user_id']
            if rating['rating'] >= 7:  # Consider rating >= 7 as relevant
                if user_id not in user_test_animes:
                    user_test_animes[user_id] = []
                user_test_animes[user_id].append(rating['anime_id'])
        
        # Calculate Precision@K and Recall@K for each user
        precisions = []
        recalls = []
        
        for user_id, relevant_animes in list(user_test_animes.items())[:100]:  # Sample 100 users
            try:
                recommendations = model.recommend(user_id, n=k, exclude_rated=True)
                recommended_ids = [rec[0] for rec in recommendations]
                
                if recommended_ids:
                    prec = precision_at_k(recommended_ids, relevant_animes, k)
                    rec = recall_at_k(recommended_ids, relevant_animes, k)
                    precisions.append(prec)
                    recalls.append(rec)
            except:
                pass
        
        if precisions:
            precision_k = np.mean(precisions)
            recall_k = np.mean(recalls)
            print(f"  Precision@{k}: {precision_k:.4f}")
            print(f"  Recall@{k}: {recall_k:.4f}")
    
    return {
        'rmse': float(rmse_value),
        'mae': float(mae_value),
        'precision_at_k': float(precision_k),
        'recall_at_k': float(recall_k),
        'coverage': float(coverage)
    }
