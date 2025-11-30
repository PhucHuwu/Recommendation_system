"""
Content-Based Recommendation System

This module implements content-based filtering using movie features
like genres, TF-IDF vectors, and other metadata.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os


class ContentBasedRecommender:
    """
    Content-based recommender using movie features.
    
    Attributes:
        movies (pd.DataFrame): Movies dataset with features
        similarity_matrix (np.ndarray): Cosine similarity matrix
        feature_matrix (np.ndarray): Feature vectors for movies
        movie_indices (dict): Mapping from movieId to index
    """
    
    def __init__(self, verbose=True):
        """
        Initialize the recommender.
        
        Args:
            verbose (bool): Print progress messages
        """
        self.verbose = verbose
        self.movies = None
        self.similarity_matrix = None
        self.feature_matrix = None
        self.movie_indices = None
        self.index_to_movieId = None
        
    def _log(self, message):
        """Print message if verbose mode is on."""
        if self.verbose:
            print(message)
    
    def load_data(self, movies_path, tfidf_path=None):
        """
        Load movies data and optional TF-IDF matrix.
        
        Args:
            movies_path (str): Path to movies CSV
            tfidf_path (str): Optional path to TF-IDF pickle
            
        Returns:
            self: For method chaining
        """
        self._log("Loading data...")
        self.movies = pd.read_csv(movies_path)
        
        # Create movie index mapping
        self.movie_indices = {movieId: idx for idx, movieId in enumerate(self.movies['movieId'])}
        self.index_to_movieId = {idx: movieId for movieId, idx in self.movie_indices.items()}
        
        self._log(f"Loaded {len(self.movies)} movies")
        
        # Load TF-IDF if provided
        if tfidf_path and os.path.exists(tfidf_path):
            with open(tfidf_path, 'rb') as f:
                tfidf_data = pickle.load(f)
                self.feature_matrix = tfidf_data['matrix']
            self._log(f"Loaded TF-IDF matrix: {self.feature_matrix.shape}")
        
        return self
    
    def build_tfidf_features(self, text_column='combined_features'):
        """
        Build TF-IDF feature matrix from text column.
        
        Args:
            text_column (str): Column name containing text features
            
        Returns:
            self: For method chaining
        """
        self._log(f"Building TF-IDF features from '{text_column}'...")
        
        vectorizer = TfidfVectorizer(
            max_features=200,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        texts = self.movies[text_column].fillna('')
        self.feature_matrix = vectorizer.fit_transform(texts)
        
        self._log(f"TF-IDF matrix shape: {self.feature_matrix.shape}")
        return self
    
    def build_genre_features(self):
        """
        Build feature matrix from binary genre columns.
        
        Returns:
            self: For method chaining
        """
        self._log("Building genre-based features...")
        
        genre_cols = [col for col in self.movies.columns if col.startswith('is_')]
        
        if len(genre_cols) == 0:
            raise ValueError("No genre columns found (columns starting with 'is_')")
        
        self.feature_matrix = self.movies[genre_cols].values
        self._log(f"Genre feature matrix shape: {self.feature_matrix.shape}")
        
        return self
    
    def build_combined_features(self, numeric_cols=None, genre_weight=1.0, numeric_weight=1.0):
        """
        Build combined feature matrix from genres and numeric features.
        
        Args:
            numeric_cols (list): List of numeric column names
            genre_weight (float): Weight for genre features
            numeric_weight (float): Weight for numeric features
            
        Returns:
            self: For method chaining
        """
        self._log("Building combined features...")
        
        # Genre features
        genre_cols = [col for col in self.movies.columns if col.startswith('is_')]
        genre_features = self.movies[genre_cols].values * genre_weight
        
        # Numeric features
        if numeric_cols is None:
            numeric_cols = ['year', 'avg_rating', 'popularity', 'genres_count']
        
        # Normalize numeric features to 0-1 range
        numeric_features = self.movies[numeric_cols].fillna(0).values
        numeric_features = (numeric_features - numeric_features.min(axis=0)) / \
                          (numeric_features.max(axis=0) - numeric_features.min(axis=0) + 1e-8)
        numeric_features = numeric_features * numeric_weight
        
        # Combine
        self.feature_matrix = np.hstack([genre_features, numeric_features])
        
        self._log(f"Combined feature matrix shape: {self.feature_matrix.shape}")
        return self
    
    def compute_similarity(self, metric='cosine'):
        """
        Compute similarity matrix between all movies.
        
        Args:
            metric (str): Similarity metric ('cosine' supported)
            
        Returns:
            self: For method chaining
        """
        if self.feature_matrix is None:
            raise ValueError("Feature matrix not built. Call a build_*_features method first.")
        
        self._log(f"Computing {metric} similarity...")
        
        if metric == 'cosine':
            self.similarity_matrix = cosine_similarity(self.feature_matrix)
        else:
            raise ValueError(f"Metric '{metric}' not supported")
        
        self._log(f"Similarity matrix shape: {self.similarity_matrix.shape}")
        return self
    
    def get_recommendations(self, movie_id, n=10, min_rating_count=10):
        """
        Get top N recommendations for a movie.
        
        Args:
            movie_id (int): MovieLens movie ID
            n (int): Number of recommendations
            min_rating_count (int): Minimum rating count threshold
            
        Returns:
            pd.DataFrame: Recommended movies with similarity scores
        """
        if self.similarity_matrix is None:
            raise ValueError("Similarity matrix not computed. Call compute_similarity() first.")
        
        if movie_id not in self.movie_indices:
            raise ValueError(f"Movie ID {movie_id} not found in dataset")
        
        # Get movie index
        idx = self.movie_indices[movie_id]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        
        # Sort by similarity (descending)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N (excluding the movie itself)
        sim_scores = sim_scores[1:n+100]  # Get more to filter
        
        # Convert to movie IDs and filter
        recommendations = []
        for movie_idx, score in sim_scores:
            movie_id_rec = self.index_to_movieId[movie_idx]
            movie_data = self.movies[self.movies['movieId'] == movie_id_rec].iloc[0]
            
            # Filter by minimum rating count
            if movie_data.get('num_ratings', 0) >= min_rating_count:
                recommendations.append({
                    'movieId': movie_id_rec,
                    'title': movie_data.get('title_clean', movie_data.get('title', '')),
                    'year': movie_data.get('year', 0),
                    'genres': movie_data.get('genres', ''),
                    'avg_rating': movie_data.get('avg_rating', 0),
                    'num_ratings': movie_data.get('num_ratings', 0),
                    'similarity_score': score
                })
                
                if len(recommendations) >= n:
                    break
        
        return pd.DataFrame(recommendations)
    
    def get_recommendations_by_title(self, title, n=10, min_rating_count=10):
        """
        Get recommendations by movie title (partial match).
        
        Args:
            title (str): Movie title (or part of it)
            n (int): Number of recommendations
            min_rating_count (int): Minimum rating count threshold
            
        Returns:
            pd.DataFrame: Recommended movies
        """
        # Find movie by title
        matches = self.movies[
            self.movies['title'].str.contains(title, case=False, na=False) |
            self.movies['title_clean'].str.contains(title, case=False, na=False)
        ]
        
        if len(matches) == 0:
            raise ValueError(f"No movie found matching '{title}'")
        
        if len(matches) > 1:
            self._log(f"Found {len(matches)} matches. Using first one:")
            self._log(f"  {matches.iloc[0]['title']}")
        
        movie_id = matches.iloc[0]['movieId']
        return self.get_recommendations(movie_id, n, min_rating_count)
    
    def save_model(self, path):
        """
        Save the model to disk.
        
        Args:
            path (str): Path to save the model
        """
        model_data = {
            'similarity_matrix': self.similarity_matrix,
            'feature_matrix': self.feature_matrix,
            'movie_indices': self.movie_indices,
            'index_to_movieId': self.index_to_movieId
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        self._log(f"Model saved to {path}")
    
    def load_model(self, path, movies_path):
        """
        Load a saved model from disk.
        
        Args:
            path (str): Path to the saved model
            movies_path (str): Path to movies CSV
            
        Returns:
            self: For method chaining
        """
        self._log("Loading saved model...")
        
        # Load movies data
        self.load_data(movies_path)
        
        # Load model
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.similarity_matrix = model_data['similarity_matrix']
        self.feature_matrix = model_data['feature_matrix']
        self.movie_indices = model_data['movie_indices']
        self.index_to_movieId = model_data['index_to_movieId']
        
        self._log("Model loaded successfully")
        return self


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("CONTENT-BASED RECOMMENDER - EXAMPLE")
    print("=" * 70)
    
    # Initialize
    cb_rec = ContentBasedRecommender(verbose=True)
    
    # Load data
    movies_path = '../data/processed/movies_enriched.csv'
    tfidf_path = '../data/processed/tfidf_matrix.pkl'
    
    cb_rec.load_data(movies_path, tfidf_path)
    
    # Build features (choose one method)
    # Method 1: TF-IDF
    # cb_rec.build_tfidf_features()
    
    # Method 2: Genres only
    # cb_rec.build_genre_features()
    
    # Method 3: Combined features
    cb_rec.build_combined_features()
    
    # Compute similarity
    cb_rec.compute_similarity()
    
    # Get recommendations
    print("\n" + "=" * 70)
    print("GETTING RECOMMENDATIONS")
    print("=" * 70)
    
    test_title = "Toy Story"
    recommendations = cb_rec.get_recommendations_by_title(test_title, n=10)
    
    print(f"\nTop 10 movies similar to '{test_title}':")
    print(recommendations[['title', 'year', 'genres', 'avg_rating', 'similarity_score']])
    
    # Save model
    model_path = '../data/models/content_based_model.pkl'
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    cb_rec.save_model(model_path)
    
    print("\n" + "=" * 70)
    print("CONTENT-BASED RECOMMENDER - COMPLETE")
    print("=" * 70)
