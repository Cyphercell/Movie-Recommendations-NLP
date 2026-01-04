import pickle
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
import re

# Load data
with open("movie_dict.pkl", "rb") as f:
    data = pickle.load(f)

# Page config
st.set_page_config(page_title="FlixRecommend", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Netflix-like dark theme and horizontal scrolling rows
st.markdown("""
<style>
    /* Main dark background */
    .stApp {
        background-color: #000000;
        color: #e5e5e5;
    }
    h1, h2, h3, h4 {
        color: #e50914 !important;  /* Netflix red */
        font-weight: bold;
    }
    .movie-title {
        color: white;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 10px;
    }
    .genre-caption {
        color: #b3b3b3;
        font-size: 0.9rem;
        text-align: center;
    }
    /* Horizontal scroll container */
    .scroll-container {
        overflow-x: auto;
        white-space: nowrap;
        padding: 10px 0;
        scrollbar-width: thin;
    }
    .scroll-container::-webkit-scrollbar {
        height: 8px;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        background-color: #333;
        border-radius: 10px;
    }
    /* Card style */
    .movie-card {
        display: inline-block;
        width: 200px;
        margin-right: 15px;
        vertical-align: top;
    }
    /* Hide sidebar and menu */
    [data-testid="stSidebar"] {display: none;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center;'>🍿 FlixRecommend</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Discover your next favorite movie</h3>", unsafe_allow_html=True)

# Recommendation function
def recommend(movie, n=20):
    movie_dictionary = data["movie_dict"]
    if movie in movie_dictionary:
        movie_vector = movie_dictionary[movie]
        cosine_dict = {}
        for i, j in movie_dictionary.items():
            if i != movie:
                cosine_dict[i] = cosine_similarity(movie_vector, j)[0][0]
        result = sorted(cosine_dict.items(), key=lambda x: x[1], reverse=True)
        return [i[0] for i in result[:n]]
    else:
        return None

# Improved high-quality poster
def get_high_quality_image(url, width=400, height=600):
    url = re.sub(r"\._[A-Z0-9_]+_\.", ".", url)  # Remove quality reducers
    url = url.replace("UX67", f"UX{width}").replace("UY98", f"UY{height}")
    url = url.replace("CR0,0,67,98", f"CR0,0,{width},{height}")
    if "CR" in url:
        url = re.sub(r"CR\d+,\d+,\d+,\d+", f"CR0,0,{width},{height}", url)
    return url

# Search bar + selectbox
movies_list = sorted(data['movie_dict'].keys())
selected_movie = st.selectbox("🔍 Search for a movie you love:", movies_list, index=None, placeholder="Type or select a movie...")

if selected_movie:
    # Show selected movie large poster
    df = data["df"]
    sel_row = df[df["Series_Title"] == selected_movie].iloc[0]
    sel_poster = get_high_quality_image(sel_row["Poster_Link"], width=500, height=750)
    sel_genre = sel_row["Genre"]
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(sel_poster, use_column_width=True)
        st.markdown(f"<h2 style='text-align: center; color: white;'>{selected_movie}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #b3b3b3;'>Genre: {sel_genre}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get recommendations
    recommendations = recommend(selected_movie, n=20)
    if recommendations:
        st.markdown("<h2 style='color: #e50914;'>Because you liked this, you might enjoy...</h2>", unsafe_allow_html=True)
        
        # Horizontal scrolling row
        st.markdown("<div class='scroll-container'>", unsafe_allow_html=True)
        
        scroll_cols = st.columns(10)  # Dummy columns to force layout, but we'll use HTML for real scroll
        # Better: use direct HTML for cards inside scroll container
        cards_html = ""
        for movie_name in recommendations:
            row = df[df["Series_Title"] == movie_name].iloc[0]
            poster = get_high_quality_image(row["Poster_Link"], width=300, height=450)
            genre = row["Genre"]
            cards_html += f"""
            <div class='movie-card'>
                <img src='{poster}' style='width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.6);'>
                <div class='movie-title'>{movie_name}</div>
                <div class='genre-caption'>{genre}</div>
            </div>
            """
        
        st.markdown(cards_html, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Movie not found in database.")

# Footer
st.markdown("<br><p style='text-align: center; color: #666;'>Powered by your movie data • Netflix-inspired UI</p>", unsafe_allow_html=True)