import requests

# A simple script to test network connectivity from Python.

def check_connection():
    """Attempts to connect to Google and the TMDB API."""
    
    # --- Test Connection to Google ---
    try:
        print("Attempting to connect to Google...")
        google_url = "https://www.google.com"
        r_google = requests.get(google_url, timeout=10)
        r_google.raise_for_status()  # Raise an exception for bad status codes
        print(f"SUCCESS: Connected to Google with status code {r_google.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"FAILED to connect to Google. Error: {e}")
        print("-" * 20)
        return

    # --- Test Connection to TMDB API ---
    try:
        print("\nAttempting to connect to The Movie Database (TMDB)...")
        # Using a valid movie ID (Fight Club) for the test
        tmdb_url = "https://api.themoviedb.org/3/movie/550?api_key=8265bd1679663a7ea12ac168da84d2e8"
        r_tmdb = requests.get(tmdb_url, timeout=10)
        r_tmdb.raise_for_status()
        print(f"SUCCESS: Connected to TMDB with status code {r_tmdb.status_code}")
        print("Network connection seems to be working correctly!")

    except requests.exceptions.RequestException as e:
        print(f"FAILED to connect to TMDB. Error: {e}")
        print("This indicates something is specifically blocking the connection to the TMDB API.")

    print("-" * 20)

if __name__ == "__main__":
    check_connection()
