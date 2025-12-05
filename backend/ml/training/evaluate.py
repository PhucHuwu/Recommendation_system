"""
Comprehensive Evaluation Framework for Recommendation Models

Implements multiple metrics:
- RMSE & MAE: Rating prediction accuracy
- Precision@K & Recall@K: Recommendation quality
- Coverage: Item catalog coverage
- Diversity: Recommendation diversity
- Novelty: How non-obvious recommendations are
"""

import numpy as np
from typing import List, Dict, Tuple, Any
import random
from collections import defaultdict


def evaluate_model(model, train_data: List[dict], test_data: List[dict], k: int = 10) -> Dict[str, float]:
    """
    Comprehensive evaluation of recommendation model
    
    Args:
        model: Trained recommendation model (User-Based, Item-Based, or Hybrid)
        train_data: Training ratings data
        test_data: Testing ratings data
        k: Parameter for Precision@K and Recall@K
        
    Returns:
        Dictionary with all metrics
    """
    print(f"\n{'='*60}")
    print(f"EVALUATING MODEL")
    print(f"{'='*60}")
    
    metrics = {}
    
    # 1. RMSE & MAE - Rating Prediction Accuracy
    print("\n1. Computing RMSE & MAE...")
    rmse, mae, coverage_pred = _compute_prediction_metrics(model, test_data, sample_size=10000)
    metrics['rmse'] = rmse
    metrics['mae'] = mae
    metrics['prediction_coverage'] = coverage_pred
    
    # 2. Precision@K & Recall@K - Recommendation Quality
    print(f"\n2. Computing Precision@{k} & Recall@{k}...")
    precision, recall, evaluated_users = _compute_ranking_metrics(
        model, train_data, test_data, k=k, sample_users=50
    )
    metrics['precision_at_k'] = precision
    metrics['recall_at_k'] = recall
    metrics['evaluated_users'] = evaluated_users
    
    # 3. Coverage - Item Catalog Coverage
    print("\n3. Computing coverage...")
    coverage = _compute_coverage(model, train_data, n_recommendations=k, sample_users=100)
    metrics['coverage'] = coverage
    
    # 4. Diversity - Recommendation Diversity
    print("\n4. Computing diversity...")
    diversity = _compute_diversity(model, train_data, n_recommendations=k, sample_users=50)
    metrics['diversity'] = diversity
    
    # 5. Novelty - Recommendation Novelty
    print("\n5. Computing novelty...")
    novelty = _compute_novelty(model, train_data, n_recommendations=k, sample_users=50)
    metrics['novelty'] = novelty
    
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}")
    
    return metrics


def _compute_prediction_metrics(model, test_data: List[dict], sample_size: int = 10000) -> Tuple[float, float, float]:
    """
    Compute RMSE and MAE for rating prediction
    
    Returns:
        (rmse, mae, coverage) where coverage is % of predictions that could be made
    """
    # Sample test data for efficiency
    if len(test_data) > sample_size:
        sampled_test = random.sample(test_data, sample_size)
    else:
        sampled_test = test_data
    
    errors = []
    abs_errors = []
    successful_predictions = 0
    
    for i, rating in enumerate(sampled_test):
        if i % 1000 == 0:
            print(f"  Progress: {i}/{len(sampled_test)}", end='\r')
        
        pred = model.predict(rating['user_id'], rating['anime_id'])
        
        if pred > 0:  # Model could make prediction
            error = rating['rating'] - pred
            errors.append(error ** 2)
            abs_errors.append(abs(error))
            successful_predictions += 1
    
    if len(errors) == 0:
        return 0.0, 0.0, 0.0
    
    rmse = np.sqrt(np.mean(errors))
    mae = np.mean(abs_errors)
    coverage = successful_predictions / len(sampled_test)
    
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE: {mae:.4f}")
    print(f"  Coverage: {coverage:.2%} ({successful_predictions}/{len(sampled_test)})")
    
    return rmse, mae, coverage


