"""
User-Based Collaborative Filtering - Neighborhood Approach

Implementation của classical User-Based CF:
- Tìm K nearest neighbors dựa trên user similarity
- Predict rating bằng weighted average của neighbor ratings
- Support cosine và pearson similarity
"""

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
import pickle
from typing import List, Tuple, Optional
from collections import defaultdict


class UserBasedCF:
    """User-Based Collaborative Filtering Model"""
    
    def __init__(self, k_neighbors: int = 50, similarity: str = 'cosine', min_overlap: int = 3):
        """
        Initialize User-Based CF
        
        Args:
            k_neighbors: Number of similar users to consider for prediction
            similarity: Similarity metric ('cosine' or 'pearson')
            min_overlap: Minimum number of co-rated items required for similarity
        """
        self.k_neighbors = k_neighbors
        self.similarity_metric = similarity
        self.min_overlap = min_overlap
        
        # Model state
        self.user_item_matrix = None
        self.user_similarity = None
        self.user_means = None  # For pearson correlation
        
        # Mappings
        self.user_id_map = {}  # user_id -> matrix index
        self.anime_id_map = {}  # anime_id -> matrix index
        self.reverse_user_map = {}  # matrix index -> user_id
        self.reverse_anime_map = {}  # matrix index -> anime_id
        
    def fit(self, ratings_data: List[dict]):
        """
        Train the model with rating data
        
        Args:
            ratings_data: List of rating dicts with keys: user_id, anime_id, rating
        """
        print(f"Training User-Based CF (k={self.k_neighbors}, similarity={self.similarity_metric})...")
        
        # Create mappings
        unique_users = sorted(set([r['user_id'] for r in ratings_data]))
        unique_animes = sorted(set([r['anime_id'] for r in ratings_data]))
        
        self.user_id_map = {uid: idx for idx, uid in enumerate(unique_users)}
        self.anime_id_map = {aid: idx for idx, aid in enumerate(unique_animes)}
        self.reverse_user_map = {idx: uid for uid, idx in self.user_id_map.items()}
        self.reverse_anime_map = {idx: aid for aid, idx in self.anime_id_map.items()}
        
        print(f"  Users: {len(unique_users):,}")
        print(f"  Animes: {len(unique_animes):,}")
        print(f"  Ratings: {len(ratings_data):,}")
        
        # Build sparse user-item matrix
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
        
        sparsity = 1 - (self.user_item_matrix.nnz / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]))
        print(f"  Matrix shape: {self.user_item_matrix.shape}")
        print(f"  Sparsity: {sparsity * 100:.2f}%")
        
        # Compute user means (for pearson)
        if self.similarity_metric == 'pearson':
            print("  Computing user means...")
            self.user_means = np.array([
                self.user_item_matrix[i].data.mean() if self.user_item_matrix[i].nnz > 0 else 0
                for i in range(self.user_item_matrix.shape[0])
            ])
        
        # Compute user-user similarity
        print("  Computing user similarity matrix...")
        self.user_similarity = self._compute_similarity()
        
        print("  Training complete!")
        
    def _compute_similarity(self) -> csr_matrix:
        """
        Compute user-user similarity matrix
        
        Returns:
            Sparse similarity matrix (n_users × n_users)
        """
        if self.similarity_metric == 'cosine':
            # Standard cosine similarity
            return sklearn_cosine(self.user_item_matrix, dense_output=False)
            
        elif self.similarity_metric == 'pearson':
            # Pearson correlation = cosine on mean-centered data
            # Center each user's ratings by their mean
            centered_matrix = self.user_item_matrix.copy().astype(np.float32)
            
            # Mean-center: subtract user mean from non-zero entries
            for i in range(centered_matrix.shape[0]):
                if centered_matrix[i].nnz > 0:
                    centered_matrix[i].data -= self.user_means[i]
            
            return sklearn_cosine(centered_matrix, dense_output=False)
        
        else:
            raise ValueError(f"Unknown similarity metric: {self.similarity_metric}")
    
    def predict(self, user_id: int, anime_id: int) -> float:
        """
        Predict rating for a user-anime pair using neighborhood-based approach
        
        Algorithm:
        1. Find K nearest neighbors who rated this anime
        2. Compute weighted average: Σ(sim(u,v) × rating(v,i)) / Σ|sim(u,v)|
        
        Args:
            user_id: User ID
            anime_id: Anime ID
            
        Returns:
            Predicted rating (1-10), or 0 if cannot predict
        """
        # Check if user and anime exist
        if user_id not in self.user_id_map or anime_id not in self.anime_id_map:
            return 0.0
        
        user_idx = self.user_id_map[user_id]
        anime_idx = self.anime_id_map[anime_id]
        
        # Get similarity scores for this user
        user_sims = self.user_similarity[user_idx].toarray().flatten()
        
        # Get users who rated this anime
        rated_users_mask = self.user_item_matrix[:, anime_idx].toarray().flatten() > 0
        
        # Find neighbors who rated this anime (exclude self)
        valid_mask = rated_users_mask & (user_sims > 0)
        valid_mask[user_idx] = False  # Exclude self
        
        if not valid_mask.any():
            return 0.0
        
        # Get top K neighbors by similarity
        valid_indices = np.where(valid_mask)[0]
        valid_sims = user_sims[valid_indices]
        
        # Sort by similarity, take top K
        if len(valid_indices) > self.k_neighbors:
            top_k_mask = np.argsort(valid_sims)[-self.k_neighbors:]
            valid_indices = valid_indices[top_k_mask]
            valid_sims = valid_sims[top_k_mask]
        
        # Get ratings from neighbors
        neighbor_ratings = self.user_item_matrix[valid_indices, anime_idx].toarray().flatten()
        
        # Weighted average
        sim_sum = np.abs(valid_sims).sum()
        if sim_sum == 0:
            return 0.0
        
        predicted_rating = np.dot(valid_sims, neighbor_ratings) / sim_sum
        
        # Clip to valid range
        return float(np.clip(predicted_rating, 1, 10))
    
    def recommend(self, user_id: int, n: int = 10, exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        Recommend top N animes for a user using VECTORIZED prediction
        
        Args:
            user_id: User ID
            n: Number of recommendations
            exclude_rated: Whether to exclude already rated animes
            
        Returns:
            List of (anime_id, predicted_rating) tuples, sorted by rating
        """
        if user_id not in self.user_id_map:
            return []
        
        user_idx = self.user_id_map[user_id]
        
        # Get user's similarity row
        user_sims = self.user_similarity[user_idx].toarray().flatten()
        
        # Find top K neighbors (exclude self)
        user_sims[user_idx] = -1  # Exclude self
        top_k_indices = np.argsort(user_sims)[-self.k_neighbors:]
        top_k_sims = user_sims[top_k_indices]
        
        # Filter positive similarities
        positive_mask = top_k_sims > 0
        if not positive_mask.any():
            return []
        
        top_k_indices = top_k_indices[positive_mask]
        top_k_sims = top_k_sims[positive_mask]
        
        # Get ratings from top K neighbors (sparse matrix)
        neighbor_ratings = self.user_item_matrix[top_k_indices, :]
        
        # VECTORIZED prediction for all animes
        sim_sum = top_k_sims.sum()
        if sim_sum == 0:
            return []
        
        # Weighted average: (K × n_items) × (K,) = (n_items,)
        predictions = neighbor_ratings.T.dot(top_k_sims) / sim_sum
        predictions = np.clip(predictions, 0, 10)
        
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
                'similarity_metric': self.similarity_metric,
                'min_overlap': self.min_overlap,
                'user_item_matrix': self.user_item_matrix,
                'user_similarity': self.user_similarity,
                'user_means': self.user_means,
                'user_id_map': self.user_id_map,
                'anime_id_map': self.anime_id_map,
                'reverse_user_map': self.reverse_user_map,
                'reverse_anime_map': self.reverse_anime_map
            }, f)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'UserBasedCF':
        """Load model from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        model = cls(
            k_neighbors=data['k_neighbors'],
            similarity=data['similarity_metric'],
            min_overlap=data['min_overlap']
        )
        model.user_item_matrix = data['user_item_matrix']
        model.user_similarity = data['user_similarity']
        model.user_means = data['user_means']
        model.user_id_map = data['user_id_map']
        model.anime_id_map = data['anime_id_map']
        model.reverse_user_map = data['reverse_user_map']
        model.reverse_anime_map = data['reverse_anime_map']
        
        print(f"Model loaded from {filepath}")
        return model
