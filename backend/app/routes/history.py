from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from datetime import datetime

history_bp = Blueprint('history', __name__)


def _get_history_data(target_user_id: int, page: int = 1, limit: int = 20):
    """
    Helper function to fetch history data for a user
    
    Args:
        target_user_id: User ID to fetch history for
        page: Page number
        limit: Items per page
        
    Returns:
        dict with history, total, page, limit, user_id
    """
    limit = min(limit, 100)
    skip = (page - 1) * limit
    
    db = get_db()
    
    # Get total count
    total = db.watch_history.count_documents({'user_id': target_user_id})
    
    # Get history with anime info
    pipeline = [
        {'$match': {'user_id': target_user_id}},
        {'$sort': {'watched_at': -1}},
        {'$skip': skip},
        {'$limit': limit},
        {'$lookup': {
            'from': 'animes',
            'localField': 'anime_id',
            'foreignField': 'mal_id',
            'as': 'anime'
        }},
        {'$unwind': {'path': '$anime', 'preserveNullAndEmptyArrays': True}},
        {'$project': {
            '_id': 0,
            'anime_id': 1,
            'watched_at': 1,
            'anime_name': '$anime.name',
            'anime_genres': '$anime.genres',
            'anime_score': '$anime.score'
        }}
    ]
    
    history = list(db.watch_history.aggregate(pipeline))
    
    return {
        'history': history,
        'total': total,
        'page': page,
        'limit': limit,
        'user_id': target_user_id
    }


@history_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_history():
    """Get current user's watch history"""
    user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    data = _get_history_data(user_id, page, limit)
    return jsonify(data), 200


@history_bp.route('/user/<int:target_user_id>', methods=['GET'])
def get_user_history(target_user_id):
    """Get watch history for a specific user (PUBLIC - no auth required)"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    data = _get_history_data(target_user_id, page, limit)
    return jsonify(data), 200


@history_bp.route('/', methods=['POST'])
@jwt_required()
def add_to_history():
    """Add anime to watch history"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'anime_id' not in data:
        return jsonify({'error': 'anime_id is required'}), 400
    
    try:
        anime_id = int(data['anime_id'])
    except ValueError:
        return jsonify({'error': 'anime_id must be a number'}), 400
    
    db = get_db()
    
    # Check if anime exists
    anime = db.animes.find_one({'mal_id': anime_id})
    if not anime:
        return jsonify({'error': 'Anime not found'}), 404
    
    # Add to history (allow duplicates for tracking multiple watches)
    new_entry = {
        'user_id': user_id,
        'anime_id': anime_id,
        'watched_at': datetime.utcnow()
    }
    
    db.watch_history.insert_one(new_entry)
    
    return jsonify({
        'message': 'Added to watch history',
        'history': {
            'user_id': user_id,
            'anime_id': anime_id,
            'anime_name': anime.get('name')
        }
    }), 201


@history_bp.route('/<int:anime_id>', methods=['DELETE'])
@jwt_required()
def remove_from_history(anime_id):
    """Remove anime from watch history"""
    user_id = int(get_jwt_identity())
    db = get_db()
    
    # Remove all entries for this anime (or just the latest one)
    result = db.watch_history.delete_many({
        'user_id': user_id,
        'anime_id': anime_id
    })
    
    if result.deleted_count == 0:
        return jsonify({'error': 'History entry not found'}), 404
    
    return jsonify({
        'message': f'Removed {result.deleted_count} entries from history'
    }), 200
