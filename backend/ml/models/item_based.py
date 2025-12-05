"""
Item-Based Collaborative Filtering - Similarity Approach

Implementation của classical Item-Based CF:
- Compute item-item similarity using adjusted cosine
- Predict rating bằng weighted sum of user's ratings for similar items
- More stable than user-based for sparse data
"""

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
import pickle
from typing import List, Tuple, Optional


class ItemBasedCF:
    """Item-Based Collaborative Filtering Model"""
    
    def __init__(self, k_similar: int = 30, similarity: str = 'adjusted_cosine'):
        """
        Initialize Item-Based CF
        
        Args:
            k_similar: Number of similar items to consider for prediction
            similarity: Similarity metric ('cosine' or 'adjusted_cosine')
        """
        self.k_similar = k_similar
        self.similarity_metric = similarity
        
        # Model state
        self.user_item_matrix = None
        self.item_similarity = None
        self.user_means = None  # For adjusted cosine
        
        # Mappings
        self.user_id_map = {}
        self.anime_id_map = {}
        self.reverse_user_map = {}
        self.reverse_anime_map = {}
        
    def fit(self, ratings_data: List[dict]):
        """
        Train the model with rating data
        
        Args:
            ratings_data: List of rating dicts with keys: user_id, anime_id, rating
        """
        print(f"Training Item-Based CF (k={self.k_similar}, similarity={self.similarity_metric})...")
        
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
        
        # Compute user means (for adjusted cosine)
        print("  Computing user means...")
        self.user_means = np.array([
            self.user_item_matrix[i].data.mean() if self.user_item_matrix[i].nnz > 0 else 0
            for i in range(self.user_item_matrix.shape[0])
        ])
        
        # Compute item-item similarity
        print("  Computing item similarity matrix...")
        self.item_similarity = self._compute_similarity()
        
        print("  Training complete!")
        
    def _compute_similarity(self) -> csr_matrix:
        """
        Compute item-item similarity matrix
        
        Uses adjusted cosine similarity:
        sim(i, j) = Σ((R_u,i - R̄_u) × (R_u,j - R̄_u)) / (||R_i - R̄|| × ||R_j - R̄||)
        
        This normalizes for different user rating scales
        
        Returns:
            Sparse similarity matrix (n_items × n_items)
        """
        if self.similarity_metric == 'cosine':
            # Standard cosine on item vectors (transpose user-item matrix)
            return sklearn_cosine(self.user_item_matrix.T, dense_output=False)
            
        elif self.similarity_metric == 'adjusted_cosine':
            # Adjusted cosine: mean-center by user, then compute cosine
            centered_matrix = self.user_item_matrix.copy().astype(np.float32)
            
            # Subtract user mean from each rating
            for i in range(centered_matrix.shape[0]):
                if centered_matrix[i].nnz > 0:
                    centered_matrix[i].data -= self.user_means[i]
            
            # Compute cosine on transpose (item vectors)
            return sklearn_cosine(centered_matrix.T, dense_output=False)
        
        else:
            raise ValueError(f"Unknown similarity metric: {self.similarity_metric}")
    
    def predict(self, user_id: int, anime_id: int) -> float:
        """
        Predict rating for a user-anime pair using item similarity
        
        Algorithm:
        1. Find K most similar items to target item
        2. Filter those that user has rated
        3. Compute weighted average: Σ(sim(i,j) × rating(u,j)) / Σ|sim(i,j)|
        
        Args:
            user_id: User ID
            anime_id: Anime ID
            
        Returns:
            Predicted rating (1-10), or 0 if cannot predict
        """
        if user_id not in self.user_id_map or anime_id not in self.anime_id_map:
            return 0.0
        
        user_idx = self.user_id_map[user_id]
        anime_idx = self.anime_id_map[anime_id]
        
        # Get animes rated by this user
        rated_animes = self.user_item_matrix[user_idx].nonzero()[1]
        
        if len(rated_animes) == 0:
            return 0.0
        
        # Get similarity scores between target anime and rated animes
        item_sims = self.item_similarity[anime_idx, rated_animes].toarray().flatten()
        
        # Get user's ratings for those animes
        user_ratings = self.user_item_matrix[user_idx, rated_animes].toarray().flatten()
        
        # Take top K similar items
        if len(item_sims) > self.k_similar:
            top_k_mask = np.argsort(item_sims)[-self.k_similar:]
            item_sims = item_sims[top_k_mask]
            user_ratings = user_ratings[top_k_mask]
        
        # Filter positive similarities
        positive_mask = item_sims > 0
        if not positive_mask.any():
            return 0.0
        
        item_sims = item_sims[positive_mask]
        user_ratings = user_ratings[positive_mask]
        
        # Weighted average
        sim_sum = item_sims.sum()
        if sim_sum == 0:
            return 0.0
        
        predicted_rating = np.dot(item_sims, user_ratings) / sim_sum
        
        return float(np.clip(predicted_rating, 1, 10))
    
    def recommend(self, user_id: int, n: int = 10, exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        Recommend top N animes for a user using VECTORIZED prediction
        
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
        
        # Get user's rated animes and ratings
        rated_animes = self.user_item_matrix[user_idx].nonzero()[1]
        
        if len(rated_animes) == 0:
            return []
        
        user_ratings = self.user_item_matrix[user_idx, rated_animes].toarray().flatten()
        
        # Get item similarity for rated animes
        # Shape: (n_rated_animes, n_all_animes)
        item_sims = self.item_similarity[rated_animes, :]
        
        # VECTORIZED: Compute predictions for all animes
        # weighted_sum: (n_items,) = (n_rated, n_items).T × (n_rated,)
        weighted_sum = item_sims.T.dot(user_ratings)
        
        # Similarity sum for normalization
        sim_sum_matrix = np.abs(item_sims).sum(axis=0)
        
        # Convert to 1D array (handle both sparse and dense)
        if hasattr(sim_sum_matrix, 'A1'):
            sim_sum = sim_sum_matrix.A1
        else:
            sim_sum = np.asarray(sim_sum_matrix).flatten()
        
        # Avoid division by zero
        sim_sum[sim_sum == 0] = 1e-10
        
        # Predicted ratings
        if hasattr(weighted_sum, 'A1'):
            predictions = weighted_sum.A1 / sim_sum
        else:
            predictions = np.asarray(weighted_sum).flatten() / sim_sum
            
        predictions = np.clip(predictions, 0, 10)
        
        # Exclude rated animes
        if exclude_rated:
            predictions[rated_animes] = 0
        
        # Get top N
        top_n_indices = np.argsort(predictions)[-n:][::-1]
        
        result = []
        for idx in top_n_indices:
            if predictions[idx] > 0:
                anime_id = self.reverse_anime_map[idx]
                result.append((anime_id, float(predictions[idx])))
        
        return result
    
    def get_similar_animes(self, anime_id: int, n: int = 10) -> List[Tuple[int, float]]:
        """
        Get similar animes based on item similarity
        
        Args:
            anime_id: Target anime ID
            n: Number of similar animes to return
            
        Returns:
            List of (anime_id, similarity_score) tuples
        """
        if anime_id not in self.anime_id_map:
            return []
        
        anime_idx = self.anime_id_map[anime_id]
        
        # Get similarity scores
        similarities = self.item_similarity[anime_idx].toarray().flatten()
        
        # Exclude self
        similarities[anime_idx] = -1
        
        # Get top N
        top_indices = np.argsort(similarities)[-n:][::-1]
        
        result = []
        for idx in top_indices:
            if similarities[idx] > 0:
                sim_anime_id = self.reverse_anime_map[idx]
                result.append((sim_anime_id, float(similarities[idx])))
        
        return result
    
    def save(self, filepath: str):
        """Save model to file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'k_similar': self.k_similar,
                'similarity_metric': self.similarity_metric,
                'user_item_matrix': self.user_item_matrix,
                'item_similarity': self.item_similarity,
                'user_means': self.user_means,
                'user_id_map': self.user_id_map,
                'anime_id_map': self.anime_id_map,
                'reverse_user_map': self.reverse_user_map,
                'reverse_anime_map': self.reverse_anime_map
            }, f)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'ItemBasedCF':
        """Load model from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        model = cls(
            k_similar=data['k_similar'],
            similarity=data['similarity_metric']
        )
        model.user_item_matrix = data['user_item_matrix']
        model.item_similarity = data['item_similarity']
        model.user_means = data['user_means']
        model.user_id_map = data['user_id_map']
        model.anime_id_map = data['anime_id_map']
        model.reverse_user_map = data['reverse_user_map']
        model.reverse_anime_map = data['reverse_anime_map']
        
        print(f"Model loaded from {filepath}")
        return model
