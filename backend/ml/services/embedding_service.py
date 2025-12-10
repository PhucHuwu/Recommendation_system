"""
Embedding Service

Generate vector embeddings for anime using sentence-transformers.
Embeddings are created from anime synopsis and genres for semantic search.
"""

import os
import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
import pickle
from pathlib import Path


class EmbeddingService:
    """Service for generating and managing anime embeddings"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',
                 cache_dir: Optional[str] = None):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the sentence-transformers model to use
            cache_dir: Directory to cache the model (optional)
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")
        
    def create_anime_text(self, anime: Dict) -> str:
        """
        Create searchable text from anime metadata
        
        Combines name, synopsis, and genres into a single text string
        for embedding generation.
        
        Args:
            anime: Anime dictionary with keys: name, synopsis, genres
            
        Returns:
            Combined text string
        """
        name = anime.get('name', '')
        synopsis = anime.get('synopsis', '')
        genres = anime.get('genres', '')
        
        # Combine fields with appropriate weighting
        # Name is repeated to give it more weight in similarity
        text_parts = []
        
        if name:
            text_parts.append(f"Title: {name}")
            text_parts.append(name)  # Repeat for emphasis
            
        if genres:
            text_parts.append(f"Genres: {genres}")
            
        if synopsis:
            text_parts.append(f"Synopsis: {synopsis}")
        
        return " ".join(text_parts)
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for a single text
        
        Args:
            text: Input text string
            
        Returns:
            Embedding vector as numpy array
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str], 
                                  batch_size: int = 32,
                                  show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar
            
        Returns:
            2D numpy array of embeddings (n_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings
    
    def generate_anime_embeddings(self, animes: List[Dict],
                                 batch_size: int = 32,
                                 show_progress: bool = True) -> Tuple[np.ndarray, List[int]]:
        """
        Generate embeddings for a list of anime
        
        Args:
            animes: List of anime dictionaries
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            
        Returns:
            Tuple of (embeddings array, anime_ids list)
        """
        print(f"Generating embeddings for {len(animes)} anime...")
        
        # Create text representations
        texts = [self.create_anime_text(anime) for anime in animes]
        anime_ids = [anime['mal_id'] for anime in animes]
        
        # Generate embeddings in batches
        embeddings = self.generate_embeddings_batch(
            texts, 
            batch_size=batch_size,
            show_progress=show_progress
        )
        
        print(f"Generated {len(embeddings)} embeddings")
        return embeddings, anime_ids
    
    def save_embeddings(self, embeddings: np.ndarray, 
                       anime_ids: List[int],
                       filepath: str):
        """
        Save embeddings and anime IDs to file
        
        Args:
            embeddings: Embedding vectors array
            anime_ids: List of anime IDs
            filepath: Path to save file
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'embeddings': embeddings,
            'anime_ids': anime_ids,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Saved embeddings to {filepath}")
        print(f"  - {len(anime_ids)} anime")
        print(f"  - {embeddings.shape[1]} dimensions")
        print(f"  - {os.path.getsize(filepath) / 1024 / 1024:.2f} MB")
    
    @staticmethod
    def load_embeddings(filepath: str) -> Tuple[np.ndarray, List[int], Dict]:
        """
        Load embeddings from file
        
        Args:
            filepath: Path to embeddings file
            
        Returns:
            Tuple of (embeddings, anime_ids, metadata)
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        embeddings = data['embeddings']
        anime_ids = data['anime_ids']
        metadata = {
            'model_name': data.get('model_name'),
            'embedding_dim': data.get('embedding_dim')
        }
        
        print(f"Loaded embeddings from {filepath}")
        print(f"  - {len(anime_ids)} anime")
        print(f"  - {embeddings.shape[1]} dimensions")
        
        return embeddings, anime_ids, metadata


# Singleton instance for reuse
_embedding_service_instance: Optional[EmbeddingService] = None


def get_embedding_service(model_name: str = 'sentence-transformers/all-MiniLM-L6-v2') -> EmbeddingService:
    """
    Get or create singleton embedding service instance
    
    Args:
        model_name: Model name for the service
        
    Returns:
        EmbeddingService instance
    """
    global _embedding_service_instance
    
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService(model_name=model_name)
    
    return _embedding_service_instance
