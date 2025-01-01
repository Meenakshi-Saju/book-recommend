import re
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from rake_nltk import Rake
from functools import lru_cache
from threading import Lock
import joblib
import os



# Global caches
_model = None
_embeddings_lock = Lock()
_song_embeddings = None
_book_embeddings = None
_user_cache = {}
_embedding_cache_file = 'embedding_cache.joblib'

def load_model():
    """Lazy load the SBERT model"""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

# Initialize lightweight tools
analyzer = SentimentIntensityAnalyzer()
rake = Rake()
scaler = MinMaxScaler()

# Load and preprocess datasets efficiently
books_df = pd.read_csv('goodreads_data.csv', usecols=['Book', 'Author', 'Avg_Rating', 'Genres', 'URL', 'Description'])
books_df['Description'] = books_df['Description'].fillna('').astype(str)

songs_df = pd.read_csv('songs_data.csv')
users_df = pd.read_csv('User.csv')

# Preprocess song features once
song_features = ['danceability', 'energy', 'valence', 'tempo', 'acousticness', 'instrumentalness', 'liveness', 'loudness']
songs_df[song_features] = scaler.fit_transform(songs_df[song_features])

def get_song_embeddings():
    """Lazy load song embeddings with caching"""
    global _song_embeddings
    with _embeddings_lock:
        if _song_embeddings is None:
            cache_path = 'song_embeddings.joblib'
            if os.path.exists(cache_path):
                _song_embeddings = joblib.load(cache_path)
            else:
                model = load_model()
                _song_embeddings = model.encode(songs_df['genre'].tolist())
                joblib.dump(_song_embeddings, cache_path)
        return _song_embeddings

def get_book_embeddings():
    """Lazy load book embeddings with caching"""
    global _book_embeddings
    with _embeddings_lock:
        if _book_embeddings is None:
            cache_path = 'book_embeddings.joblib'
            if os.path.exists(cache_path):
                _book_embeddings = joblib.load(cache_path)
            else:
                model = load_model()
                descriptions = books_df['Description'].fillna('').tolist()
                _book_embeddings = model.encode(descriptions)
                joblib.dump(_book_embeddings, cache_path)
        return _book_embeddings

@lru_cache(maxsize=128)
def extract_keywords_rake(text):
    rake.extract_keywords_from_text(text)
    return tuple(rake.get_ranked_phrases())

@lru_cache(maxsize=128)
def analyze_sentiment_vader(text):
    return analyzer.polarity_scores(text)['compound']

def clean_recommendations(recommendations):
    if pd.isna(recommendations) or recommendations == '':
        return []
    
    if isinstance(recommendations, list):
        books = recommendations
    else:
        try:
            books = eval(recommendations) if '[' in recommendations else recommendations.split(',')
        except:
            books = recommendations.split(',')
    
    seen = set()
    return [str(book).strip() for book in books if book and book not in seen and not seen.add(book)]

def get_user_info(username):
    """Cache and retrieve user information"""
    if username not in _user_cache:
        user_info = users_df[users_df['User name'] == username].iloc[0]
        _user_cache[username] = {
            'genres': frozenset(genre.strip() for genre in user_info['Genre'].split(',')),
            'notes': user_info['Notes'],
            'recommendations': set(clean_recommendations(user_info['Recommended Books']))
        }
    return _user_cache[username]

def calculate_genre_match(book_genres, preferred_genres):
    """Calculate genre match percentage with improved scoring"""
    book_genre_set = set(g.strip().lower() for g in book_genres.split(','))
    preferred_genres = set(g.lower() for g in preferred_genres)
    
    # Calculate both direct and partial matches
    direct_matches = book_genre_set.intersection(preferred_genres)
    
    # Calculate partial matches (e.g., "fantasy" matches with "dark fantasy")
    partial_matches = set()
    for book_genre in book_genre_set:
        for pref_genre in preferred_genres:
            if (book_genre in pref_genre or pref_genre in book_genre) and \
               book_genre != pref_genre and \
               len(min(book_genre, pref_genre)) > 3:  # Avoid matching too short strings
                partial_matches.add((book_genre, pref_genre))
    
    # Weight direct matches more heavily than partial matches
    match_score = (len(direct_matches) * 1.0 + len(partial_matches) * 0.5)
    max_possible_score = max(len(preferred_genres), len(book_genre_set))
    
    return min((match_score / max_possible_score) * 100, 100)  # Cap at 100%

