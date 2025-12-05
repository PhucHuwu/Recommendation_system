"""
User-Based Collaborative Filtering

Gợi ý anime dựa trên sự tương đồng giữa các users.
Sử dụng Cosine Similarity hoặc Pearson Correlation.
"""

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from typing import List, Tuple


class UserBasedCF:
    """User-Based Collaborative Filtering Model"""
    
    def __init__(self, k_neighbors: int = 50):
        """
        Initialize User-Based CF
        
        Args:
            k_neighbors: Number of similar users to consider
        """
        self.k_neighbors = k_neighbors
        self.user_similarity = None
        self.user_item_matrix = None
        self.user_id_map = {}  # Map user_id to matrix index
        self.anime_id_map = {}  # Map anime_id to matrix index
        self.reverse_anime_map = {}  # Map matrix index to anime_id
        
    def fit(self, ratings_data: List[dict]):
        """
        Train the model with rating data
        
        Args:
            ratings_data: List of rating dicts with keys: user_id, anime_id, rating
        """
        print("Training User-Based CF...")
        
        # Create mappings
        unique_users = sorted(set([r['user_id'] for r in ratings_data]))
        unique_animes = sorted(set([r['anime_id'] for r in ratings_data]))
        
        self.user_id_map = {uid: idx for idx, uid in enumerate(unique_users)}
        self.anime_id_map = {aid: idx for idx, aid in enumerate(unique_animes)}
        self.reverse_anime_map = {idx: aid for aid, idx in self.anime_id_map.items()}
        
        print(f"  Users: {len(unique_users):,}")
        print(f"  Animes: {len(unique_animes):,}")
        print(f"  Ratings: {len(ratings_data):,}")
        
        # Create sparse user-item matrix
        rows, cols, data = [], [], []
        for rating in ratings_data:
            user_idx = self.user_id_map[rating['user_id']]
            anime_idx = self.anime_id_map[rating['anime_id']]
            rows.append(user_idx)
            cols.append(anime_idx)
            data.append(rating['rating'])
        
        self.user_item_matrix = csr_matrix(
            (data, (rows, cols)),
            shape=(len(unique_users), len(unique_animes)),
            dtype=np.float32
        )
        
        print(f"  Matrix shape: {self.user_item_matrix.shape}")
        print(f"  Sparsity: {(1 - self.user_item_matrix.nnz / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1])) * 100:.2f}%")
        
        # Compute user similarity
        print("  Computing user similarity...")
        self.user_similarity = cosine_similarity(self.user_item_matrix, dense_output=False)
        
        print("  Training complete!")
        
    def predict(self, user_id: int, anime_id: int) -> float:
        """
        Predict rating for a user-anime pair
        
        Args:
            user_id: User ID
            anime_id: Anime ID
            
        Returns:
            Predicted rating (1-10)
        """
        if user_id not in self.user_id_map or anime_id not in self.anime_id_map:
            return 0.0
        
        user_idx = self.user_id_map[user_id]
        anime_idx = self.anime_id_map[anime_id]
        
        # Get k most similar users who have rated this anime
        user_sims = self.user_similarity[user_idx].toarray().flatten()
        
        # Get users who rated this anime
        rated_users_mask = self.user_item_matrix[:, anime_idx].toarray().flatten() > 0
        
        # Filter to only similar users who rated this anime
        valid_users = rated_users_mask & (user_sims > 0)
        
        if not valid_users.any():
            # No similar users, return global mean or 0
            return 0.0
        
        # Get top k similar users
        valid_indices = np.where(valid_users)[0]
        valid_sims = user_sims[valid_indices]
        
        # Sort by similarity and take top k
        top_k_indices = valid_indices[np.argsort(valid_sims)[-self.k_neighbors:]]
        top_k_sims = user_sims[top_k_indices]
        
        # Get ratings from top k users
        top_k_ratings = self.user_item_matrix[top_k_indices, anime_idx].toarray().flatten()
        
        # Weighted average
        if top_k_sims.sum() == 0:
            return 0.0
        
        predicted_rating = np.dot(top_k_sims, top_k_ratings) / top_k_sims.sum()
        
        # Clip to 1-10 range
        return np.clip(predicted_rating, 1, 10)
    
    def recommend(self, user_id: int, n: int = 10, exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        Recommend top N animes for a user using VECTORIZED computation
        
        Args:
            user_id: User ID
            n: Number of recommendations
            exclude_rated: Whether to exclude already rated animes
            
        Returns:
            List of (anime_id, predicted_rating) tuples
        """
        if user_id not in self.user_id_map:
            return []
        
        user_idx = self.user_id_map[user_id]
        
        # Get user's similarity row (keep sparse!)
        user_sims = self.user_similarity[user_idx]
        
        # Get top K most similar users
        user_sims_dense = user_sims.toarray().flatten()
        top_k_user_indices = np.argsort(user_sims_dense)[-self.k_neighbors:]
        top_k_sims = user_sims_dense[top_k_user_indices]
        
        # Filter out users with zero similarity
        positive_mask = top_k_sims > 0
        if not positive_mask.any():
            return []
        
        top_k_user_indices = top_k_user_indices[positive_mask]
        top_k_sims = top_k_sims[positive_mask]
        
        # Get ratings from top K users (sparse sub-matrix)
        top_k_ratings = self.user_item_matrix[top_k_user_indices, :]
        
        # VECTORIZED: Compute weighted average for ALL animes at once
        # Shape: (k_users, n_animes) → weighted by similarity → (n_animes,)
        sim_sum = top_k_sims.sum()
        if sim_sum == 0:
            return []
        
        # Weighted ratings: similarity weights × ratings matrix
        weighted_ratings = top_k_ratings.T.dot(top_k_sims) / sim_sum
        
        # Clip predictions
        predictions = np.clip(weighted_ratings, 0, 10)
        
        # Exclude rated animes
        if exclude_rated:
            rated_animes = self.user_item_matrix[user_idx].nonzero()[1]
            predictions[rated_animes] = 0
        
        # Get top N
        top_n_indices = np.argsort(predictions)[-n:][::-1]
        
        result = []
        for idx in top_n_indices:
            if predictions[idx] > 0:
                anime_id = self.reverse_anime_map[idx]
                result.append((anime_id, float(predictions[idx])))
        
        return result
    
    def save(self, filepath: str):
        """Save model to file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'k_neighbors': self.k_neighbors,
                'user_similarity': self.user_similarity,
                'user_item_matrix': self.user_item_matrix,
                'user_id_map': self.user_id_map,
                'anime_id_map': self.anime_id_map,
                'reverse_anime_map': self.reverse_anime_map
            }, f)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load model from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        model = cls(k_neighbors=data['k_neighbors'])
        model.user_similarity = data['user_similarity']
        model.user_item_matrix = data['user_item_matrix']
        model.user_id_map = data['user_id_map']
        model.anime_id_map = data['anime_id_map']
        model.reverse_anime_map = data['reverse_anime_map']
        
        print(f"Model loaded from {filepath}")
        return model
