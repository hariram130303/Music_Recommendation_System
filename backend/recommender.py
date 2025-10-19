#recommender.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack

# --- Data Loading and Feature Preparation ---
# This part is memory-efficient and can be done at startup.

# --- Data Loading and Feature Preparation ---
try:
    df = pd.read_csv('songs_2000_2020_50k.csv')

    # 1. Text feature (Genre)
    tfidf = TfidfVectorizer(stop_words='english')
    genre_matrix = tfidf.fit_transform(df['Genre'].fillna(''))

    # 2. Numerical features
    numerical_features = ['Popularity', 'Duration']
    scaler = MinMaxScaler()
    df[numerical_features] = df[numerical_features].fillna(df[numerical_features].mean())
    numerical_matrix = scaler.fit_transform(df[numerical_features])

    # 3. Combine + convert to CSR
    combined_features = hstack([genre_matrix, numerical_matrix]).tocsr()

    print("Recommender system initialized successfully.")
    is_ready = True

except FileNotFoundError:
    print("Error: 'songs_2000_2020_50k.csv' not found.")
    is_ready = False
except KeyError as e:
    print(f"Error: Missing expected column in CSV: {e}")
    is_ready = False


# --- Recommendation Function (Updated Logic) ---
def get_recommendations(song_title, num_recs=5):
    """
    Get music recommendations by calculating similarity on-the-fly.
    """
    if not is_ready:
        return {"error": "Recommender system is not ready. Check server logs."}
    
    try:
        # Find the index of the song
        song_idx = df[df['Title'].str.lower() == song_title.lower()].index[0]
        
        # Get the feature vector for the input song
        song_vector = combined_features[song_idx]

        # *** THE KEY CHANGE IS HERE ***
        # Calculate similarity between THIS song and ALL other songs
        sim_scores = cosine_similarity(song_vector, combined_features)
        
        # sim_scores is a 2D array, so we flatten it to a 1D list
        sim_scores = list(enumerate(sim_scores[0]))
        
        # Sort the songs based on similarity
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get the top N recommendations (excluding the song itself)
        sim_scores = sim_scores[1:num_recs + 1]
        
        # Get song indices
        song_indices = [i[0] for i in sim_scores]
        
        # Return the recommended songs
        recommendations = df[['Title', 'Artist']].iloc[song_indices]
        return recommendations.to_dict(orient='records')

    except (IndexError, KeyError):
        return {"error": "Song not found in the dataset. Please try another."}