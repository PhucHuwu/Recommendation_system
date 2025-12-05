from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from app.services.recommendation_service import get_recommendation_service

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
        model = active_model['name'] if active_model else 'user_based_cf'
    
    # Get recommendation service
    rec_service = get_recommendation_service()
    
    # Get recommendations from ML model
    recommendations = rec_service.get_recommendations(user_id, n=limit, model_name=model)
    
    if not recommendations:
        # Fallback: return top animes if no recommendations
        user_ratings = list(db.ratings.find({'user_id': user_id}, {'anime_id': 1}))
        rated_anime_ids = [r['anime_id'] for r in user_ratings]
        
        animes = list(db.animes.find(
            {'mal_id': {'$nin': rated_anime_ids}},
            {'_id': 0}
        ).sort('score', -1).limit(limit))
        
        recommendations = [(a['mal_id'], a.get('score', 0)) for a in animes]
    
    # Get anime details for recommendations
    result = []
    for anime_id, predicted_rating in recommendations:
        anime = db.animes.find_one({'mal_id': anime_id}, {'_id': 0})
        if anime:
            result.append({
                'anime_id': anime_id,
                'name': anime.get('name'),
                'genres': anime.get('genres'),
                'score': anime.get('score'),
                'predicted_rating': round(predicted_rating, 2)
            })
    
    return jsonify({
        'recommendations': result,
        'model_used': model,
        'count': len(result)
    }), 200


@recommendation_bp.route('/similar/<int:anime_id>', methods=['GET'])
def get_similar_animes(anime_id):
    """Get similar animes based on content/genre"""
    limit = request.args.get('limit', 10, type=int)
    use_content = request.args.get('use_content', 'false').lower() == 'true'
    
    limit = min(limit, 20)
    
    db = get_db()
    
    # Get the target anime
    target_anime = db.animes.find_one({'mal_id': anime_id})
    
    if not target_anime:
        return jsonify({'error': 'Anime not found'}), 404
    
    # Get recommendation service
    rec_service = get_recommendation_service()
    
    # Get similar animes from ML model
    similar = rec_service.get_similar_animes(anime_id, n=limit, use_content=use_content)
    
    # Get anime details
    result = []
    for sim_anime_id, similarity in similar:
        anime = db.animes.find_one({'mal_id': sim_anime_id}, {'_id': 0})
        if anime:
            result.append({
                'anime_id': sim_anime_id,
                'name': anime.get('name'),
                'genres': anime.get('genres'),
                'score': anime.get('score'),
                'similarity': round(similarity, 4)
            })
    
    return jsonify({
        'anime_id': anime_id,
        'anime_name': target_anime.get('name'),
        'similar_animes': result,
        'count': len(result),
        'method': 'content-based' if use_content else 'item-based'
    }), 200
