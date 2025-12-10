"""
Embedding Service for Anime Vector Search

This service generates vector embeddings using sentence-transformers
to enable semantic search across anime content (synopsis + genres).
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Optional
import pickle
import os


class EmbeddingService:
    """Service to generate and manage vector embeddings for anime"""
    
    def __init__(self, model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initialize embedding service
        
        Args:
            model_name: Name of the sentence-transformer model to use
                       Default: paraphrase-multilingual-MiniLM-L12-v2 (supports Vietnamese)
        """
        print(f"Loading embedding model: {model_name}")
        
        import torch
        import os
        
        # Workaround for meta tensor error with torch >= 2.9
        # Disable meta device initialization
        os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
        
        # Determine device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        try:
            # First try normal loading
            self.model = SentenceTransformer(
                model_name,
                device=device,
                trust_remote_code=True
            )
        except NotImplementedError as e:
            if "meta tensor" in str(e):
                print("Meta tensor error detected, trying alternative loading method...")
                # Alternative: Load without device first, then move
                from transformers import AutoTokenizer, AutoModel
                
                # Load tokenizer and model separately
                self.model = SentenceTransformer(model_name, device='cpu')
                if device == 'cuda':
                    self.model = self.model.to(device)
            else:
                raise e
        
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded on {device}. Embedding dimension: {self.embedding_dim}")
        
    def create_anime_text(self, anime: Dict) -> str:
        """
        Create searchable text from anime metadata
        
        Combines synopsis and genres to create rich text representation
        that captures both content and categorization.
        
        Args:
            anime: Anime document with fields: name, synopsis, genres
            
        Returns:
            Combined text string for embedding
        """
        parts = []
        
        # Add name
        if anime.get('name'):
            parts.append(f"Tên: {anime['name']}")
        
        # Add genres (important for categorization)
        if anime.get('genres'):
            genres = anime['genres']
            if isinstance(genres, str):
                parts.append(f"Thể loại: {genres}")
        
        # Add synopsis (main content for semantic matching)
        if anime.get('synopsis'):
            synopsis = anime['synopsis'].strip()
            if synopsis and synopsis != 'Unknown':
                parts.append(f"Nội dung: {synopsis}")
        
        # Fallback if no meaningful content
        if not parts:
            return anime.get('name', f"Anime {anime.get('mal_id', 'Unknown')}")
        
        return " | ".join(parts)
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array of embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32, 
                                   show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar
            
        Returns:
            2D numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.embedding_dim)
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings.astype(np.float32)
    
    def generate_anime_embeddings(self, animes: List[Dict], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of anime documents
        
        Args:
            animes: List of anime documents
            batch_size: Batch size for processing
            
        Returns:
            2D numpy array of embeddings
        """
        print(f"Generating embeddings for {len(animes)} animes...")
        
        # Create text representations
        texts = [self.create_anime_text(anime) for anime in animes]
        
        # Generate embeddings in batches
        embeddings = self.generate_embeddings_batch(texts, batch_size=batch_size)
        
        print(f"Generated {len(embeddings)} embeddings of dimension {self.embedding_dim}")
        return embeddings
    
    def save_embeddings(self, embeddings: np.ndarray, anime_ids: List[int], 
                        filepath: str):
        """
        Save embeddings and corresponding anime IDs to file
        
        Args:
            embeddings: 2D array of embeddings
            anime_ids: List of anime IDs (mal_id)
            filepath: Path to save file
        """
        data = {
            'embeddings': embeddings,
            'anime_ids': anime_ids,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Saved embeddings to {filepath}")
        print(f"  - Embeddings shape: {embeddings.shape}")
        print(f"  - Anime IDs: {len(anime_ids)}")
    
    @staticmethod
    def load_embeddings(filepath: str) -> Dict:
        """
        Load embeddings from file
        
        Args:
            filepath: Path to embeddings file
            
        Returns:
            Dict with keys: embeddings, anime_ids, model_name, embedding_dim
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        print(f"Loaded embeddings from {filepath}")
        print(f"  - Model: {data['model_name']}")
        print(f"  - Embeddings shape: {data['embeddings'].shape}")
        print(f"  - Anime IDs: {len(data['anime_ids'])}")
        
        return data
