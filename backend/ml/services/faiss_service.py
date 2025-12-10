"""
FAISS Service

Manage FAISS index for vector similarity search on anime embeddings.
Supports building index, searching for similar anime, and save/load functionality.
"""

import os
import numpy as np
import faiss
from typing import List, Tuple, Optional, Dict
import pickle
from pathlib import Path


class FAISSService:
    """Service for managing FAISS vector search index"""
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize FAISS service
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.index: Optional[faiss.Index] = None
        self.anime_ids: List[int] = []
        self.id_to_idx: Dict[int, int] = {}  # Map anime_id to index position
        
    def build_index(self, embeddings: np.ndarray, anime_ids: List[int],
                   index_type: str = 'flat'):
        """
        Build FAISS index from embeddings
        
        Args:
            embeddings: Numpy array of shape (n_samples, embedding_dim)
            anime_ids: List of anime IDs corresponding to embeddings
            index_type: Type of FAISS index ('flat' or 'ivf')
        """
        if len(embeddings) != len(anime_ids):
            raise ValueError(f"Embeddings and anime_ids length mismatch: "
                           f"{len(embeddings)} vs {len(anime_ids)}")
        
        print(f"Building FAISS index with {len(embeddings)} vectors...")
        
        # Ensure embeddings are float32 (required by FAISS)
        embeddings = embeddings.astype('float32')
        
        if index_type == 'flat':
            # IndexFlatL2 - exact search using L2 distance
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        elif index_type == 'ivf':
            # IndexIVFFlat - faster approximate search
            # Use sqrt(n) clusters as a rule of thumb
            n_clusters = min(int(np.sqrt(len(embeddings))), 100)
            quantizer = faiss.IndexFlatL2(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, n_clusters)
            # Train the index
            print(f"Training IVF index with {n_clusters} clusters...")
            self.index.train(embeddings)
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        # Add vectors to index
        self.index.add(embeddings)
        
        # Store anime IDs mapping
        self.anime_ids = anime_ids
        self.id_to_idx = {anime_id: idx for idx, anime_id in enumerate(anime_ids)}
        
        print(f"Index built successfully:")
        print(f"  - Index type: {index_type}")
        print(f"  - Total vectors: {self.index.ntotal}")
        print(f"  - Dimension: {self.embedding_dim}")
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[Tuple[int, float]]:
        """
        Search for k most similar anime
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (anime_id, distance) tuples, sorted by similarity
        """
        if self.index is None:
            raise RuntimeError("Index not built yet. Call build_index() first.")
        
        # Ensure query is 2D array with float32
        query_vector = np.array(query_vector, dtype='float32')
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_vector, k)
        
        # Convert to (anime_id, distance) tuples
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.anime_ids):  # Valid index
                anime_id = self.anime_ids[idx]
                # Convert L2 distance to similarity score (lower is better)
                # We'll use negative distance so higher score = more similar
                similarity = float(-dist)
                results.append((anime_id, similarity))
        
        return results
    
    def search_by_id(self, anime_id: int, k: int = 10, 
                    exclude_self: bool = True) -> List[Tuple[int, float]]:
        """
        Find similar anime to a given anime
        
        Args:
            anime_id: ID of the anime to find similar ones for
            k: Number of results to return
            exclude_self: Whether to exclude the query anime from results
            
        Returns:
            List of (anime_id, similarity) tuples
        """
        if anime_id not in self.id_to_idx:
            raise ValueError(f"Anime ID {anime_id} not found in index")
        
        # Get the embedding vector for this anime
        idx = self.id_to_idx[anime_id]
        
        # Reconstruct the vector from index
        # For IndexFlatL2, we can access vectors directly
        if isinstance(self.index, faiss.IndexFlatL2):
            vector = faiss.rev_swig_ptr(self.index.get_xb(), self.index.ntotal * self.embedding_dim)
            vector = np.array(vector).reshape(self.index.ntotal, self.embedding_dim)
            query_vector = vector[idx:idx+1]
        else:
            raise NotImplementedError("Getting vector from this index type not supported")
        
        # Search for similar, getting k+1 to account for self
        results = self.search(query_vector, k=k+1 if exclude_self else k)
        
        # Remove self if requested
        if exclude_self:
            results = [(aid, sim) for aid, sim in results if aid != anime_id][:k]
        
        return results
    
    def save(self, filepath: str):
        """
        Save FAISS index and metadata to file
        
        Args:
            filepath: Path to save index
        """
        if self.index is None:
            raise RuntimeError("No index to save")
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = filepath
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        meta_path = filepath + '.meta'
        metadata = {
            'anime_ids': self.anime_ids,
            'id_to_idx': self.id_to_idx,
            'embedding_dim': self.embedding_dim
        }
        
        with open(meta_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"Saved FAISS index to {filepath}")
        print(f"  - Index size: {os.path.getsize(index_path) / 1024 / 1024:.2f} MB")
        print(f"  - Metadata size: {os.path.getsize(meta_path) / 1024:.2f} KB")
    
    def load(self, filepath: str):
        """
        Load FAISS index and metadata from file
        
        Args:
            filepath: Path to index file
        """
        # Load FAISS index
        self.index = faiss.read_index(filepath)
        
        # Load metadata
        meta_path = filepath + '.meta'
        with open(meta_path, 'rb') as f:
            metadata = pickle.load(f)
        
        self.anime_ids = metadata['anime_ids']
        self.id_to_idx = metadata['id_to_idx']
        self.embedding_dim = metadata['embedding_dim']
        
        print(f"Loaded FAISS index from {filepath}")
        print(f"  - Total vectors: {self.index.ntotal}")
        print(f"  - Dimension: {self.embedding_dim}")
        print(f"  - Anime count: {len(self.anime_ids)}")
    
    def get_stats(self) -> Dict:
        """
        Get index statistics
        
        Returns:
            Dictionary with index statistics
        """
        if self.index is None:
            return {'status': 'not_built'}
        
        return {
            'status': 'ready',
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.embedding_dim,
            'anime_count': len(self.anime_ids),
            'index_type': type(self.index).__name__
        }


# Singleton instance
_faiss_service_instance: Optional[FAISSService] = None


def get_faiss_service(embedding_dim: int = 384) -> FAISSService:
    """
    Get or create singleton FAISS service instance
    
    Args:
        embedding_dim: Embedding dimension
        
    Returns:
        FAISSService instance
    """
    global _faiss_service_instance
    
    if _faiss_service_instance is None:
        _faiss_service_instance = FAISSService(embedding_dim=embedding_dim)
    
    return _faiss_service_instance
