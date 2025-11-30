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

# SVG Icons
def get_svg_icon(icon_name, size=24, color="#FF6B6B"):
    """Get SVG icon markup."""
    icons = {
        'movie': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="2" y1="7" x2="7" y2="7"></line><line x1="2" y1="17" x2="7" y2="17"></line><line x1="17" y1="17" x2="22" y2="17"></line><line x1="17" y1="7" x2="22" y2="7"></line></svg>''',
        'search': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>''',
        'user': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>''',
        'chart': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>''',
        'star': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>''',
        'users': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>''',
        'target': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>''',
        'settings': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M12 1v6m0 6v6m5.657-13.657-4.243 4.243m-2.828 2.828-4.243 4.243m16.97 1.414-4.243-4.243m-2.828-2.828-4.243-4.243m16.97 7.071h-6m-6 0H1"></path></svg>''',
        'calendar': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>''',
        'tag': f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>''',
    }
    return icons.get(icon_name, '')

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .movie-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #FF6B6B;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .movie-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .metric-card {
        background-color: #fff;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .icon-text {
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #FF6B6B 0%, #ff5252 100%);
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(255,107,107,0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff5252 0%, #ff3838 100%);
        box-shadow: 0 6px 10px rgba(255,107,107,0.4);
    }
    .sidebar-icon {
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
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
            st.markdown(f'''
                <div class="icon-text">
                    {get_svg_icon('movie', 28, '#FF6B6B')}
                    <h3 style="display:inline; margin:0;">{movie_data['title_clean']}</h3>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(f'''
                <div class="icon-text" style="margin-top:8px;">
                    {get_svg_icon('calendar', 18, '#666')}
                    <span><strong>Year:</strong> {int(movie_data['year']) if pd.notna(movie_data['year']) else 'Unknown'}</span>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(f'''
                <div class="icon-text" style="margin-top:8px;">
                    {get_svg_icon('tag', 18, '#666')}
                    <span><strong>Genres:</strong> {movie_data['genres']}</span>
                </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            if pd.notna(movie_data['avg_rating']):
                st.markdown(f'''
                    <div class="metric-card">
                        <div class="icon-text" style="justify-content:center;">
                            {get_svg_icon('star', 20, '#FFD700')}
                            <span style="font-size:0.9rem; color:#666;">Rating</span>
                        </div>
                        <div style="font-size:1.5rem; font-weight:bold; color:#FF6B6B; margin-top:4px;">
                            {movie_data['avg_rating']:.2f}/5.0
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            if pd.notna(movie_data['num_ratings']):
                st.markdown(f'''
                    <div class="metric-card">
                        <div class="icon-text" style="justify-content:center;">
                            {get_svg_icon('users', 20, '#4ECDC4')}
                            <span style="font-size:0.9rem; color:#666;">Ratings</span>
                        </div>
                        <div style="font-size:1.3rem; font-weight:bold; color:#4ECDC4; margin-top:4px;">
                            {int(movie_data['num_ratings']):,}
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            if show_similarity and similarity_score is not None:
                st.markdown(f'''
                    <div class="metric-card">
                        <div class="icon-text" style="justify-content:center;">
                            {get_svg_icon('target', 20, '#9B59B6')}
                            <span style="font-size:0.9rem; color:#666;">Similarity</span>
                        </div>
                        <div style="font-size:1.3rem; font-weight:bold; color:#9B59B6; margin-top:4px;">
                            {similarity_score:.3f}
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    # Header
    st.markdown(f'''
        <div style="text-align:center; margin-bottom:2rem;">
            <div style="display:inline-block; margin-bottom:1rem;">
                {get_svg_icon('movie', 60, '#FF6B6B')}
            </div>
            <p class="main-header">Movie Recommendation System</p>
            <p class="sub-header">Discover your next favorite movie with AI-powered recommendations</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Load data and models
    with st.spinner('Loading data and models...'):
        movies, ratings = load_data()
        models = load_models()
    
    # Sidebar
    st.sidebar.markdown(f'''
        <div style="text-align:center; padding:1rem;">
            <div class="icon-text" style="justify-content:center; font-size:1.5rem; font-weight:bold;">
                {get_svg_icon('settings', 24, '#4ECDC4')}
                <span>Settings</span>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Select Mode:",
        [
            f"Search & Recommend",
            f"User Recommendations",
            f"Model Comparison"
        ]
    )
    
    # Add icons to mode labels in display
    mode_icons = {
        "Search & Recommend": get_svg_icon('search', 18, '#FF6B6B'),
        "User Recommendations": get_svg_icon('user', 18, '#4ECDC4'),
        "Model Comparison": get_svg_icon('chart', 18, '#9B59B6')
    }
    
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
    st.markdown(f'''
        <div class="icon-text" style="margin-bottom:1rem;">
            {get_svg_icon('search', 32, '#FF6B6B')}
            <h2 style="display:inline; margin:0;">Search for a Movie</h2>
        </div>
    ''', unsafe_allow_html=True)
    
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
                st.markdown(f'''
                    <div class="icon-text" style="margin:1.5rem 0 1rem 0;">
                        {get_svg_icon('movie', 28, '#4ECDC4')}
                        <h3 style="display:inline; margin:0;">Selected Movie</h3>
                    </div>
                ''', unsafe_allow_html=True)
                selected_movie = movies[movies['movieId'] == selected_movie_id].iloc[0]
                display_movie_card(selected_movie)
                
                # Get recommendations
                st.markdown("---")
                st.markdown(f'''
                    <div class="icon-text" style="margin:1.5rem 0 1rem 0;">
                        {get_svg_icon('target', 28, '#9B59B6')}
                        <h3 style="display:inline; margin:0;">Recommendations from {model_name}</h3>
                    </div>
                ''', unsafe_allow_html=True)
                
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
    st.markdown(f'''
        <div class="icon-text" style="margin-bottom:1rem;">
            {get_svg_icon('user', 32, '#4ECDC4')}
            <h2 style="display:inline; margin:0;">User-Based Recommendations</h2>
        </div>
    ''', unsafe_allow_html=True)
    
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
    st.markdown(f'''
        <div class="icon-text" style="margin-bottom:1rem;">
            {get_svg_icon('chart', 32, '#9B59B6')}
            <h2 style="display:inline; margin:0;">Model Comparison</h2>
        </div>
    ''', unsafe_allow_html=True)
    
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
