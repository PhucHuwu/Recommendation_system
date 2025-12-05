"""
Content-Based Filtering

Gợi ý anime dựa trên nội dung (genres, synopsis).
Sử dụng TF-IDF cho synopsis và one-hot encoding cho genres.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
import pickle
from typing import List, Tuple


class ContentBasedCF:
    """Content-Based Filtering Model"""
    
    def __init__(self, use_synopsis: bool = True, use_genres: bool = True):
        """
        Initialize Content-Based CF
        
        Args:
            use_synopsis: Whether to use synopsis for similarity
            use_genres: Whether to use genres for similarity
        """
        self.use_synopsis = use_synopsis
        self.use_genres = use_genres
        self.tfidf_vectorizer = None
        self.mlb = None  # MultiLabelBinarizer for genres
        self.content_matrix = None
        self.anime_id_map = {}
        self.reverse_anime_map = {}
        self.anime_features = {}  # Store anime metadata
        
    def fit(self, animes_data: List[dict]):
        """
        Train the model with anime data
        
        Args:
            animes_data: List of anime dicts with keys: mal_id, name, genres, synopsis
        """
        print("Training Content-Based CF...")
        
        # Create mappings
        sorted_animes = sorted(animes_data, key=lambda x: x['mal_id'])
        self.anime_id_map = {a['mal_id']: idx for idx, a in enumerate(sorted_animes)}
        self.reverse_anime_map = {idx: a['mal_id'] for idx, a in enumerate(sorted_animes)}
        
        print(f"  Animes: {len(sorted_animes):,}")
        
        # Store features
        for anime in sorted_animes:
            self.anime_features[anime['mal_id']] = {
                'name': anime.get('name', ''),
                'genres': anime.get('genres', ''),
                'synopsis': anime.get('synopsis', '')
            }
        
        # Build content matrix
        features = []
        
        # Process synopsis with TF-IDF
        if self.use_synopsis:
            print("  Processing synopsis with TF-IDF...")
            synopses = [anime.get('synopsis', '') for anime in sorted_animes]
            
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                min_df=2,
                max_df=0.8
            )
            
            try:
                synopsis_features = self.tfidf_vectorizer.fit_transform(synopses)
                features.append(synopsis_features)
                print(f"    TF-IDF features: {synopsis_features.shape[1]}")
            except Exception as e:
                print(f"    Warning: Could not process synopsis: {e}")
                self.use_synopsis = False
        
        # Process genres with MultiLabelBinarizer
        if self.use_genres:
            print("  Processing genres...")
            genres_list = []
            for anime in sorted_animes:
                genres_str = anime.get('genres', '')
                if genres_str:
                    # Split by comma and strip whitespace
                    genres = [g.strip() for g in genres_str.split(',')]
                    genres_list.append(genres)
                else:
                    genres_list.append([])
            
            self.mlb = MultiLabelBinarizer()
            genre_features = self.mlb.fit_transform(genres_list)
            features.append(genre_features)
            print(f"    Genre features: {len(self.mlb.classes_)} genres")
        
        if not features:
            raise ValueError("No features to use! Enable synopsis or genres.")
        
        # Combine features
        if len(features) == 1:
            self.content_matrix = features[0]
            # Convert to csr_matrix if sparse
            if hasattr(self.content_matrix, 'tocsr'):
                self.content_matrix = self.content_matrix.tocsr()
        else:
            # Combine TF-IDF and genres (with genre weight)
            from scipy.sparse import hstack, csr_matrix
            genre_weight = 0.3  # Weight for genres vs synopsis
            
            if self.use_synopsis and self.use_genres:
                # Weight genres more
                weighted_genres = features[1] * genre_weight
                self.content_matrix = hstack([features[0], weighted_genres]).tocsr()
            else:
                self.content_matrix = hstack(features).tocsr()
        
        print(f"  Content matrix shape: {self.content_matrix.shape}")
        print("  Training complete!")
        
    def get_similar_animes(self, anime_id: int, n: int = 10) -> List[Tuple[int, float]]:
        """
        Get similar animes based on content
        
        Args:
            anime_id: Target anime ID
            n: Number of similar animes to return
            
        Returns:
            List of (anime_id, similarity_score) tuples
        """
        if anime_id not in self.anime_id_map:
            return []
        
        anime_idx = self.anime_id_map[anime_id]
        
        # Compute similarity with all animes
        anime_vector = self.content_matrix[anime_idx]
        similarities = cosine_similarity(anime_vector, self.content_matrix).flatten()
        
        # Get top n similar animes (excluding itself)
        similarities[anime_idx] = -1  # Exclude self
        top_indices = np.argsort(similarities)[-n:][::-1]
        
        result = []
        for idx in top_indices:
            if similarities[idx] > 0:
                result.append((self.reverse_anime_map[idx], float(similarities[idx])))
        
        return result
    
    def recommend_based_on_genres(self, genres: List[str], n: int = 10) -> List[Tuple[int, float]]:
        """
        Recommend animes based on genre preferences
        
        Args:
            genres: List of preferred genres
            n: Number of recommendations
            
        Returns:
            List of (anime_id, score) tuples
        """
        if not self.use_genres or not genres:
            return []
        
        # Create one-hot vector for input genres
        genre_vector = self.mlb.transform([genres])
        
        # Compute similarity with all animes (using only genre features)
        if self.use_synopsis:
            # Extract genre features from content matrix
            # This is simplified - in practice you'd store genre matrix separately
            genre_features = self.content_matrix[:, -len(self.mlb.classes_):]
        else:
            genre_features = self.content_matrix
        
        similarities = cosine_similarity(genre_vector, genre_features).flatten()
        
        # Get top n
        top_indices = np.argsort(similarities)[-n:][::-1]
        
        result = []
        for idx in top_indices:
            if similarities[idx] > 0:
                result.append((self.reverse_anime_map[idx], float(similarities[idx])))
        
        return result
    
    def save(self, filepath: str):
        """Save model to file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'use_synopsis': self.use_synopsis,
                'use_genres': self.use_genres,
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'mlb': self.mlb,
                'content_matrix': self.content_matrix,
                'anime_id_map': self.anime_id_map,
                'reverse_anime_map': self.reverse_anime_map,
                'anime_features': self.anime_features
            }, f)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load model from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        model = cls(use_synopsis=data['use_synopsis'], use_genres=data['use_genres'])
        model.tfidf_vectorizer = data['tfidf_vectorizer']
        model.mlb = data['mlb']
        # Ensure content_matrix is in csr format for indexing
        content_matrix = data['content_matrix']
        if hasattr(content_matrix, 'tocsr'):
            model.content_matrix = content_matrix.tocsr()
        else:
            model.content_matrix = content_matrix
        model.anime_id_map = data['anime_id_map']
        model.reverse_anime_map = data['reverse_anime_map']
        model.anime_features = data['anime_features']
        
        print(f"Model loaded from {filepath}")
        return model
