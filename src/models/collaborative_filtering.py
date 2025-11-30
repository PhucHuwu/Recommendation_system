"""
Collaborative Filtering Recommendation System

This module implements user-based and item-based collaborative filtering
using rating patterns.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import pickle
import os


class CollaborativeFilteringRecommender:
    """
    Collaborative Filtering recommender using rating patterns.
    
    Supports both user-based and item-based approaches.
    
    Attributes:
        ratings (pd.DataFrame): User-item ratings
        movies (pd.DataFrame): Movie metadata
        user_item_matrix (pd.DataFrame): User-item rating matrix
        item_similarity (np.ndarray): Item-item similarity matrix
        user_similarity (np.ndarray): User-user similarity matrix
    """
    
    def __init__(self, approach='item', verbose=True):
        """
        Initialize the recommender.
        
        Args:
            approach (str): 'item' for item-based or 'user' for user-based
            verbose (bool): Print progress messages
        """
        self.approach = approach
        self.verbose = verbose
        self.ratings = None
        self.movies = None
        self.user_item_matrix = None
        self.item_similarity = None
        self.user_similarity = None
        self.movie_id_to_idx = None
        self.idx_to_movie_id = None
        self.user_id_to_idx = None
        self.idx_to_user_id = None
        
    def _log(self, message):
        """Print message if verbose mode is on."""
        if self.verbose:
            print(message)
    
    def load_data(self, ratings_path, movies_path):
        """
        Load ratings and movies data.
        
        Args:
            ratings_path (str): Path to ratings CSV
            movies_path (str): Path to movies CSV
            
        Returns:
            self: For method chaining
        """
        self._log("Loading data...")
        self.ratings = pd.read_csv(ratings_path)
        self.movies = pd.read_csv(movies_path)
        
        self._log(f"Loaded {len(self.ratings)} ratings")
        self._log(f"Loaded {len(self.movies)} movies")
        self._log(f"Users: {self.ratings['userId'].nunique()}")
        self._log(f"Movies: {self.ratings['movieId'].nunique()}")
        
        return self
    
    def build_user_item_matrix(self, min_ratings_per_user=10, min_ratings_per_movie=10):
        """
        Build user-item rating matrix.
        
        Args:
            min_ratings_per_user (int): Minimum ratings required per user
            min_ratings_per_movie (int): Minimum ratings required per movie
            
        Returns:
            self: For method chaining
        """
        self._log("Building user-item matrix...")
        
        # Filter users and movies with enough ratings
        user_counts = self.ratings['userId'].value_counts()
        movie_counts = self.ratings['movieId'].value_counts()
        
        active_users = user_counts[user_counts >= min_ratings_per_user].index
        popular_movies = movie_counts[movie_counts >= min_ratings_per_movie].index
        
        # Filter ratings
        filtered_ratings = self.ratings[
            (self.ratings['userId'].isin(active_users)) &
            (self.ratings['movieId'].isin(popular_movies))
        ]
        
        self._log(f"Filtered to {len(filtered_ratings)} ratings")
        self._log(f"Active users: {len(active_users)}")
        self._log(f"Popular movies: {len(popular_movies)}")
        
        # Create user-item matrix
        self.user_item_matrix = filtered_ratings.pivot_table(
            index='userId',
            columns='movieId',
            values='rating'
        ).fillna(0)
        
        # Create index mappings
        self.movie_id_to_idx = {mid: idx for idx, mid in enumerate(self.user_item_matrix.columns)}
        self.idx_to_movie_id = {idx: mid for mid, idx in self.movie_id_to_idx.items()}
        
        self.user_id_to_idx = {uid: idx for idx, uid in enumerate(self.user_item_matrix.index)}
        self.idx_to_user_id = {idx: uid for uid, idx in self.user_id_to_idx.items()}
        
        self._log(f"User-item matrix shape: {self.user_item_matrix.shape}")
        
        return self
    
    def compute_item_similarity(self, metric='cosine'):
        """
        Compute item-item similarity matrix.
        
        Args:
            metric (str): Similarity metric ('cosine' supported)
            
        Returns:
            self: For method chaining
        """
        if self.user_item_matrix is None:
            raise ValueError("User-item matrix not built. Call build_user_item_matrix() first.")
        
        self._log(f"Computing item-item {metric} similarity...")
        
        if metric == 'cosine':
            # Transpose to get items as rows
            item_features = self.user_item_matrix.T
            self.item_similarity = cosine_similarity(item_features)
        else:
            raise ValueError(f"Metric '{metric}' not supported")
        
        self._log(f"Item similarity matrix shape: {self.item_similarity.shape}")
        
        return self
    
    def compute_user_similarity(self, metric='cosine'):
        """
        Compute user-user similarity matrix.
        
        Args:
            metric (str): Similarity metric ('cosine' supported)
            
        Returns:
            self: For method chaining
        """
        if self.user_item_matrix is None:
            raise ValueError("User-item matrix not built. Call build_user_item_matrix() first.")
        
        self._log(f"Computing user-user {metric} similarity...")
        
        if metric == 'cosine':
            self.user_similarity = cosine_similarity(self.user_item_matrix)
        else:
            raise ValueError(f"Metric '{metric}' not supported")
        
        self._log(f"User similarity matrix shape: {self.user_similarity.shape}")
        
        return self
    
    def fit(self, min_ratings_per_user=10, min_ratings_per_movie=10):
        """
        Fit the collaborative filtering model.
        
        Args:
            min_ratings_per_user (int): Minimum ratings per user
            min_ratings_per_movie (int): Minimum ratings per movie
            
        Returns:
            self: For method chaining
        """
        self.build_user_item_matrix(min_ratings_per_user, min_ratings_per_movie)
        
        if self.approach == 'item':
            self.compute_item_similarity()
        elif self.approach == 'user':
            self.compute_user_similarity()
        else:
            raise ValueError(f"Approach '{self.approach}' not supported. Use 'item' or 'user'.")
        
        return self
    
    def get_item_based_recommendations(self, movie_id, n=10):
        """
        Get item-based recommendations for a movie.
        
        Args:
            movie_id (int): MovieLens movie ID
            n (int): Number of recommendations
            
        Returns:
            pd.DataFrame: Recommended movies with similarity scores
        """
        if self.item_similarity is None:
            raise ValueError("Item similarity not computed. Call compute_item_similarity() first.")
        
        if movie_id not in self.movie_id_to_idx:
            raise ValueError(f"Movie ID {movie_id} not in filtered dataset")
        
        # Get movie index
        idx = self.movie_id_to_idx[movie_id]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.item_similarity[idx]))
        
        # Sort by similarity (descending)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N (excluding the movie itself)
        sim_scores = sim_scores[1:n+1]
        
        # Convert to DataFrame
        recommendations = []
        for movie_idx, score in sim_scores:
            movie_id_rec = self.idx_to_movie_id[movie_idx]
            movie_data = self.movies[self.movies['movieId'] == movie_id_rec]
            
            if len(movie_data) > 0:
                movie_data = movie_data.iloc[0]
                recommendations.append({
                    'movieId': movie_id_rec,
                    'title': movie_data.get('title_clean', movie_data.get('title', '')),
                    'year': movie_data.get('year', 0),
                    'genres': movie_data.get('genres', ''),
                    'avg_rating': movie_data.get('avg_rating', 0),
                    'num_ratings': movie_data.get('num_ratings', 0),
                    'similarity_score': score
                })
        
        return pd.DataFrame(recommendations)
    
    def get_user_based_recommendations(self, user_id, n=10):
        """
        Get user-based recommendations for a user.
        
        Args:
            user_id (int): MovieLens user ID
            n (int): Number of recommendations
            
        Returns:
            pd.DataFrame: Recommended movies with predicted ratings
        """
        if self.user_similarity is None:
            raise ValueError("User similarity not computed. Call compute_user_similarity() first.")
        
        if user_id not in self.user_id_to_idx:
            raise ValueError(f"User ID {user_id} not in filtered dataset")
        
        # Get user index
        user_idx = self.user_id_to_idx[user_id]
        
        # Get similar users
        sim_scores = self.user_similarity[user_idx]
        
        # Get user's ratings
        user_ratings = self.user_item_matrix.iloc[user_idx]
        
        # Predict ratings for unrated movies
        predicted_ratings = {}
        
        for movie_idx in range(len(self.user_item_matrix.columns)):
            movie_id = self.idx_to_movie_id[movie_idx]
            
            # Skip if user already rated
            if user_ratings.iloc[movie_idx] > 0:
                continue
            
            # Calculate weighted average of similar users' ratings
            movie_ratings = self.user_item_matrix.iloc[:, movie_idx]
            
            # Get ratings from users who rated this movie
            rated_mask = movie_ratings > 0
            if rated_mask.sum() == 0:
                continue
            
            # Weighted sum
            numerator = np.sum(sim_scores[rated_mask] * movie_ratings[rated_mask])
            denominator = np.sum(np.abs(sim_scores[rated_mask]))
            
            if denominator > 0:
                predicted_ratings[movie_id] = numerator / denominator
        
        # Sort by predicted rating
        top_movies = sorted(predicted_ratings.items(), key=lambda x: x[1], reverse=True)[:n]
        
        # Convert to DataFrame
        recommendations = []
        for movie_id, pred_rating in top_movies:
            movie_data = self.movies[self.movies['movieId'] == movie_id]
            
            if len(movie_data) > 0:
                movie_data = movie_data.iloc[0]
                recommendations.append({
                    'movieId': movie_id,
                    'title': movie_data.get('title_clean', movie_data.get('title', '')),
                    'year': movie_data.get('year', 0),
                    'genres': movie_data.get('genres', ''),
                    'avg_rating': movie_data.get('avg_rating', 0),
                    'num_ratings': movie_data.get('num_ratings', 0),
                    'predicted_rating': pred_rating
                })
        
        return pd.DataFrame(recommendations)
    
    def get_recommendations(self, identifier, n=10):
        """
        Get recommendations based on approach.
        
        Args:
            identifier (int): Movie ID (item-based) or User ID (user-based)
            n (int): Number of recommendations
            
        Returns:
            pd.DataFrame: Recommended movies
        """
        if self.approach == 'item':
            return self.get_item_based_recommendations(identifier, n)
        elif self.approach == 'user':
            return self.get_user_based_recommendations(identifier, n)
        else:
            raise ValueError(f"Unknown approach: {self.approach}")
    
    def save_model(self, path):
        """
        Save the model to disk.
        
        Args:
            path (str): Path to save the model
        """
        model_data = {
            'approach': self.approach,
            'user_item_matrix': self.user_item_matrix,
            'item_similarity': self.item_similarity,
            'user_similarity': self.user_similarity,
            'movie_id_to_idx': self.movie_id_to_idx,
            'idx_to_movie_id': self.idx_to_movie_id,
            'user_id_to_idx': self.user_id_to_idx,
            'idx_to_user_id': self.idx_to_user_id
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        self._log(f"Model saved to {path}")
    
    def load_model(self, path, ratings_path, movies_path):
        """
        Load a saved model from disk.
        
        Args:
            path (str): Path to the saved model
            ratings_path (str): Path to ratings CSV
            movies_path (str): Path to movies CSV
            
        Returns:
            self: For method chaining
        """
        self._log("Loading saved model...")
        
        # Load data
        self.load_data(ratings_path, movies_path)
        
        # Load model
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.approach = model_data['approach']
        self.user_item_matrix = model_data['user_item_matrix']
        self.item_similarity = model_data['item_similarity']
        self.user_similarity = model_data['user_similarity']
        self.movie_id_to_idx = model_data['movie_id_to_idx']
        self.idx_to_movie_id = model_data['idx_to_movie_id']
        self.user_id_to_idx = model_data['user_id_to_idx']
        self.idx_to_user_id = model_data['idx_to_user_id']
        
        self._log("Model loaded successfully")
        return self


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("COLLABORATIVE FILTERING RECOMMENDER - EXAMPLE")
    print("=" * 70)
    
    # Initialize (item-based)
    cf_rec = CollaborativeFilteringRecommender(approach='item', verbose=True)
    
    # Load data
    ratings_path = '../data/processed/ratings.csv'
    movies_path = '../data/processed/movies_enriched.csv'
    
    cf_rec.load_data(ratings_path, movies_path)
    
    # Fit model
    cf_rec.fit(min_ratings_per_user=20, min_ratings_per_movie=50)
    
    # Get recommendations
    print("\n" + "=" * 70)
    print("GETTING RECOMMENDATIONS")
    print("=" * 70)
    
    # Find a popular movie ID
    toy_story_id = 1  # Toy Story movie ID
    
    try:
        recommendations = cf_rec.get_item_based_recommendations(toy_story_id, n=10)
        print(f"\nTop 10 movies similar to Toy Story (based on user ratings):")
        print(recommendations[['title', 'year', 'genres', 'avg_rating', 'similarity_score']])
    except ValueError as e:
        print(f"Error: {e}")
        print("Note: Movie may not be in filtered dataset.")
    
    # Save model
    model_path = '../data/models/collaborative_filtering_model.pkl'
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    cf_rec.save_model(model_path)
    
    print("\n" + "=" * 70)
    print("COLLABORATIVE FILTERING RECOMMENDER - COMPLETE")
    print("=" * 70)
