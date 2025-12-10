"""
FAISS Service for Vector Similarity Search

This service manages FAISS index for fast similarity search
across anime embeddings.
"""

import faiss
import numpy as np
from typing import List, Tuple, Optional
import pickle
import os


class FAISSService:
    """Service to build and query FAISS index for anime search"""
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize FAISS service
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.index = None
        self.anime_ids = None
        self.is_trained = False
        
    def build_index(self, embeddings: np.ndarray, anime_ids: List[int], 
                    index_type: str = 'flat'):
        """
        Build FAISS index from embeddings
        
        Args:
            embeddings: 2D numpy array of shape (n_animes, embedding_dim)
            anime_ids: List of anime IDs corresponding to embeddings
            index_type: Type of FAISS index ('flat' or 'ivf')
        """
        n_vectors = embeddings.shape[0]
        
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                           f"got {embeddings.shape[1]}")
        
        print(f"Building FAISS index for {n_vectors} vectors...")
        
        if index_type == 'flat':
            # IndexFlatL2: Exact search using L2 distance
            # Best for smaller datasets (< 1M vectors)
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            
        elif index_type == 'ivf':
            # IndexIVFFlat: Faster approximate search
            # Good for larger datasets
            n_list = min(100, n_vectors // 10)  # Number of clusters
            quantizer = faiss.IndexFlatL2(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, n_list)
            
            # IVF index needs training
            print(f"Training IVF index with {n_list} clusters...")
            self.index.train(embeddings)
            self.is_trained = True
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        # Add vectors to index
        self.index.add(embeddings)
        self.anime_ids = anime_ids
        
        print(f"Index built successfully")
        print(f"  - Index type: {index_type}")
        print(f"  - Total vectors: {self.index.ntotal}")
        print(f"  - Is trained: {self.is_trained}")
    
    def search(self, query_embedding: np.ndarray, k: int = 10) -> Tuple[List[int], List[float]]:
        """
        Search for k most similar anime
        
        Args:
            query_embedding: Query vector of shape (embedding_dim,) or (1, embedding_dim)
            k: Number of results to return
            
        Returns:
            Tuple of (anime_ids, distances)
        """
        if self.index is None:
            raise ValueError("Index not built yet. Call build_index() first.")
        
        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Ensure float32 type
        query_embedding = query_embedding.astype(np.float32)
        
        # Search
        k = min(k, self.index.ntotal)  # Can't return more than total vectors
        distances, indices = self.index.search(query_embedding, k)
        
        # Convert to lists
        distances = distances[0].tolist()
        indices = indices[0].tolist()
        
        # Map indices to anime IDs
        result_anime_ids = [self.anime_ids[idx] for idx in indices if idx != -1]
        result_distances = [dist for idx, dist in zip(indices, distances) if idx != -1]
        
        return result_anime_ids, result_distances
    
    def search_batch(self, query_embeddings: np.ndarray, k: int = 10) -> Tuple[List[List[int]], List[List[float]]]:
        """
        Search for multiple queries at once
        
        Args:
            query_embeddings: 2D array of query vectors (n_queries, embedding_dim)
            k: Number of results per query
            
        Returns:
            Tuple of (list of anime_ids lists, list of distances lists)
        """
        if self.index is None:
            raise ValueError("Index not built yet. Call build_index() first.")
        
        # Ensure float32 type
        query_embeddings = query_embeddings.astype(np.float32)
        
        # Search
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embeddings, k)
        
        # Convert to lists of lists
        result_anime_ids = []
        result_distances = []
        
        for i in range(len(query_embeddings)):
            anime_ids = [self.anime_ids[idx] for idx in indices[i] if idx != -1]
            dists = [dist for idx, dist in zip(indices[i], distances[i]) if idx != -1]
            result_anime_ids.append(anime_ids)
            result_distances.append(dists)
        
        return result_anime_ids, result_distances
    
    def save(self, filepath: str):
        """
        Save FAISS index to file
        
        Args:
            filepath: Path to save index
        """
        if self.index is None:
            raise ValueError("No index to save")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save index
        faiss.write_index(self.index, filepath)
        
        # Save metadata
        metadata_path = filepath + '.meta'
        metadata = {
            'anime_ids': self.anime_ids,
            'embedding_dim': self.embedding_dim,
            'is_trained': self.is_trained,
            'ntotal': self.index.ntotal
        }
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"Saved FAISS index to {filepath}")
        print(f"  - Total vectors: {self.index.ntotal}")
    
    def load(self, filepath: str):
        """
        Load FAISS index from file
        
        Args:
            filepath: Path to index file
        """
        # Load index
        self.index = faiss.read_index(filepath)
        
        # Load metadata
        metadata_path = filepath + '.meta'
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        self.anime_ids = metadata['anime_ids']
        self.embedding_dim = metadata['embedding_dim']
        self.is_trained = metadata.get('is_trained', False)
        
        print(f"Loaded FAISS index from {filepath}")
        print(f"  - Total vectors: {self.index.ntotal}")
        print(f"  - Embedding dim: {self.embedding_dim}")
        print(f"  - Is trained: {self.is_trained}")
    
    def get_stats(self) -> dict:
        """Get statistics about the index"""
        if self.index is None:
            return {'status': 'not_built'}
        
        return {
            'status': 'ready',
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.embedding_dim,
            'is_trained': self.is_trained,
            'total_anime': len(self.anime_ids) if self.anime_ids else 0
        }
