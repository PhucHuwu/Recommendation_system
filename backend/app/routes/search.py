"""
Search Routes

API endpoints for vector-based semantic search
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
import os
import sys
from pathlib import Path

# Add ml directory to path for imports
ml_dir = Path(__file__).parent.parent.parent / 'ml'
sys.path.insert(0, str(ml_dir))

from ml.services.embedding_service import get_embedding_service
from ml.services.faiss_service import get_faiss_service

search_bp = Blueprint('search', __name__)

# Load FAISS index on startup
_index_loaded = False


def ensure_index_loaded():
    """Ensure FAISS index is loaded"""
    global _index_loaded
    
    if _index_loaded:
        return True
    
    try:
        from flask import current_app
        faiss_path = current_app.config.get('FAISS_INDEX_PATH', 'ml/saved_models/faiss_index.bin')
        embedding_dim = current_app.config.get('EMBEDDING_DIM', 384)
        
        # Check if index file exists
        if not os.path.exists(faiss_path):
            return False
        
        # Load FAISS index
        faiss_service = get_faiss_service(embedding_dim=embedding_dim)
        faiss_service.load(faiss_path)
        
        _index_loaded = True
        return True
        
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return False


@search_bp.route('/status', methods=['GET'])
def search_status():
    """Check if vector search is available"""
    if ensure_index_loaded():
        faiss_service = get_faiss_service()
        stats = faiss_service.get_stats()
        return jsonify({
            'available': True,
            'stats': stats
        }), 200
    else:
        return jsonify({
            'available': False,
            'message': 'FAISS index not built yet. Run scripts/build_faiss_index.py'
        }), 503


@search_bp.route('/vector', methods=['POST'])
def vector_search():
    """
    Search anime by text query using vector similarity
    
    Body:
        query (str): Search query text
        limit (int): Number of results to return (default: 10)
    
    Returns:
        List of anime with similarity scores
    """
    if not ensure_index_loaded():
        return jsonify({
            'error': 'Vector search not available. Index not built.'
        }), 503
    
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    query = data['query']
    limit = data.get('limit', 10)
    
    if not query or len(query.strip()) < 2:
        return jsonify({'error': 'Query must be at least 2 characters'}), 400
    
    limit = min(max(1, limit), 50)  # Clamp between 1 and 50
    
    try:
        # Generate embedding for query
        from flask import current_app
        model_name = current_app.config.get('EMBEDDING_MODEL')
        
        embedding_service = get_embedding_service(model_name=model_name)
        query_embedding = embedding_service.generate_embedding(query)
        
        # Search in FAISS
        faiss_service = get_faiss_service()
        results = faiss_service.search(query_embedding, k=limit)
        
        # Get anime details from database
        db = get_db()
        anime_ids = [anime_id for anime_id, _ in results]
        
        animes_cursor = db.animes.find(
            {'mal_id': {'$in': anime_ids}},
            {'_id': 0}
        )
        animes_dict = {a['mal_id']: a for a in animes_cursor}
        
        # Build response with scores
        anime_results = []
        for anime_id, similarity in results:
            if anime_id in animes_dict:
                anime = animes_dict[anime_id].copy()
                anime['similarity_score'] = similarity
                anime_results.append(anime)
        
        return jsonify({
            'animes': anime_results,
            'count': len(anime_results),
            'query': query
        }), 200
        
    except Exception as e:
        print(f"Error in vector search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@search_bp.route('/similar/<int:anime_id>', methods=['GET'])
def find_similar(anime_id):
    """
    Find similar anime based on another anime
    
    Args:
        anime_id: Anime ID to find similar ones for
        
    Query params:
        limit: Number of results (default: 10)
    
    Returns:
        List of similar anime with similarity scores
    """
    if not ensure_index_loaded():
        return jsonify({
            'error': 'Vector search not available. Index not built.'
        }), 503
    
    limit = request.args.get('limit', 10, type=int)
    limit = min(max(1, limit), 50)
    
    # Check if anime exists
    db = get_db()
    anime = db.animes.find_one({'mal_id': anime_id}, {'_id': 0})
    
    if not anime:
        return jsonify({'error': 'Anime not found'}), 404
    
    try:
        # Find similar anime
        faiss_service = get_faiss_service()
        results = faiss_service.search_by_id(anime_id, k=limit, exclude_self=True)
        
        # Get anime details
        anime_ids = [aid for aid, _ in results]
        animes_cursor = db.animes.find(
            {'mal_id': {'$in': anime_ids}},
            {'_id': 0}
        )
        animes_dict = {a['mal_id']: a for a in animes_cursor}
        
        # Build response
        anime_results = []
        for aid, similarity in results:
            if aid in animes_dict:
                similar_anime = animes_dict[aid].copy()
                similar_anime['similarity_score'] = similarity
                anime_results.append(similar_anime)
        
        return jsonify({
            'anime': anime,
            'similar': anime_results,
            'count': len(anime_results)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"Error finding similar anime: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500