def normalize_score(score, min_threshold=40):
    """Normalize scores to ensure a minimum threshold"""
    return min_threshold + (100 - min_threshold) * (score / 100)


def recommend_books_for_user(username, debug=False):
    if username not in users_df['User name'].values:
        return {"error": f"User '{username}' not found."}

    # Get cached user info
    user_info = get_user_info(username)
    preferred_genres = user_info['genres']
    notes = user_info['notes']
    recommended_books = user_info['recommendations']

    # Enhanced genre filtering with fuzzy matching
    genre_matches = []
    for book_idx, book_genres in enumerate(books_df['Genres']):
        if pd.isna(book_genres):
            continue
        match_score = calculate_genre_match(book_genres, preferred_genres)
        if match_score > 30:  # Lower threshold for initial filtering
            genre_matches.append((book_idx, match_score))
    
    if not genre_matches:
        return {"error": f"No unrecommended books found for genres: {', '.join(preferred_genres)}."}
    
    # Convert to filtered dataframe
    matched_indices = [idx for idx, _ in genre_matches]
    filtered_books = books_df.iloc[matched_indices].copy()
    genre_scores = np.array([score for _, score in genre_matches])
    
    # Remove already recommended books
    mask = ~filtered_books['Book'].isin(recommended_books)
    filtered_books = filtered_books[mask]
    genre_scores = genre_scores[mask]
    
    if filtered_books.empty:
        return {"error": "No unrecommended books found matching your preferences."}

    # Enhanced text similarity calculation
    user_embedding = load_model().encode([notes])
    filtered_embeddings = get_book_embeddings()[filtered_books.index]
    
    # Calculate cosine similarity
    cosine_sim = cosine_similarity(user_embedding, filtered_embeddings)[0]
    
    # Normalize similarity scores using numpy arrays instead of pandas Series
    notes_scores = normalize_score(cosine_sim * 100)
    genre_scores = normalize_score(genre_scores)
    
    # Calculate weighted final scores
    final_scores = (
        notes_scores * 0.6 +  # Increased weight for content matching
        genre_scores * 0.4    # Genre matching weight
    )
    
    # Get best match using numpy instead of pandas
    best_match_idx = np.argmax(final_scores)
    most_similar_book = filtered_books.iloc[best_match_idx]
    
    # Update recommendations and save
    new_book = most_similar_book['Book']
    if new_book not in recommended_books:
        recommended_books.add(new_book)
        users_df.loc[users_df['User name'] == username, 'Recommended Books'] = str(list(recommended_books))
        users_df.to_csv('User.csv', index=False)
        _user_cache[username]['recommendations'] = recommended_books

    # Get playlist recommendation
    playlist = recommend_playlist_for_book(most_similar_book['Description'])

    return {
        "book": {
            "title": most_similar_book['Book'],
            "author": most_similar_book['Author'],
            "rating": most_similar_book['Avg_Rating'],
            "genre": most_similar_book['Genres'],
            "url": most_similar_book['URL'],
            "description": most_similar_book['Description']
        },
        "match_scores": {
            "overall_match": round(float(final_scores[best_match_idx]), 1),
            "notes_match": round(float(notes_scores[best_match_idx]), 1),
            "genre_match": round(float(genre_scores[best_match_idx]), 1)
        },
        "playlist": playlist
    }


@lru_cache(maxsize=64)
def recommend_playlist_for_book(book_description):
    sentiment_score = analyze_sentiment_vader(book_description)
    sentiment_adjustment = (sentiment_score + 1) / 2

    book_embedding = load_model().encode([book_description])
    vibe_similarity = cosine_similarity(book_embedding, get_song_embeddings())
    adjusted_similarity = vibe_similarity * sentiment_adjustment

    top_song_indices = adjusted_similarity.argsort()[0][-5:][::-1]
    top_songs = songs_df.iloc[top_song_indices]

    return [
        {
            "song": row['song'],
            "artist": row['artist'],
            "year": row['year'],
            "popularity": row['popularity'],
            "danceability": row['danceability'],
            "energy": row['energy'],
            "valence": row['valence'],
            "tempo": row['tempo'],
            "genre": row['genre']
        }
        for _, row in top_songs.iterrows()
    ]

def recommend_playlist_for_book_entered_by_user(book_name):
    book_data = books_df[books_df['Book'].str.lower() == book_name.lower()]
    
    if book_data.empty:
        print("Book not found in database.")
        return []
    
    return recommend_playlist_for_book(book_data.iloc[0]['Description'])