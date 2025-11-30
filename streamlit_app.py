"""
Movie Recommendation System - Streamlit Cloud App

Optimized version for Streamlit Cloud deployment.
Builds models on-the-fly instead of loading large pickle files.
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Page config
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #4ECDC4;
        margin-bottom: 1.5rem;
    }
    .movie-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 5px solid #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load movies and ratings data."""
    movies = pd.read_csv('data/processed/movies_enriched.csv')
    ratings = pd.read_csv('data/processed/ratings.csv')
    return movies, ratings


@st.cache_resource
def build_content_based_model(movies, feature_type='genre'):
    """
    Build content-based model on-the-fly.
    
    Args:
        movies: Movies DataFrame
        feature_type: 'genre', 'tfidf', or 'combined'
    
    Returns:
        similarity_matrix, movie_indices, index_to_movieId
    """
    movie_indices = {movieId: idx for idx, movieId in enumerate(movies['movieId'])}
    index_to_movieId = {idx: movieId for movieId, idx in movie_indices.items()}
    
    if feature_type == 'genre':
        # Genre-based features
        genre_cols = [col for col in movies.columns if col.startswith('is_')]
        feature_matrix = movies[genre_cols].values
        
    elif feature_type == 'tfidf':
        # TF-IDF features
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2), stop_words='english')
        texts = movies['combined_features'].fillna('') if 'combined_features' in movies.columns else movies['genres'].fillna('')
        feature_matrix = vectorizer.fit_transform(texts)
        
    else:  # combined
        # Combined genre + numeric features
        genre_cols = [col for col in movies.columns if col.startswith('is_')]
        genre_features = movies[genre_cols].values
        
        numeric_cols = ['year', 'avg_rating', 'popularity', 'genres_count']
        numeric_cols = [col for col in numeric_cols if col in movies.columns]
        
        if numeric_cols:
            numeric_features = movies[numeric_cols].fillna(0).values
            numeric_features = (numeric_features - numeric_features.min(axis=0)) / \
                              (numeric_features.max(axis=0) - numeric_features.min(axis=0) + 1e-8)
            feature_matrix = np.hstack([genre_features, numeric_features])
        else:
            feature_matrix = genre_features
    
    # Compute similarity
    similarity_matrix = cosine_similarity(feature_matrix)
    
    return similarity_matrix, movie_indices, index_to_movieId


@st.cache_resource
def build_collaborative_model(ratings, movies, approach='item'):
    """
    Build collaborative filtering model on-the-fly.
    
    Args:
        ratings: Ratings DataFrame
        movies: Movies DataFrame  
        approach: 'item' or 'user'
    
    Returns:
        similarity_matrix, user_item_matrix, movie_indices, user_indices
    """
    # Create user-item matrix
    user_item = ratings.pivot_table(
        index='userId', 
        columns='movieId', 
        values='rating',
        fill_value=0
    )
    
    movie_indices = {movieId: idx for idx, movieId in enumerate(user_item.columns)}
    user_indices = {userId: idx for idx, userId in enumerate(user_item.index)}
    index_to_movieId = {idx: movieId for movieId, idx in movie_indices.items()}
    index_to_userId = {idx: userId for userId, idx in user_indices.items()}
    
    if approach == 'item':
        # Item-based: similarity between movies
        similarity_matrix = cosine_similarity(user_item.T)
    else:
        # User-based: similarity between users
        similarity_matrix = cosine_similarity(user_item)
    
    return similarity_matrix, user_item, movie_indices, user_indices, index_to_movieId, index_to_userId


def get_content_recommendations(movie_id, similarity_matrix, movie_indices, index_to_movieId, movies, n=10):
    """Get content-based recommendations."""
    if movie_id not in movie_indices:
        return pd.DataFrame()
    
    idx = movie_indices[movie_id]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+50]
    
    recommendations = []
    for movie_idx, score in sim_scores:
        rec_movie_id = index_to_movieId[movie_idx]
        movie_data = movies[movies['movieId'] == rec_movie_id]
        if len(movie_data) > 0:
            movie_data = movie_data.iloc[0]
            if movie_data.get('num_ratings', 0) >= 10:
                recommendations.append({
                    'movieId': rec_movie_id,
                    'title': movie_data.get('title_clean', movie_data.get('title', '')),
                    'year': movie_data.get('year', 0),
                    'genres': movie_data.get('genres', ''),
                    'avg_rating': movie_data.get('avg_rating', 0),
                    'num_ratings': movie_data.get('num_ratings', 0),
                    'similarity_score': score
                })
                if len(recommendations) >= n:
                    break
    
    return pd.DataFrame(recommendations)


