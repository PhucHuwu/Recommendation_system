"""
Model Evaluation Metrics Module

This module provides evaluation metrics for recommendation systems.
Supports both rating prediction and ranking metrics.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


class RecommendationMetrics:
    """
    Evaluation metrics for recommendation systems.
    
    Supports:
    - Rating prediction metrics: RMSE, MAE
    - Ranking metrics: Precision@K, Recall@K, F1@K, NDCG@K
    - Coverage and diversity metrics
    """
    
    def __init__(self, verbose=True):
        """
        Initialize metrics calculator.
        
        Args:
            verbose (bool): Print progress messages
        """
        self.verbose = verbose
        
    def _log(self, message):
        """Print message if verbose mode is on."""
        if self.verbose:
            print(message)
    
    # ===== Rating Prediction Metrics =====
    
    def rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Root Mean Squared Error.
        
        Args:
            y_true: True ratings
            y_pred: Predicted ratings
            
        Returns:
            RMSE score
        """
        mse = np.mean((y_true - y_pred) ** 2)
        return np.sqrt(mse)
    
    def mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Mean Absolute Error.
        
        Args:
            y_true: True ratings
            y_pred: Predicted ratings
            
        Returns:
            MAE score
        """
        return np.mean(np.abs(y_true - y_pred))
    
    # ===== Ranking Metrics =====
    
    def precision_at_k(self, recommended: List, relevant: List, k: int = 10) -> float:
        """
        Calculate Precision@K.
        
        Precision@K = (# of recommended items @K that are relevant) / K
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Number of top recommendations to consider
            
        Returns:
            Precision@K score
        """
        if k == 0:
            return 0.0
        
        recommended_at_k = recommended[:k]
        relevant_set = set(relevant)
        
        num_relevant_and_recommended = len(set(recommended_at_k) & relevant_set)
        
        return num_relevant_and_recommended / k
    
    def recall_at_k(self, recommended: List, relevant: List, k: int = 10) -> float:
        """
        Calculate Recall@K.
        
        Recall@K = (# of recommended items @K that are relevant) / (total # of relevant items)
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Number of top recommendations to consider
            
        Returns:
            Recall@K score
        """
        if len(relevant) == 0:
            return 0.0
        
        recommended_at_k = recommended[:k]
        relevant_set = set(relevant)
        
        num_relevant_and_recommended = len(set(recommended_at_k) & relevant_set)
        
        return num_relevant_and_recommended / len(relevant)
    
    def f1_at_k(self, recommended: List, relevant: List, k: int = 10) -> float:
        """
        Calculate F1-Score@K.
        
        F1@K = 2 * (Precision@K * Recall@K) / (Precision@K + Recall@K)
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Number of top recommendations to consider
            
        Returns:
            F1@K score
        """
        precision = self.precision_at_k(recommended, relevant, k)
        recall = self.recall_at_k(recommended, relevant, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def ndcg_at_k(self, recommended: List, relevant: List, k: int = 10) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain@K.
        
        NDCG accounts for the position of relevant items in the recommendation list.
        Higher ranked relevant items contribute more to the score.
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Number of top recommendations to consider
            
        Returns:
            NDCG@K score
        """
        if len(relevant) == 0:
            return 0.0
        
        recommended_at_k = recommended[:k]
        relevant_set = set(relevant)
        
        # Calculate DCG
        dcg = 0.0
        for i, item in enumerate(recommended_at_k):
            if item in relevant_set:
                # Binary relevance (1 if relevant, 0 otherwise)
                # Position is i+1 (1-indexed)
                dcg += 1.0 / np.log2(i + 2)  # +2 because log2(1) = 0
        
        # Calculate IDCG (Ideal DCG)
        idcg = 0.0
        for i in range(min(len(relevant), k)):
            idcg += 1.0 / np.log2(i + 2)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def average_precision_at_k(self, recommended: List, relevant: List, k: int = 10) -> float:
        """
        Calculate Average Precision@K.
        
        AP@K considers the order of relevant items.
        
        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Number of top recommendations to consider
            
        Returns:
            AP@K score
        """
        if len(relevant) == 0:
            return 0.0
        
        recommended_at_k = recommended[:k]
        relevant_set = set(relevant)
        
        num_hits = 0
        sum_precisions = 0.0
        
        for i, item in enumerate(recommended_at_k):
            if item in relevant_set:
                num_hits += 1
                precision_at_i = num_hits / (i + 1)
                sum_precisions += precision_at_i
        
        if num_hits == 0:
            return 0.0
        
        return sum_precisions / min(len(relevant), k)
    
    # ===== Coverage & Diversity Metrics =====
    
    def catalog_coverage(self, recommended_items: List[List], total_items: int) -> float:
        """
        Calculate catalog coverage.
        
        Coverage = (# of unique items recommended) / (total # of items)
        
        Args:
            recommended_items: List of recommendation lists
            total_items: Total number of items in catalog
            
        Returns:
            Coverage score (0-1)
        """
        unique_recommended = set()
        for recs in recommended_items:
            unique_recommended.update(recs)
        
        return len(unique_recommended) / total_items if total_items > 0 else 0.0
    
    def diversity(self, recommended_items: List[List]) -> float:
        """
        Calculate diversity as average pairwise dissimilarity.
        
        Simple diversity metric based on unique items per user.
        
        Args:
            recommended_items: List of recommendation lists
            
        Returns:
            Average diversity score
        """
        if len(recommended_items) == 0:
            return 0.0
        
        diversities = []
        for recs in recommended_items:
            if len(recs) > 1:
                # Diversity = ratio of unique items
                diversity = len(set(recs)) / len(recs)
                diversities.append(diversity)
        
        return np.mean(diversities) if diversities else 0.0
    
    # ===== Batch Evaluation =====
    
    def evaluate_ranking(
        self,
        recommendations: Dict[int, List],
        ground_truth: Dict[int, List],
        k_values: List[int] = [5, 10, 20]
    ) -> Dict[str, Dict[int, float]]:
        """
        Evaluate ranking metrics for multiple users.
        
        Args:
            recommendations: Dict mapping user_id to list of recommended item_ids
            ground_truth: Dict mapping user_id to list of relevant item_ids
            k_values: List of K values to evaluate
            
        Returns:
            Dict with metrics for each K value
        """
        self._log(f"Evaluating ranking metrics for {len(recommendations)} users...")
        
        results = {
            'precision@k': {k: [] for k in k_values},
            'recall@k': {k: [] for k in k_values},
            'f1@k': {k: [] for k in k_values},
            'ndcg@k': {k: [] for k in k_values},
            'ap@k': {k: [] for k in k_values}
        }
        
        for user_id in recommendations:
            if user_id not in ground_truth:
                continue
            
            recommended = recommendations[user_id]
            relevant = ground_truth[user_id]
            
            for k in k_values:
                results['precision@k'][k].append(
                    self.precision_at_k(recommended, relevant, k)
                )
                results['recall@k'][k].append(
                    self.recall_at_k(recommended, relevant, k)
                )
                results['f1@k'][k].append(
                    self.f1_at_k(recommended, relevant, k)
                )
                results['ndcg@k'][k].append(
                    self.ndcg_at_k(recommended, relevant, k)
                )
                results['ap@k'][k].append(
                    self.average_precision_at_k(recommended, relevant, k)
                )
        
        # Average across users
        averaged_results = {}
        for metric_name, metric_dict in results.items():
            averaged_results[metric_name] = {
                k: np.mean(values) if values else 0.0
                for k, values in metric_dict.items()
            }
        
        return averaged_results
    
    def print_evaluation_results(self, results: Dict[str, Dict[int, float]]):
        """
        Print evaluation results in a formatted table.
        
        Args:
            results: Dict from evaluate_ranking()
        """
        print("\n" + "=" * 70)
        print("RANKING METRICS EVALUATION RESULTS")
        print("=" * 70)
        
        k_values = sorted(list(results['precision@k'].keys()))
        
        print(f"\n{'Metric':<20} " + " ".join([f"@{k:<8}" for k in k_values]))
        print("-" * 70)
        
        for metric_name in ['precision@k', 'recall@k', 'f1@k', 'ndcg@k', 'ap@k']:
            values_str = " ".join([
                f"{results[metric_name][k]:.4f}   "
                for k in k_values
            ])
            print(f"{metric_name:<20} {values_str}")


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("RECOMMENDATION METRICS - EXAMPLE")
    print("=" * 70)
    
    metrics = RecommendationMetrics(verbose=True)
    
    # Example 1: Rating prediction metrics
    print("\n1. RATING PREDICTION METRICS:")
    y_true = np.array([4.0, 3.5, 5.0, 2.0, 4.5])
    y_pred = np.array([3.8, 3.2, 4.8, 2.5, 4.2])
    
    rmse = metrics.rmse(y_true, y_pred)
    mae = metrics.mae(y_true, y_pred)
    
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    
    # Example 2: Ranking metrics
    print("\n2. RANKING METRICS:")
    recommended = [1, 5, 8, 12, 15, 20, 25, 30, 35, 40]
    relevant = [5, 8, 10, 22, 30]
    
    for k in [5, 10]:
        precision = metrics.precision_at_k(recommended, relevant, k)
        recall = metrics.recall_at_k(recommended, relevant, k)
        f1 = metrics.f1_at_k(recommended, relevant, k)
        ndcg = metrics.ndcg_at_k(recommended, relevant, k)
        
        print(f"\nMetrics @{k}:")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        print(f"  NDCG: {ndcg:.4f}")
    
    # Example 3: Batch evaluation
    print("\n3. BATCH EVALUATION:")
    recommendations = {
        1: [1, 5, 8, 12, 15],
        2: [2, 6, 9, 13, 16],
        3: [3, 7, 10, 14, 17]
    }
    ground_truth = {
        1: [5, 8, 10],
        2: [2, 6, 20],
        3: [7, 10, 14, 17]
    }
    
    results = metrics.evaluate_ranking(recommendations, ground_truth, k_values=[5, 10])
    metrics.print_evaluation_results(results)
    
    print("\n" + "=" * 70)
    print("METRICS MODULE - COMPLETE")
    print("=" * 70)