def _compute_ranking_metrics(model, train_data: List[dict], test_data: List[dict], 
                             k: int = 10, sample_users: int = 50) -> Tuple[float, float, int]:
    """
    Compute Precision@K and Recall@K
    
    Strategy:
    - For each user in test, find items they rated highly (>=7)
    - Get top K recommendations
    - Compute precision and recall
    
    Returns:
        (precision@k, recall@k, number of evaluated users)
    """
    # Build user test items mapping (relevant items)
    user_test_relevant = defaultdict(list)
    for rating in test_data:
        if rating['rating'] >= 7:  # Consider 7+ as relevant
            user_test_relevant[rating['user_id']].append(rating['anime_id'])
    
    # Build user train items (to exclude from recommendations)
    user_train_items = defaultdict(set)
    for rating in train_data:
        user_train_items[rating['user_id']].add(rating['anime_id'])
    
    # Filter to users who:
    # 1. Have relevant items in test
    # 2. Also exist in train (can get recommendations)
    valid_users = [u for u in user_test_relevant.keys() 
                   if len(user_test_relevant[u]) > 0 and u in user_train_items]
    
    if len(valid_users) == 0:
        print("  No valid users for evaluation")
        return 0.0, 0.0, 0
    
    # Sample users for efficiency
    sample_users = min(sample_users, len(valid_users))
    sampled_users = random.sample(valid_users, sample_users)
    
    precisions = []
    recalls = []
    evaluated = 0
    
    for i, user_id in enumerate(sampled_users):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(sampled_users)}", end='\r')
        
        relevant_items = set(user_test_relevant[user_id])
        
        try:
            # Get recommendations (exclude train items)
            recommendations = model.recommend(user_id, n=k, exclude_rated=True)
            recommended_ids = [anime_id for anime_id, _ in recommendations]
            
            if len(recommended_ids) > 0 and len(relevant_items) > 0:
                # Precision: relevant in recommendations / k
                hits = len(set(recommended_ids) & relevant_items)
                precision = hits / k
                recall = hits / len(relevant_items)
                
                precisions.append(precision)
                recalls.append(recall)
                evaluated += 1
        except Exception as e:
            print(f"\n  ⚠️ Error for user {user_id}: {type(e).__name__}: {str(e)}")
            continue
    
    if len(precisions) == 0:
        return 0.0, 0.0, 0
    
    avg_precision = np.mean(precisions)
    avg_recall = np.mean(recalls)
    
    print(f"  Precision@{k}: {avg_precision:.4f}")
    print(f"  Recall@{k}: {avg_recall:.4f}")
    print(f"  Evaluated users: {evaluated}")
    
    return avg_precision, avg_recall, evaluated


def _compute_coverage(model, train_data: List[dict], n_recommendations: int = 10, 
                     sample_users: int = 100) -> float:
    """
    Compute catalog coverage: % of items that appear in recommendations
    
    Returns:
        Coverage ratio (0-1)
    """
    # Get all unique items in catalog
    all_items = set([r['anime_id'] for r in train_data])
    
    # Get all unique users
    all_users = list(set([r['user_id'] for r in train_data]))
    
    # Sample users
    sample_users = min(sample_users, len(all_users))
    sampled_users = random.sample(all_users, sample_users)
    
    # Collect all recommended items
    recommended_items = set()
    
    for user_id in sampled_users:
        try:
            recs = model.recommend(user_id, n=n_recommendations)
            recommended_items.update([anime_id for anime_id, _ in recs])
        except:
            continue
    
    coverage = len(recommended_items) / len(all_items) if len(all_items) > 0 else 0
    
    print(f"  Coverage: {coverage:.2%} ({len(recommended_items)}/{len(all_items)} items)")
    
    return coverage


