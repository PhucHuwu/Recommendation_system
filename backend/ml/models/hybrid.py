"""
Hybrid Collaborative Filtering Model

Combines User-Based and Item-Based CF using weighted strategy:
- Leverages strengths of both approaches
- Falls back gracefully when one model can't predict
- Supports weight optimization
"""

import numpy as np
import pickle
from typing import List, Tuple, Optional, Union
from .user_based import UserBasedCF
from .item_based import ItemBasedCF


class HybridWeightedCF:
    """
    Hybrid CF using weighted combination of User-Based and Item-Based predictions
    
    Prediction strategy:
    - pred_hybrid = α × pred_user + β × pred_item
    - where α + β = 1
    - Handles cases where one model can't predict (fallback)
    """
    
    def __init__(self, 
                 user_based_model: UserBasedCF, 
                 item_based_model: ItemBasedCF,
                 user_weight: float = 0.5,
                 item_weight: float = 0.5):
        """
        Initialize Hybrid model
        
        Args:
            user_based_model: Trained User-Based CF model
            item_based_model: Trained Item-Based CF model
            user_weight: Weight for user-based predictions (α)
            item_weight: Weight for item-based predictions (β)
        """
        self.user_model = user_based_model
        self.item_model = item_based_model
        self.user_weight = user_weight
        self.item_weight = item_weight
        
        # Normalize weights
        total = user_weight + item_weight
        if total > 0:
            self.user_weight = user_weight / total
            self.item_weight = item_weight / total
        
        print(f"Hybrid Model initialized:")
        print(f"  User-Based weight: {self.user_weight:.2f}")
        print(f"  Item-Based weight: {self.item_weight:.2f}")
    
    def predict(self, user_id: int, anime_id: int) -> float:
        """
        Predict rating using weighted combination
        
        Algorithm:
        1. Get prediction from both models
        2. If both can predict: weighted average
        3. If only one can predict: use that one
        4. If neither can predict: return 0
        
        Args:
            user_id: User ID
            anime_id: Anime ID
            
        Returns:
            Predicted rating (1-10), or 0 if cannot predict
        """
        user_pred = self.user_model.predict(user_id, anime_id)
        item_pred = self.item_model.predict(user_id, anime_id)
        
        # Both models can predict
        if user_pred > 0 and item_pred > 0:
            return self.user_weight * user_pred + self.item_weight * item_pred
        
        # Only user-based can predict
        if user_pred > 0:
            return user_pred
        
        # Only item-based can predict  
        if item_pred > 0:
            return item_pred
        
        # Neither can predict
        return 0.0
    
    def recommend(self, user_id: int, n: int = 10, exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        Recommend using hybrid approach
        
        Strategy:
        1. Get recommendations from both models
        2. Merge and re-rank by weighted scores
        3. Return top N
        
        Args:
            user_id: User ID
            n: Number of recommendations
            exclude_rated: Exclude already rated items
            
        Returns:
            List of (anime_id, predicted_rating) tuples
        """
        # Get recommendations from both models (get more than N for better coverage)
        user_recs = self.user_model.recommend(user_id, n=n*2, exclude_rated=exclude_rated)
        item_recs = self.item_model.recommend(user_id, n=n*2, exclude_rated=exclude_rated)
        
        # Merge predictions
        anime_scores = {}
        
        # Add user-based predictions
        for anime_id, score in user_recs:
            anime_scores[anime_id] = self.user_weight * score
        
        # Add/merge item-based predictions
        for anime_id, score in item_recs:
            if anime_id in anime_scores:
                anime_scores[anime_id] += self.item_weight * score
            else:
                anime_scores[anime_id] = self.item_weight * score
        
        # Sort by score
        sorted_recs = sorted(anime_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_recs[:n]
    
    def save(self, filepath: str):
        """Save hybrid model configuration"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'user_weight': self.user_weight,
                'item_weight': self.item_weight,
                # Note: Individual models must be saved separately
            }, f)
        print(f"Hybrid model config saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str, 
             user_model: UserBasedCF, 
             item_model: ItemBasedCF) -> 'HybridWeightedCF':
        """Load hybrid model configuration"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        model = cls(
            user_model,
            item_model,
            user_weight=data['user_weight'],
            item_weight=data['item_weight']
        )
        
        print(f"Hybrid model config loaded from {filepath}")
        return model


class HybridSwitchingCF:
    """
    Hybrid CF using switching strategy based on confidence
    
    Choose best model based on:
    - User activity (# of ratings)
    - Item popularity (# of ratings)
    """
    
    def __init__(self,
                 user_based_model: UserBasedCF,
                 item_based_model: ItemBasedCF,
                 user_threshold: int = 20,
                 item_threshold: int = 50):
        """
        Initialize switching hybrid
        
        Args:
            user_based_model: User-Based CF model
            item_based_model: Item-Based CF model
            user_threshold: Min ratings to prefer user-based
            item_threshold: Min ratings to prefer item-based
        """
        self.user_model = user_based_model
        self.item_model = item_based_model
        self.user_threshold = user_threshold
        self.item_threshold = item_threshold
    
    def predict(self, user_id: int, anime_id: int) -> float:
        """
        Predict using switching strategy
        
        Decision logic:
        - If user is active (>threshold ratings) → use User-Based
        - Else if item is popular (>threshold ratings) → use Item-Based
        - Else → use weighted average
        """
        # Get user activity
        user_idx = self.user_model.user_id_map.get(user_id, -1)
        anime_idx = self.item_model.anime_id_map.get(anime_id, -1)
        
        user_activity = 0
        item_popularity = 0
        
        if user_idx >= 0 and self.user_model.user_item_matrix is not None:
            user_activity = self.user_model.user_item_matrix[user_idx].nnz
        
        if anime_idx >= 0 and self.item_model.user_item_matrix is not None:
            item_popularity = self.item_model.user_item_matrix[:, anime_idx].nnz
        
        # Switching logic
        if user_activity >= self.user_threshold:
            return self.user_model.predict(user_id, anime_id)
        elif item_popularity >= self.item_threshold:
            return self.item_model.predict(user_id, anime_id)
        else:
            # Weighted average as fallback
            user_pred = self.user_model.predict(user_id, anime_id)
            item_pred = self.item_model.predict(user_id, anime_id)
            
            if user_pred > 0 and item_pred > 0:
                return 0.5 * user_pred + 0.5 * item_pred
            elif user_pred > 0:
                return user_pred
            else:
                return item_pred
    
    def recommend(self, user_id: int, n: int = 10, exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """Recommend using switching logic"""
        # For simplicity, use weighted approach for recommendations
        user_idx = self.user_model.user_id_map.get(user_id, -1)
        user_activity = 0
        
        if user_idx >= 0 and self.user_model.user_item_matrix is not None:
            user_activity = self.user_model.user_item_matrix[user_idx].nnz
        
        if user_activity >= self.user_threshold:
            return self.user_model.recommend(user_id, n, exclude_rated)
        else:
            return self.item_model.recommend(user_id, n, exclude_rated)
