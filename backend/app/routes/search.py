"""
Search Routes - Vector Search API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
import os
import numpy as np

# Import ML services
from ml.services.embedding_service import EmbeddingService
from ml.services.faiss_service import FAISSService

search_bp = Blueprint('search', __name__)

# ========================= K VALUE RECOMMENDATIONS =========================
# Vector search: K = 20-30 (exploration mode, higher recall)
# Similar anime: K = 6-12 (quality focused)
# ===========================================================================
DEFAULT_K_VECTOR_SEARCH = 20   # Default for vector search (exploration)
DEFAULT_K_SIMILAR = 12         # Default for similar anime
MAX_K_LIMIT = 50               # Maximum allowed K

# Global services (lazy loaded)
_embedding_service = None
_faiss_service = None


def get_embedding_service():
    """Get or create embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        model_name = os.getenv('EMBEDDING_MODEL', 
                               'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        _embedding_service = EmbeddingService(model_name=model_name)
    return _embedding_service


def get_faiss_service():
    """Get or create FAISS service singleton"""
    global _faiss_service
    if _faiss_service is None:
        index_path = os.getenv('FAISS_INDEX_PATH', 'ml/saved_models/faiss_index.bin')
        embedding_dim = int(os.getenv('EMBEDDING_DIM', 384))
        
        _faiss_service = FAISSService(embedding_dim=embedding_dim)
        
        # Load index if exists
        if os.path.exists(index_path):
            _faiss_service.load(index_path)
        else:
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. "
                f"Please run scripts/build_faiss_index.py first."
            )
    
    return _faiss_service


@search_bp.route('/vector', methods=['POST'])
def vector_search():
    """
    Search anime by query text using vector similarity
    
    Request body:
        {
            "query": str,      # Search query in Vietnamese or English
            "limit": int       # Number of results (default: 10, max: 50)
        }
    
    Returns:
        {
            "animes": [...],   # List of matching anime with details
            "count": int,      # Number of results
            "query": str       # Original query
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data['query'].strip()
        if not query or len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400
        
        limit = data.get('limit', DEFAULT_K_VECTOR_SEARCH)
        limit = min(limit, MAX_K_LIMIT)  # Cap at max
        
        # Get services
        embedding_service = get_embedding_service()
        faiss_service = get_faiss_service()
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)
        
        # Search in FAISS
        anime_ids, distances = faiss_service.search(query_embedding, k=limit)
        
        # Get anime details from MongoDB
        db = get_db()
        animes = []
        
        for anime_id, distance in zip(anime_ids, distances):
            anime = db.animes.find_one({'mal_id': anime_id}, {'_id': 0})
            if anime:
                # Add similarity score (convert distance to similarity)
                # Lower distance = higher similarity
                anime['similarity_score'] = float(1 / (1 + distance))
                anime['distance'] = float(distance)
                animes.append(anime)
        
        return jsonify({
            'animes': animes,
            'count': len(animes),
            'query': query
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        print(f"Error in vector_search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@search_bp.route('/similar/<int:anime_id>', methods=['GET'])
def find_similar(anime_id):
    """
    Find similar anime based on another anime
    
    URL params:
        anime_id: int      # ID of the anime to find similar ones for
    
    Query params:
        limit: int         # Number of results (default: 10, max: 50)
    
    Returns:
        {
            "base_anime": {...},      # The source anime
            "similar_animes": [...],  # List of similar anime
            "count": int              # Number of results
        }
    """
    try:
        limit = request.args.get('limit', DEFAULT_K_SIMILAR, type=int)
        limit = min(limit, MAX_K_LIMIT)
        
        db = get_db()
        
        # Get base anime
        base_anime = db.animes.find_one({'mal_id': anime_id}, {'_id': 0})
        if not base_anime:
            return jsonify({'error': 'Anime not found'}), 404
        
        # Get services
        embedding_service = get_embedding_service()
        faiss_service = get_faiss_service()
        
        # Create text representation and generate embedding
        anime_text = embedding_service.create_anime_text(base_anime)
        query_embedding = embedding_service.generate_embedding(anime_text)
        
        # Search in FAISS (k+1 because result will include the anime itself)
        anime_ids, distances = faiss_service.search(query_embedding, k=limit + 1)
        
        # Get similar anime details (excluding the base anime)
        similar_animes = []
        
        for aid, distance in zip(anime_ids, distances):
            if aid == anime_id:
                continue  # Skip the base anime itself
            
            anime = db.animes.find_one({'mal_id': aid}, {'_id': 0})
            if anime:
                anime['similarity_score'] = float(1 / (1 + distance))
                anime['distance'] = float(distance)
                similar_animes.append(anime)
            
            if len(similar_animes) >= limit:
                break
        
        return jsonify({
            'base_anime': base_anime,
            'similar_animes': similar_animes,
            'count': len(similar_animes)
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        print(f"Error in find_similar: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@search_bp.route('/status', methods=['GET'])
def search_status():
    """
    Get status of vector search service
    
    Returns:
        {
            "status": str,           # "ready" or "not_ready"
            "index_stats": {...},    # FAISS index statistics
            "model_info": {...}      # Embedding model information
        }
    """
    try:
        embedding_service = get_embedding_service()
        faiss_service = get_faiss_service()
        
        return jsonify({
            'status': 'ready',
            'index_stats': faiss_service.get_stats(),
            'model_info': {
                'model_name': embedding_service.model_name,
                'embedding_dim': embedding_service.embedding_dim
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e)
        }), 503
