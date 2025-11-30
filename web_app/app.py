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

# Custom CSS - Enhanced Premium Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Container Background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Header Styles with Gradient */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: fadeInDown 0.8s ease-in;
    }
    
    .sub-header {
        font-size: 1.3rem;
        text-align: center;
        color: #ffffff;
        margin-bottom: 2rem;
        font-weight: 300;
        animation: fadeInUp 0.8s ease-in;
    }
    
    /* Movie Card with Glassmorphism */
    .movie-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    
    .movie-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(180deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
        transform: translateY(-2px);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #f5576c;
        box-shadow: 0 0 0 3px rgba(245, 87, 108, 0.1);
    }
    
    /* Select Boxes */
    .stSelectbox>div>div {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
    }
    
    /* Info Boxes */
    .stAlert {
        border-radius: 15px;
        border-left: 5px solid #667eea;
        background-color: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #0d47a1;
        border-radius: 15px;
        padding: 1rem;
        font-weight: 500;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #e65100;
        border-radius: 15px;
        padding: 1rem;
        font-weight: 500;
    }
    
    .stError {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #b71c1c;
        border-radius: 15px;
        padding: 1rem;
        font-weight: 500;
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #f5576c !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        font-weight: 600;
    }
    
    /* Metrics (Streamlit native) */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #666;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* Card Title Styles */
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-subtitle {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    
    /* Badge Styles */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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


def display_movie_card(movie_data, show_similarity=False, similarity_score=None, rank=None):
    """Display an enhanced movie card with details."""
    with st.container():
        st.markdown('<div class="movie-card">', unsafe_allow_html=True)
        
        # Header with rank badge
        if rank:
            st.markdown(f'<span class="badge">#{rank}</span>', unsafe_allow_html=True)
        
        # Title with larger emphasis
        st.markdown(f'<div class="card-title">🎬 {movie_data["title_clean"]}</div>', unsafe_allow_html=True)
        
        # Year and genres on same line
        year_str = int(movie_data['year']) if pd.notna(movie_data['year']) else 'Unknown'
        st.markdown(f'<div class="card-subtitle">📅 {year_str} • 🎭 {movie_data["genres"]}</div>', unsafe_allow_html=True)
        
        # Metrics in columns
        metric_cols = st.columns(3)
        
        with metric_cols[0]:
            if pd.notna(movie_data['avg_rating']):
                rating_val = movie_data['avg_rating']
                # Star rating visual
                stars = "⭐" * int(rating_val)
                st.markdown(f"**Rating**")
                st.markdown(f"{stars} {rating_val:.2f}/5.0")
        
        with metric_cols[1]:
            if pd.notna(movie_data['num_ratings']):
                st.markdown(f"**Popularity**")
                st.markdown(f"👥 {int(movie_data['num_ratings']):,} ratings")
        
        with metric_cols[2]:
            if show_similarity and similarity_score is not None:
                st.markdown(f"**Match Score**")
                # Progress bar visual for similarity
                match_percent = int(similarity_score * 100)
                st.markdown(f"🎯 {similarity_score:.3f}")
                st.progress(similarity_score)
        
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    # Enhanced Header with Animation
    st.markdown('<p class="main-header">🎬 Movie Recommendation System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">✨ Discover your next favorite movie with AI-powered recommendations! ✨</p>', unsafe_allow_html=True)
    
    # Load data and models
    with st.spinner('🔄 Loading data and models...'):
        movies, ratings = load_data()
        models = load_models()
    
    # Enhanced Sidebar
    st.sidebar.markdown("### ⚙️ Control Panel")
    st.sidebar.markdown("---")
    
    # Mode selection with better labels
    mode = st.sidebar.radio(
        "🎯 Select Mode:",
        ["🔍 Search & Recommend", "👤 User Recommendations", "📊 Model Comparison"],
        help="Choose how you want to get recommendations"
    )
    
    st.sidebar.markdown("---")
    
    # Model selection with emojis
    model_name = st.sidebar.selectbox(
        "🤖 Recommendation Model:",
        list(models.keys()),
        help="Different models use different approaches"
    )
    
    # Show model info
    with st.sidebar.expander("ℹ️ Model Info"):
        if "TF-IDF" in model_name:
            st.info("Uses text similarity from titles and genres")
        elif "Genre" in model_name:
            st.info("Matches movies with same genres")
        elif "Combined" in model_name:
            st.info("Uses genres + ratings + metadata")
        elif "Item-Based" in model_name:
            st.info("Finds similar movies based on user ratings")
        elif "User-Based" in model_name:
            st.info("Recommends based on similar users")
    
    # Number of recommendations
    n_recommendations = st.sidebar.slider(
        "📊 Number of Results:",
        min_value=5,
        max_value=20,
        value=10,
        step=5,
        help="How many recommendations to show"
    )
    
    st.sidebar.markdown("---")
    
    # Dataset stats with metrics
    st.sidebar.markdown("### 📈 Dataset Statistics")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("🎬 Movies", f"{len(movies):,}")
        st.metric("⭐ Ratings", f"{len(ratings):,}")
    with col2:
        st.metric("👥 Users", f"{ratings['userId'].nunique():,}")
        avg_rating = ratings['rating'].mean()
        st.metric("📊 Avg Rating", f"{avg_rating:.2f}")
    
    st.sidebar.markdown("---")
    st.sidebar.success("✅ All systems ready!")
    
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
                        
                        # Display recommendations with enhanced cards
                        for idx, (_, rec) in enumerate(recs.iterrows(), 1):
                            movie_data = movies[movies['movieId'] == rec['movieId']].iloc[0]
                            
                            similarity_score = rec.get('similarity_score', rec.get('predicted_rating', None))
                            display_movie_card(movie_data, show_similarity=True, similarity_score=similarity_score, rank=idx)
                    
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
                
                # Display recommendations with enhanced cards
                for idx, (_, rec) in enumerate(recs.iterrows(), 1):
                    movie_data = movies[movies['movieId'] == rec['movieId']].iloc[0]
                    display_movie_card(movie_data, show_similarity=True, similarity_score=rec['predicted_rating'], rank=idx)
            
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
