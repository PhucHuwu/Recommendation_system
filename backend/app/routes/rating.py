from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from datetime import datetime

rating_bp = Blueprint('rating', __name__)


@rating_bp.route('/', methods=['POST'])
@jwt_required()
def add_rating():
    """Add a new rating (1-10 scale)"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'anime_id' not in data or 'rating' not in data:
        return jsonify({'error': 'anime_id and rating are required'}), 400
    
    try:
        anime_id = int(data['anime_id'])
        rating = int(data['rating'])
    except ValueError:
        return jsonify({'error': 'anime_id and rating must be numbers'}), 400
    
    # Validate rating (1-10 scale as per dataset)
    if rating < 1 or rating > 10:
        return jsonify({'error': 'Rating must be between 1 and 10'}), 400
    
    db = get_db()
    
    # Check if anime exists
    anime = db.animes.find_one({'mal_id': anime_id})
    if not anime:
        return jsonify({'error': 'Anime not found'}), 404
    
    # Check if rating already exists
    existing = db.ratings.find_one({'user_id': user_id, 'anime_id': anime_id})
    
    if existing:
        return jsonify({'error': 'Rating already exists. Use PUT to update.'}), 409
    
    # Create new rating
    new_rating = {
        'user_id': user_id,
        'anime_id': anime_id,
        'rating': rating,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = db.ratings.insert_one(new_rating)
    new_rating['_id'] = str(result.inserted_id)
    
    return jsonify({
        'message': 'Rating added successfully',
        'rating': {
            'user_id': user_id,
            'anime_id': anime_id,
            'rating': rating
        }
    }), 201


@rating_bp.route('/<int:anime_id>', methods=['PUT'])
@jwt_required()
def update_rating(anime_id):
    """Update an existing rating"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'rating' not in data:
        return jsonify({'error': 'rating is required'}), 400
    
    try:
        rating = int(data['rating'])
    except ValueError:
        return jsonify({'error': 'rating must be a number'}), 400
    
    # Validate rating (1-10 scale)
    if rating < 1 or rating > 10:
        return jsonify({'error': 'Rating must be between 1 and 10'}), 400
    
    db = get_db()
    
    # Update rating
    result = db.ratings.update_one(
        {'user_id': user_id, 'anime_id': anime_id},
        {'$set': {'rating': rating, 'updated_at': datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'Rating not found'}), 404
    
    return jsonify({
        'message': 'Rating updated successfully',
        'rating': {
            'user_id': user_id,
            'anime_id': anime_id,
            'rating': rating
        }
    }), 200


@rating_bp.route('/<int:anime_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(anime_id):
    """Delete a rating"""
    user_id = int(get_jwt_identity())
    db = get_db()
    
    result = db.ratings.delete_one({'user_id': user_id, 'anime_id': anime_id})
    
    if result.deleted_count == 0:
        return jsonify({'error': 'Rating not found'}), 404
    
    return jsonify({'message': 'Rating deleted successfully'}), 200


@rating_bp.route('/user/<int:target_user_id>', methods=['GET'])
def get_user_ratings(target_user_id):
    """Get all ratings by a specific user"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    limit = min(limit, 100)
    skip = (page - 1) * limit
    
    db = get_db()
    
    # Get total count
    total = db.ratings.count_documents({'user_id': target_user_id})
    
    # Get ratings with anime info
    pipeline = [
        {'$match': {'user_id': target_user_id}},
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
            'rating': 1,
            'created_at': 1,
            'updated_at': 1,
            'anime_name': '$anime.name',
            'anime_genres': '$anime.genres'
        }}
    ]
    
    ratings = list(db.ratings.aggregate(pipeline))
    
    return jsonify({
        'ratings': ratings,
        'total': total,
        'page': page,
        'limit': limit
    }), 200


@rating_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_ratings():
    """Get current user's ratings"""
    user_id = int(get_jwt_identity())
    return get_user_ratings(user_id)