def _compute_diversity(model, train_data: List[dict], n_recommendations: int = 10,
                      sample_users: int = 50) -> float:
    """
    Compute diversity of recommendations using intra-list diversity
    
    Diversity = average pairwise dissimilarity within recommendation lists
    Higher is more diverse
    
    Returns:
        Average diversity score (0-1)
    """
    all_users = list(set([r['user_id'] for r in train_data]))
    sample_users = min(sample_users, len(all_users))
    sampled_users = random.sample(all_users, sample_users)
    
    diversities = []
    
    for user_id in sampled_users:
        try:
            recs = model.recommend(user_id, n=n_recommendations)
            rec_ids = [anime_id for anime_id, _ in recs]
            
            if len(rec_ids) < 2:
                continue
            
            # Compute pairwise diversity (1 - similarity)
            # For simplicity, consider items as diverse if they're different
            # In practice, could use item features/genres for similarity
            total_pairs = 0
            diverse_pairs = 0
            
            for i in range(len(rec_ids)):
                for j in range(i+1, len(rec_ids)):
                    total_pairs += 1
                    if rec_ids[i] != rec_ids[j]:  # Different items = diverse
                        diverse_pairs += 1
            
            if total_pairs > 0:
                diversity = diverse_pairs / total_pairs
                diversities.append(diversity)
        except:
            continue
    
    avg_diversity = np.mean(diversities) if len(diversities) > 0 else 0
    
    print(f"  Diversity: {avg_diversity:.4f}")
    
    return avg_diversity


def _compute_novelty(model, train_data: List[dict], n_recommendations: int = 10,
                    sample_users: int = 50) -> float:
    """
    Compute novelty of recommendations
    
    Novelty = -log2(popularity of recommended items)
    Higher novelty = recommending less popular items
    
    Returns:
        Average novelty score
    """
    # Compute item popularity
    item_popularity = defaultdict(int)
    total_ratings = len(train_data)
    
    for rating in train_data:
        item_popularity[rating['anime_id']] += 1
    
    # Convert to probabilities
    item_prob = {item_id: count / total_ratings 
                 for item_id, count in item_popularity.items()}
    
    # Sample users and compute novelty
    all_users = list(set([r['user_id'] for r in train_data]))
    sample_users = min(sample_users, len(all_users))
    sampled_users = random.sample(all_users, sample_users)
    
    novelties = []
    
    for user_id in sampled_users:
        try:
            recs = model.recommend(user_id, n=n_recommendations)
            
            for anime_id, _ in recs:
                if anime_id in item_prob:
                    # Novelty = -log2(p)
                    novelty = -np.log2(item_prob[anime_id]) if item_prob[anime_id] > 0 else 0
                    novelties.append(novelty)
        except:
            continue
    
    avg_novelty = np.mean(novelties) if len(novelties) > 0 else 0
    
    print(f"  Novelty: {avg_novelty:.4f}")
    
    return avg_novelty


def compare_models(results: Dict[str, Dict[str, float]]):
    """
    Print comparison table of multiple models
    
    Args:
        results: Dictionary mapping model_name -> metrics_dict
    """
    print(f"\n{'='*80}")
    print("MODEL COMPARISON")
    print(f"{'='*80}\n")
    
    # Get all metric names
    all_metrics = set()
    for metrics in results.values():
        all_metrics.update(metrics.keys())
    
    # Print header
    print(f"{'Metric':<25}", end='')
    for model_name in results.keys():
        print(f"{model_name:<20}", end='')
    print()
    print("-" * 80)
    
    # Print each metric
    for metric in sorted(all_metrics):
        print(f"{metric:<25}", end='')
        for model_name in results.keys():
            value = results[model_name].get(metric, 0)
            if isinstance(value, float):
                print(f"{value:<20.4f}", end='')
            else:
                print(f"{value:<20}", end='')
        print()
    
    print(f"\n{'='*80}\n")
    
    # Find best model for each metric
    print("🏆 BEST PERFORMERS:")
    print("-" * 40)
    
    important_metrics = ['rmse', 'mae', 'precision_at_k', 'recall_at_k', 'coverage']
    
    for metric in important_metrics:
        if metric in all_metrics:
            # Lower is better for RMSE/MAE, higher for others
            is_lower_better = metric in ['rmse', 'mae']
            
            best_model = None
            best_value = float('inf') if is_lower_better else float('-inf')
            
            for model_name, metrics in results.items():
                value = metrics.get(metric, float('inf') if is_lower_better else float('-inf'))
                if is_lower_better:
                    if value < best_value:
                        best_value = value
                        best_model = model_name
                else:
                    if value > best_value:
                        best_value = value
                        best_model = model_name
            
            arrow = "↓" if is_lower_better else "↑"
            print(f"{metric:<20} {arrow}: {best_model:<15} ({best_value:.4f})")