def get_item_based_recommendations(movie_id, similarity_matrix, movie_indices, index_to_movieId, movies, n=10):
    """Get item-based collaborative filtering recommendations."""
    if movie_id not in movie_indices:
        return pd.DataFrame()
    
    idx = movie_indices[movie_id]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+50]
    
    recommendations = []
    for movie_idx, score in sim_scores:
        rec_movie_id = index_to_movieId[movie_idx]
        movie_data = movies[movies['movieId'] == rec_movie_id]
        if len(movie_data) > 0:
            movie_data = movie_data.iloc[0]
            recommendations.append({
                'movieId': rec_movie_id,
                'title': movie_data.get('title_clean', movie_data.get('title', '')),
                'year': movie_data.get('year', 0),
                'genres': movie_data.get('genres', ''),
                'avg_rating': movie_data.get('avg_rating', 0),
                'num_ratings': movie_data.get('num_ratings', 0),
                'similarity_score': score
            })
            if len(recommendations) >= n:
                break
    
    return pd.DataFrame(recommendations)


def get_user_based_recommendations(user_id, similarity_matrix, user_item, user_indices, index_to_movieId, movies, n=10):
    """Get user-based collaborative filtering recommendations."""
    if user_id not in user_indices:
        return pd.DataFrame()
    
    user_idx = user_indices[user_id]
    user_ratings = user_item.iloc[user_idx].values
    
    # Find similar users
    user_similarities = similarity_matrix[user_idx]
    
    # Weighted average of similar users' ratings
    weighted_ratings = np.zeros(user_item.shape[1])
    similarity_sum = np.zeros(user_item.shape[1])
    
    for other_idx, sim in enumerate(user_similarities):
        if other_idx != user_idx and sim > 0:
            other_ratings = user_item.iloc[other_idx].values
            mask = (other_ratings > 0) & (user_ratings == 0)
            weighted_ratings[mask] += sim * other_ratings[mask]
            similarity_sum[mask] += sim
    
    # Avoid division by zero
    similarity_sum[similarity_sum == 0] = 1
    predicted_ratings = weighted_ratings / similarity_sum
    
    # Get top predictions for unwatched movies
    unwatched_mask = user_ratings == 0
    predictions = [(idx, predicted_ratings[idx]) for idx in range(len(predicted_ratings)) if unwatched_mask[idx]]
    predictions = sorted(predictions, key=lambda x: x[1], reverse=True)[:n+20]
    
    recommendations = []
    for movie_idx, pred_rating in predictions:
        rec_movie_id = index_to_movieId[movie_idx]
        movie_data = movies[movies['movieId'] == rec_movie_id]
        if len(movie_data) > 0:
            movie_data = movie_data.iloc[0]
            recommendations.append({
                'movieId': rec_movie_id,
                'title': movie_data.get('title_clean', movie_data.get('title', '')),
                'year': movie_data.get('year', 0),
                'genres': movie_data.get('genres', ''),
                'avg_rating': movie_data.get('avg_rating', 0),
                'num_ratings': movie_data.get('num_ratings', 0),
                'predicted_rating': pred_rating
            })
            if len(recommendations) >= n:
                break
    
    return pd.DataFrame(recommendations)


