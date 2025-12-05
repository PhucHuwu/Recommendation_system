from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db

recommendation_bp = Blueprint('recommendation', __name__)


@recommendation_bp.route('/', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized recommendations for the current user"""
    user_id = int(get_jwt_identity())
    limit = request.args.get('limit', 10, type=int)
    model = request.args.get('model', None)  # Allow specifying model
    
    limit = min(limit, 50)
    
    db = get_db()
    
    # Get active model if not specified
    if not model:
        active_model = db.models.find_one({'is_active': True})
        model = active_model['name'] if active_model else 'user_based'
    
    # TODO: Replace with actual ML recommendation logic
    # For now, return top-rated animes the user hasn't rated yet
    
    # Get user's rated anime IDs
    user_ratings = list(db.ratings.find({'user_id': user_id}, {'anime_id': 1}))
    rated_anime_ids = [r['anime_id'] for r in user_ratings]
    
    # Get top animes user hasn't rated
    recommendations = list(db.animes.find(
        {'mal_id': {'$nin': rated_anime_ids}},
        {'_id': 0}
    ).sort('score', -1).limit(limit))
    
    # Add predicted rating (placeholder - will be replaced by ML model)
    for anime in recommendations:
        anime['predicted_rating'] = anime.get('score', 0)
    
    return jsonify({
        'recommendations': recommendations,
        'model_used': model,
        'count': len(recommendations)
    }), 200


@recommendation_bp.route('/similar/<int:anime_id>', methods=['GET'])
def get_similar_animes(anime_id):
    """Get similar animes based on content/genre"""
    limit = request.args.get('limit', 10, type=int)
    limit = min(limit, 20)
    
    db = get_db()
    
    # Get the target anime
    target_anime = db.animes.find_one({'mal_id': anime_id})
    
    if not target_anime:
        return jsonify({'error': 'Anime not found'}), 404
    
    # Get target genres
    target_genres = target_anime.get('genres', '')
    
    if not target_genres:
        return jsonify({'animes': [], 'message': 'No genres found for this anime'}), 200
    
    # Find animes with similar genres (simple approach)
    # TODO: Replace with content-based filtering using TF-IDF/embeddings
    similar_animes = list(db.animes.find(
        {
            'mal_id': {'$ne': anime_id},
            'genres': {'$regex': target_genres.split(',')[0].strip(), '$options': 'i'}
        },
        {'_id': 0}
    ).sort('score', -1).limit(limit))
    
    return jsonify({
        'anime_id': anime_id,
        'anime_name': target_anime.get('name'),
        'similar_animes': similar_animes,
        'count': len(similar_animes)
    }), 200
