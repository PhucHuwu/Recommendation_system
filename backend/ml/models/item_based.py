"""
Item-Based Collaborative Filtering

Gợi ý anime dựa trên sự tương đồng giữa các anime.
Sử dụng Cosine Similarity trên rating matrix.
"""

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from typing import List, Tuple


class ItemBasedCF:
    """Item-Based Collaborative Filtering Model"""
    
    def __init__(self, k_similar: int = 30):
        """
        Initialize Item-Based CF
        
        Args:
            k_similar: Number of similar items to consider
        """
        self.k_similar = k_similar
        self.item_similarity = None
        self.user_item_matrix = None
        self.user_id_map = {}
        self.anime_id_map = {}
        self.reverse_anime_map = {}
        
    def fit(self, ratings_data: List[dict]):
        """
        Train the model with rating data
        
        Args:
            ratings_data: List of rating dicts with keys: user_id, anime_id, rating
        """
        print("Training Item-Based CF...")
        
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
        
        # Compute item similarity (transpose matrix for item-item similarities)
        print("  Computing item similarity...")
        self.item_similarity = cosine_similarity(self.user_item_matrix.T, dense_output=False)
        
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
        
        # Get animes rated by this user
        rated_animes = self.user_item_matrix[user_idx].nonzero()[1]
        
        if len(rated_animes) == 0:
            return 0.0
        
        # Get similarity between target anime and rated animes
        item_sims = self.item_similarity[anime_idx, rated_animes].toarray().flatten()
        
        # Get ratings for rated animes
        user_ratings = self.user_item_matrix[user_idx, rated_animes].toarray().flatten()
        
        # Get top k similar items
        if len(item_sims) > self.k_similar:
            top_k_indices = np.argsort(item_sims)[-self.k_similar:]
            item_sims = item_sims[top_k_indices]
            user_ratings = user_ratings[top_k_indices]
        
        # Filter out non-positive similarities
        positive_mask = item_sims > 0
        if not positive_mask.any():
            return 0.0
        
        item_sims = item_sims[positive_mask]
        user_ratings = user_ratings[positive_mask]
        
        # Weighted average
        if item_sims.sum() == 0:
            return 0.0
        
        predicted_rating = np.dot(item_sims, user_ratings) / item_sims.sum()
        
        # Clip to 1-10 range
        return np.clip(predicted_rating, 1, 10)
    
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
        
        # Get top n similar animes (excluding itself)
        similarities[anime_idx] = -1  # Exclude self
        top_indices = np.argsort(similarities)[-n:][::-1]
        
        result = []
        for idx in top_indices:
            if similarities[idx] > 0:
                result.append((self.reverse_anime_map[idx], float(similarities[idx])))
        
        return result
    
    def recommend(self, user_id: int, n: int = 10, exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        Recommend top N animes for a user
        
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
        
        # Get animes not rated by user
        if exclude_rated:
            rated_animes = self.user_item_matrix[user_idx].nonzero()[1]
            candidate_animes = [i for i in range(self.user_item_matrix.shape[1]) if i not in rated_animes]
        else:
            candidate_animes = list(range(self.user_item_matrix.shape[1]))
        
        if not candidate_animes:
            return []
        
        # Predict ratings for all candidates
        predictions = []
        for anime_idx in candidate_animes:
            anime_id = self.reverse_anime_map[anime_idx]
            pred_rating = self.predict(user_id, anime_id)
            if pred_rating > 0:
                predictions.append((anime_id, pred_rating))
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:n]
    
    def save(self, filepath: str):
        """Save model to file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'k_similar': self.k_similar,
                'item_similarity': self.item_similarity,
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
        
        model = cls(k_similar=data['k_similar'])
        model.item_similarity = data['item_similarity']
        model.user_item_matrix = data['user_item_matrix']
        model.user_id_map = data['user_id_map']
        model.anime_id_map = data['anime_id_map']
        model.reverse_anime_map = data['reverse_anime_map']
        
        print(f"Model loaded from {filepath}")
        return model
