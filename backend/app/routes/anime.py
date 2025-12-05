from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from bson import ObjectId

anime_bp = Blueprint('anime', __name__)


@anime_bp.route('/', methods=['GET'])
def get_animes():
    """Get list of animes with pagination"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    genre = request.args.get('genre', None)
    sort_by = request.args.get('sort', 'score')  # score, name
    order = request.args.get('order', 'desc')  # asc, desc
    
    # Limit max items per page
    limit = min(limit, 100)
    skip = (page - 1) * limit
    
    db = get_db()
    
    # Build query
    query = {}
    if genre:
        query['genres'] = {'$regex': genre, '$options': 'i'}
    
    # Build sort
    sort_order = -1 if order == 'desc' else 1
    sort_field = 'score' if sort_by == 'score' else 'name'
    
    # Get total count
    total = db.animes.count_documents(query)
    
    # Get animes
    animes = list(db.animes.find(query, {'_id': 0})
                  .sort(sort_field, sort_order)
                  .skip(skip)
                  .limit(limit))
    
    return jsonify({
        'animes': animes,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    }), 200


@anime_bp.route('/<int:anime_id>', methods=['GET'])
def get_anime(anime_id):
    """Get single anime by ID"""
    db = get_db()
    
    anime = db.animes.find_one({'mal_id': anime_id}, {'_id': 0})
    
    if not anime:
        return jsonify({'error': 'Anime not found'}), 404
    
    # Get average rating from user ratings
    pipeline = [
        {'$match': {'anime_id': anime_id}},
        {'$group': {
            '_id': None,
            'avg_rating': {'$avg': '$rating'},
            'rating_count': {'$sum': 1}
        }}
    ]
    rating_stats = list(db.ratings.aggregate(pipeline))
    
    if rating_stats:
        anime['user_avg_rating'] = round(rating_stats[0]['avg_rating'], 2)
        anime['user_rating_count'] = rating_stats[0]['rating_count']
    else:
        anime['user_avg_rating'] = None
        anime['user_rating_count'] = 0
    
    return jsonify({'anime': anime}), 200


@anime_bp.route('/search', methods=['GET'])
def search_animes():
    """Search animes by name"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query or len(query) < 2:
        return jsonify({'error': 'Search query must be at least 2 characters'}), 400
    
    limit = min(limit, 50)
    
    db = get_db()
    
    # Search by name (case insensitive)
    animes = list(db.animes.find(
        {'name': {'$regex': query, '$options': 'i'}},
        {'_id': 0}
    ).limit(limit))
    
    return jsonify({
        'animes': animes,
        'count': len(animes),
        'query': query
    }), 200


@anime_bp.route('/top', methods=['GET'])
def get_top_animes():
    """Get top rated animes"""
    limit = request.args.get('limit', 10, type=int)
    limit = min(limit, 50)
    
    db = get_db()
    
    animes = list(db.animes.find({}, {'_id': 0})
                  .sort('score', -1)
                  .limit(limit))
    
    return jsonify({'animes': animes}), 200


@anime_bp.route('/genres', methods=['GET'])
def get_genres():
    """Get list of all unique genres"""
    db = get_db()
    
    # Get all unique genres
    pipeline = [
        {'$project': {'genres': {'$split': ['$genres', ', ']}}},
        {'$unwind': '$genres'},
        {'$group': {'_id': '$genres'}},
        {'$sort': {'_id': 1}}
    ]
    
    result = list(db.animes.aggregate(pipeline))
    genres = [r['_id'] for r in result if r['_id']]
    
    return jsonify({'genres': genres}), 200
