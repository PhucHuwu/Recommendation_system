from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from datetime import datetime

history_bp = Blueprint('history', __name__)


def _get_history_from_ratings(target_user_id: int, page: int = 1, limit: int = 20):
    """
    Helper function to get watch history from ratings collection
    
    Logic: If user rated an anime, they watched it
    
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
    
    # Get total count from ratings (rated = watched)
    total = db.ratings.count_documents({'user_id': target_user_id})
    
    # Get ratings as watch history (with anime info)
    pipeline = [
        {'$match': {'user_id': target_user_id}},
        # Sort by updated_at (most recent rating = most recent watch)
        {'$sort': {'updated_at': -1}},
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
            # Use updated_at as watched_at, fallback to created_at if updated_at is null
            'watched_at': {'$ifNull': ['$updated_at', '$created_at']},
            'anime_name': '$anime.name',
            'anime_genres': '$anime.genres',
            'anime_score': '$anime.score'
        }}
    ]
    
    history = list(db.ratings.aggregate(pipeline))
    
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
    """Get current user's watch history (from ratings)"""
    user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    data = _get_history_from_ratings(user_id, page, limit)
    return jsonify(data), 200


@history_bp.route('/user/<int:target_user_id>', methods=['GET'])
def get_user_history(target_user_id):
    """Get watch history for a specific user (PUBLIC - from ratings)"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    data = _get_history_from_ratings(target_user_id, page, limit)
    return jsonify(data), 200


@history_bp.route('/', methods=['POST'])
@jwt_required()
def add_to_history():
    """
    Add to history is now deprecated - use ratings instead
    This endpoint is kept for backward compatibility but does nothing
    """
    return jsonify({
        'message': 'Use ratings to track watch history',
        'deprecated': True
    }), 200


@history_bp.route('/<int:anime_id>', methods=['DELETE'])
@jwt_required()
def remove_from_history(anime_id):
    """
    Remove from history is now deprecated - delete rating instead
    This endpoint is kept for backward compatibility
    """
    user_id = int(get_jwt_identity())
    db = get_db()
    
    # Delete rating (which is the watch history)
    result = db.ratings.delete_one({
        'user_id': user_id,
        'anime_id': anime_id
    })
    
    if result.deleted_count == 0:
        return jsonify({'error': 'No rating found for this anime'}), 404
    
    return jsonify({
        'message': f'Rating/history deleted successfully'
    }), 200
