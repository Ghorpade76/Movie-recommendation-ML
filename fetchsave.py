import pickle
import pandas as pd
import requests
from tqdm import tqdm

# --- MOVIES TO PRE-CACHE FOR THE DEMO ---
# You can change these to any movies you want to showcase during your presentation.
DEMO_MOVIES = ["Avatar", "The Dark Knight Rises", "Fight Club", "Inception", "Iron Man", "Spectre", "Dead Poets Society"]
# -----------------------------------------

def fetch_poster_from_api(movie_id):
    """A direct API call to fetch a poster URL."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url, timeout=10)
        data.raise_for_status()
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except requests.exceptions.RequestException as e:
        print(f"Skipping movie ID {movie_id}: {e}")
    return None

def get_recommendation_ids(movie_title, movies_df, similarity_matrix):
    """Gets the movie_ids for a movie and its top 5 recommendations."""
    try:
        idx = movies_df[movies_df['title'] == movie_title].index[0]
        distances = sorted(list(enumerate(similarity_matrix[idx])), reverse=True, key=lambda x: x[1])
        
        # Get the source movie ID + 5 recommendation IDs
        ids_to_fetch = [movies_df.iloc[idx].movie_id]
        for i in distances[1:6]:
            ids_to_fetch.append(movies_df.iloc[i[0]].movie_id)
        return ids_to_fetch
    except IndexError:
        print(f"Warning: '{movie_title}' not found in the dataset.")
        return []

if __name__ == '__main__':
    print("Loading model files...")
    movies = pd.DataFrame(pickle.load(open('artifacts/movie_dict.pkl', 'rb')))
    similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

    # Get a unique set of all movie IDs to fetch for the demo
    all_movie_ids_to_cache = set()
    print("Finding movies and their recommendations...")
    for movie_title in DEMO_MOVIES:
        ids = get_recommendation_ids(movie_title, movies, similarity)
        all_movie_ids_to_cache.update(ids)

    poster_cache = {}
    print(f"Fetching {len(all_movie_ids_to_cache)} posters for the demo kit...")
    
    # Use tqdm for a cool progress bar
    for movie_id in tqdm(all_movie_ids_to_cache, desc="Fetching posters"):
        poster_url = fetch_poster_from_api(movie_id)
        if poster_url:
            poster_cache[movie_id] = poster_url
    
    # Save the cache to a file
    with open('artifacts/poster_cache.pkl', 'wb') as f:
        pickle.dump(poster_cache, f)
        
    print(f"\nDone! Saved {len(poster_cache)} poster URLs to 'artifacts/poster_cache.pkl'.")
    print("You are now ready to run the main app in Demo Mode.")