def display_movie_card(movie_data, score=None, score_label="Similarity"):
    """Display a movie card."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**🎬 {movie_data['title_clean']}**")
        year = int(movie_data['year']) if pd.notna(movie_data['year']) else 'Unknown'
        st.caption(f"📅 {year} | 🎭 {movie_data['genres']}")
    
    with col2:
        if pd.notna(movie_data['avg_rating']):
            st.metric("⭐", f"{movie_data['avg_rating']:.1f}")
        if score is not None:
            st.caption(f"{score_label}: {score:.3f}")


def main():
    # Header
    st.markdown('<p class="main-header">🎬 Movie Recommender</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Discover your next favorite movie!</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data...'):
        movies, ratings = load_data()
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Mode:",
        ["🔍 Movie Recommendations", "👤 User Recommendations", "📊 Model Comparison"]
    )
    
    st.sidebar.markdown("---")
    
    # Model selection
    model_type = st.sidebar.selectbox(
        "Model:",
        ["Content-Based (Genre)", "Content-Based (TF-IDF)", "Content-Based (Combined)", 
         "Collaborative (Item-Based)", "Collaborative (User-Based)"]
    )
    
    # Number of recommendations
    n_recommendations = st.sidebar.slider("Results:", 5, 15, 10)
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 **Dataset**\n- {len(movies):,} movies\n- {len(ratings):,} ratings\n- {ratings['userId'].nunique():,} users")
    
    # Build models based on selection
    if 'Content-Based' in model_type:
        feature_type = 'genre' if 'Genre' in model_type else ('tfidf' if 'TF-IDF' in model_type else 'combined')
        with st.spinner(f'Building {model_type} model...'):
            similarity_matrix, movie_indices, index_to_movieId = build_content_based_model(movies, feature_type)
    
    if 'Collaborative' in model_type:
        approach = 'item' if 'Item' in model_type else 'user'
        with st.spinner(f'Building {model_type} model...'):
            cf_similarity, user_item, cf_movie_indices, user_indices, cf_index_to_movieId, index_to_userId = build_collaborative_model(ratings, movies, approach)
    
    # Main content
    if mode == "🔍 Movie Recommendations":
        st.header("🔍 Find Similar Movies")
        
        search_query = st.text_input("Search movie:", placeholder="e.g., Toy Story, Matrix, Inception...")
        
        if search_query:
            matches = movies[
                movies['title'].str.contains(search_query, case=False, na=False) |
                movies['title_clean'].str.contains(search_query, case=False, na=False)
            ].head(20)
            
            if len(matches) == 0:
                st.warning("No movies found. Try a different search.")
            else:
                selected_movie_id = st.selectbox(
                    "Select movie:",
                    matches['movieId'].tolist(),
                    format_func=lambda x: movies[movies['movieId'] == x].iloc[0]['title']
                )
                
                if selected_movie_id:
                    selected_movie = movies[movies['movieId'] == selected_movie_id].iloc[0]
                    
                    st.subheader("📽️ Selected Movie")
                    display_movie_card(selected_movie)
                    
                    st.markdown("---")
                    st.subheader(f"🎯 Recommendations ({model_type})")
                    
                    # Get recommendations
                    if 'Content-Based' in model_type:
                        recs = get_content_recommendations(
                            selected_movie_id, similarity_matrix, movie_indices, 
                            index_to_movieId, movies, n_recommendations
                        )
                        score_label = "Similarity"
                    elif 'Item-Based' in model_type:
                        if selected_movie_id in cf_movie_indices:
                            recs = get_item_based_recommendations(
                                selected_movie_id, cf_similarity, cf_movie_indices,
                                cf_index_to_movieId, movies, n_recommendations
                            )
                            score_label = "Similarity"
                        else:
                            st.warning("Movie not in collaborative filtering dataset. Try Content-Based models.")
                            recs = pd.DataFrame()
                    else:
                        st.info("Use 'User Recommendations' mode for User-Based CF.")
                        recs = pd.DataFrame()
                    
                    if len(recs) > 0:
                        for idx, (_, rec) in enumerate(recs.iterrows(), 1):
                            with st.container():
                                st.markdown(f"**{idx}.**")
                                movie_data = movies[movies['movieId'] == rec['movieId']].iloc[0]
                                score = rec.get('similarity_score', rec.get('predicted_rating', 0))
                                display_movie_card(movie_data, score, score_label)
                                st.markdown("---")
    
    elif mode == "👤 User Recommendations":
        st.header("👤 Personalized Recommendations")
        
        if 'User-Based' not in model_type:
            st.warning("Please select 'Collaborative (User-Based)' model for user recommendations.")
        else:
            user_ids = sorted(ratings['userId'].unique())[:100]  # Limit for performance
            selected_user = st.selectbox("Select User ID:", user_ids)
            
            if selected_user:
                user_ratings_df = ratings[ratings['userId'] == selected_user].merge(
                    movies[['movieId', 'title_clean', 'genres']], on='movieId'
                ).sort_values('rating', ascending=False)
                
                with st.expander(f"📚 User {selected_user}'s History ({len(user_ratings_df)} movies)"):
                    st.dataframe(user_ratings_df[['title_clean', 'genres', 'rating']].head(15))
                
                st.markdown("---")
                st.subheader("🎯 Personalized Recommendations")
                
                recs = get_user_based_recommendations(
                    selected_user, cf_similarity, user_item, user_indices,
                    cf_index_to_movieId, movies, n_recommendations
                )
                
                if len(recs) > 0:
                    for idx, (_, rec) in enumerate(recs.iterrows(), 1):
                        movie_data = movies[movies['movieId'] == rec['movieId']].iloc[0]
                        st.markdown(f"**{idx}.**")
                        display_movie_card(movie_data, rec['predicted_rating'], "Predicted")
                        st.markdown("---")
                else:
                    st.info("No recommendations available for this user.")
    
    elif mode == "📊 Model Comparison":
        st.header("📊 Compare Models")
        
        search_query = st.text_input("Search movie:", placeholder="e.g., Toy Story")
        
        if search_query:
            matches = movies[
                movies['title'].str.contains(search_query, case=False, na=False)
            ].head(10)
            
            if len(matches) > 0:
                selected_movie_id = st.selectbox(
                    "Select movie:",
                    matches['movieId'].tolist(),
                    format_func=lambda x: movies[movies['movieId'] == x].iloc[0]['title']
                )
                
                if selected_movie_id:
                    st.markdown("---")
                    
                    # Build all content-based models
                    cols = st.columns(3)
                    
                    for idx, (feature_type, label) in enumerate([('genre', 'Genre'), ('tfidf', 'TF-IDF'), ('combined', 'Combined')]):
                        with cols[idx]:
                            st.markdown(f"### {label}")
                            sim_matrix, m_indices, idx_to_id = build_content_based_model(movies, feature_type)
                            recs = get_content_recommendations(selected_movie_id, sim_matrix, m_indices, idx_to_id, movies, 5)
                            
                            if len(recs) > 0:
                                for _, rec in recs.iterrows():
                                    st.markdown(f"- {rec['title']} ({rec['similarity_score']:.3f})")
                            else:
                                st.caption("No recommendations")


if __name__ == "__main__":
    main()
