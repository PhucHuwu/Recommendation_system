"""
Movie Recommendation System - Streamlit Web App

A web interface for the movie recommendation system.
Supports multiple recommendation models and comparison.
"""

import streamlit as st
import sys
import os
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.abspath('./src'))

from models.content_based import ContentBasedRecommender
from models.collaborative_filtering import CollaborativeFilteringRecommender

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
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #4ECDC4;
        margin-bottom: 2rem;
    }
    .movie-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #FF6B6B;
    }
    .metric-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF6B6B;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff5252;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_data():
    """Load movies and ratings data."""
    movies = pd.read_csv('data/processed/movies_enriched.csv')
    ratings = pd.read_csv('data/processed/ratings.csv')
    return movies, ratings


@st.cache_resource
def load_models():
    """Load all trained models."""
    models = {}
    
    # Content-Based Models
    cb_tfidf = ContentBasedRecommender(verbose=False)
    cb_tfidf.load_model(
        'data/models/content_based_tfidf.pkl',
        'data/processed/movies_enriched.csv'
    )
    models['Content-Based (TF-IDF)'] = cb_tfidf
    
    cb_genre = ContentBasedRecommender(verbose=False)
    cb_genre.load_model(
        'data/models/content_based_genre.pkl',
        'data/processed/movies_enriched.csv'
    )
    models['Content-Based (Genre)'] = cb_genre
    
    cb_combined = ContentBasedRecommender(verbose=False)
    cb_combined.load_model(
        'data/models/content_based_combined.pkl',
        'data/processed/movies_enriched.csv'
    )
    models['Content-Based (Combined)'] = cb_combined
    
    # Collaborative Filtering Models
    cf_item = CollaborativeFilteringRecommender(approach='item', verbose=False)
    cf_item.load_model(
        'data/models/collaborative_item_based.pkl',
        'data/processed/ratings.csv',
        'data/processed/movies_enriched.csv'
    )
    models['Collaborative (Item-Based)'] = cf_item
    
    cf_user = CollaborativeFilteringRecommender(approach='user', verbose=False)
    cf_user.load_model(
        'data/models/collaborative_user_based.pkl',
        'data/processed/ratings.csv',
        'data/processed/movies_enriched.csv'
    )
    models['Collaborative (User-Based)'] = cf_user
    
    return models


