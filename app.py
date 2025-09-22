'''
Author: Bappy Ahmed
Email: entbappy73@gmail.com
Date: 2021-Nov-15
Updated by: Malhar Nikam & Team (with Smart Caching)
'''

import pickle
import streamlit as st
import requests
import pandas as pd
import os

# --- Smart Poster Fetcher with Hybrid Caching ---
def fetch_poster(movie_id):
    """
    Fetches a movie poster with a smart hybrid strategy:
    1. Tries to get the poster from a local "demo kit" cache first.
    2. If not in the cache, tries to fetch it live from the TMDB API.
    3. If the API fails, returns a clean placeholder image.
    """
    # 1. Check local cache first (for demo mode)
    if 'poster_cache' in globals() and movie_id in poster_cache:
        return poster_cache[movie_id]
    
    # 2. If not in cache, try fetching live from API
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url, timeout=5)
        data.raise_for_status()
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
    except requests.exceptions.RequestException:
        # 3. Graceful fallback if API fails
        return "https://placehold.co/500x750/333/FFFFFF?text=Poster+Not+Available"
    
    # This is a fallback in case the API call works but there's no poster path.
    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"


def recommend(movie):
    """Recommends 5 similar movies based on the selected movie."""
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset.")
        return [], [], [], []
        
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_years = []
    recommended_movie_ratings = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_years.append(movies.iloc[i[0]].year)
        recommended_movie_ratings.append(movies.iloc[i[0]].vote_average)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings

# --- App Layout ---
st.set_page_config(layout="wide")
st.header('Movie Recommender System Using Machine Learning')

# --- Data Loading ---
try:
    movies_dict = pickle.load(open('artifacts/movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Model files not found. Please run the data processing notebook first.")
    st.stop()

# Load the poster cache if it exists for "Demo Mode"
poster_cache_path = 'artifacts/poster_cache.pkl'
if os.path.exists(poster_cache_path):
    poster_cache = pickle.load(open(poster_cache_path, 'rb'))
    st.sidebar.success("✅ Demo Mode Active: Posters loaded from local cache.")
else:
    st.sidebar.warning("⚠️ Live API Mode: Some posters may not load on restricted networks.")


# --- UI Elements ---
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    with st.spinner('Finding recommendations...'):
        recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings = recommend(selected_movie)
    
    if recommended_movie_names:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])
                year = recommended_movie_years[i]
                if pd.notna(year):
                    st.caption(f"Year: {int(year)}")
                else:
                    st.caption("Year: N/A")
                
                rating = recommended_movie_ratings[i]
                st.caption(f"Rating: {rating:.1f} ⭐")