def display_movie_card(movie_data, show_similarity=False, similarity_score=None):
    """Display a movie card with details."""
    with st.container():
        st.markdown('<div class="movie-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### 🎬 {movie_data['title_clean']}")
            st.markdown(f"**Year:** {int(movie_data['year']) if pd.notna(movie_data['year']) else 'Unknown'}")
            st.markdown(f"**Genres:** {movie_data['genres']}")
        
        with col2:
            if pd.notna(movie_data['avg_rating']):
                st.metric("⭐ Rating", f"{movie_data['avg_rating']:.2f}/5.0")
            if pd.notna(movie_data['num_ratings']):
                st.metric("👥 Ratings", f"{int(movie_data['num_ratings']):,}")
            if show_similarity and similarity_score is not None:
                st.metric("🎯 Similarity", f"{similarity_score:.3f}")
        
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<p class="main-header">🎬 Movie Recommendation System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Discover your next favorite movie!</p>', unsafe_allow_html=True)
    
    # Load data and models
    with st.spinner('Loading data and models...'):
        movies, ratings = load_data()
        models = load_models()
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    st.sidebar.markdown("---")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Select Mode:",
        ["🔍 Search & Recommend", "👤 User Recommendations", "📊 Model Comparison"]
    )
    
    st.sidebar.markdown("---")
    
    # Model selection
    model_name = st.sidebar.selectbox(
        "Choose Recommendation Model:",
        list(models.keys())
    )
    
    # Number of recommendations
    n_recommendations = st.sidebar.slider(
        "Number of Recommendations:",
        min_value=5,
        max_value=20,
        value=10,
        step=5
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **Dataset Info:**
    - Movies: {len(movies):,}
    - Ratings: {len(ratings):,}
    - Users: {ratings['userId'].nunique():,}
    """)
    
    # Main content based on mode
    if mode == "🔍 Search & Recommend":
        search_and_recommend(movies, models, model_name, n_recommendations)
    
    elif mode == "👤 User Recommendations":
        user_recommendations(movies, ratings, models, model_name, n_recommendations)
    
    elif mode == "📊 Model Comparison":
        model_comparison(movies, models, n_recommendations)


def search_and_recommend(movies, models, model_name, n_recommendations):
    """Search for a movie and get recommendations."""
    st.header("🔍 Search for a Movie")
    
    # Search box
    search_query = st.text_input(
        "Enter movie title:",
        placeholder="e.g., Toy Story, Matrix, Inception..."
    )
    
    if search_query:
        # Find matching movies
        matches = movies[
            movies['title'].str.contains(search_query, case=False, na=False) |
            movies['title_clean'].str.contains(search_query, case=False, na=False)
        ]
        
        if len(matches) == 0:
            st.warning("No movies found. Try a different search term.")
        else:
            st.success(f"Found {len(matches)} movie(s)")
            
            # Show matches
            selected_movie_id = st.selectbox(
                "Select a movie:",
                matches['movieId'].tolist(),
                format_func=lambda x: movies[movies['movieId'] == x].iloc[0]['title']
            )
            
            if selected_movie_id:
                # Display selected movie
                st.subheader("📽️ Selected Movie")
                selected_movie = movies[movies['movieId'] == selected_movie_id].iloc[0]
                display_movie_card(selected_movie)
                
                # Get recommendations
                st.markdown("---")
                st.subheader(f"🎯 Recommendations from {model_name}")
                
                with st.spinner('Generating recommendations...'):
                    try:
                        model = models[model_name]
                        
                        # Get recommendations based on model type
                        if 'Collaborative' in model_name and 'Item' in model_name:
                            if selected_movie_id in model.movie_id_to_idx:
                                recs = model.get_item_based_recommendations(selected_movie_id, n=n_recommendations)
                            else:
                                st.warning("This movie is not in the Collaborative Filtering dataset. Try a more popular movie or use Content-Based models.")
                                return
                        elif 'Collaborative' in model_name and 'User' in model_name:
                            st.warning("User-Based CF requires a user ID. Please use 'User Recommendations' mode.")
                            return
                        else:
                            recs = model.get_recommendations(selected_movie_id, n=n_recommendations)
                        
                        # Display recommendations
                        for idx, (_, rec) in enumerate(recs.iterrows(), 1):
                            st.markdown(f"**{idx}. Recommendation**")
                            movie_data = movies[movies['movieId'] == rec['movieId']].iloc[0]
                            
                            similarity_score = rec.get('similarity_score', rec.get('predicted_rating', None))
                            display_movie_card(movie_data, show_similarity=True, similarity_score=similarity_score)
                    
                    except Exception as e:
                        st.error(f"Error generating recommendations: {str(e)}")


def user_recommendations(movies, ratings, models, model_name, n_recommendations):
    """Get personalized recommendations for a user."""
    st.header("👤 User-Based Recommendations")
    
    # Get list of users
    user_ids = sorted(ratings['userId'].unique())
    
    selected_user = st.selectbox(
        "Select User ID:",
        user_ids,
        index=0
    )
    
    if selected_user:
        # Show user's rating history
        user_ratings = ratings[ratings['userId'] == selected_user].merge(
            movies[['movieId', 'title_clean', 'genres']],
            on='movieId'
        ).sort_values('rating', ascending=False)
        
        with st.expander(f"📚 User {selected_user}'s Rating History ({len(user_ratings)} movies)"):
            st.dataframe(
                user_ratings[['title_clean', 'genres', 'rating', 'timestamp']].head(20),
                use_container_width=True
            )
        
        # Get recommendations
        st.markdown("---")
        st.subheader(f"🎯 Personalized Recommendations")
        
        with st.spinner('Generating recommendations...'):
            try:
                if 'User-Based' in model_name:
                    model = models[model_name]
                    recs = model.get_user_based_recommendations(selected_user, n=n_recommendations)
                else:
                    st.warning("Please select 'Collaborative (User-Based)' model for user recommendations.")
                    return
                
                # Display recommendations
                for idx, (_, rec) in enumerate(recs.iterrows(), 1):
                    st.markdown(f"**{idx}. Recommendation**")
                    movie_data = movies[movies['movieId'] == rec['movieId']].iloc[0]
                    display_movie_card(movie_data, show_similarity=True, similarity_score=rec['predicted_rating'])
            
            except Exception as e:
                st.error(f"Error: {str(e)}")


def model_comparison(movies, models, n_recommendations):
    """Compare recommendations from different models."""
    st.header("📊 Model Comparison")
    
    # Search for a movie
    search_query = st.text_input(
        "Enter movie title for comparison:",
        placeholder="e.g., Toy Story"
    )
    
    if search_query:
        matches = movies[
            movies['title'].str.contains(search_query, case=False, na=False) |
            movies['title_clean'].str.contains(search_query, case=False, na=False)
        ]
        
        if len(matches) > 0:
            selected_movie_id = st.selectbox(
                "Select a movie:",
                matches['movieId'].tolist(),
                format_func=lambda x: movies[movies['movieId'] == x].iloc[0]['title']
            )
            
            if selected_movie_id:
                selected_movie = movies[movies['movieId'] == selected_movie_id].iloc[0]
                display_movie_card(selected_movie)
                
                st.markdown("---")
                
                # Get recommendations from all content-based models
                cols = st.columns(3)
                
                cb_models = {name: model for name, model in models.items() if 'Content-Based' in name}
                
                for idx, (model_name, model) in enumerate(cb_models.items()):
                    with cols[idx]:
                        st.markdown(f"### {model_name}")
                        try:
                            recs = model.get_recommendations(selected_movie_id, n=5)
                            for _, rec in recs.iterrows():
                                movie_title = movies[movies['movieId'] == rec['movieId']].iloc[0]['title_clean']
                                st.markdown(f"- {movie_title} ({rec['similarity_score']:.3f})")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
