from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from rake_nltk import Rake
from threading import Lock
import numpy as np
import pandas as pd
from functools import lru_cache
import joblib
import os

class HybridRecommender:
    def __init__(self):
        self._model = None
        self._embeddings_lock = Lock()
        self._song_embeddings = None
        self._book_embeddings = None
        self._user_cache = {}
        self._embedding_cache_file = 'embedding_cache.joblib'
        
        # Initialize tools
        self.analyzer = SentimentIntensityAnalyzer()
        self.rake = Rake()
        self.scaler = MinMaxScaler()
        
        # Load datasets
        self.books_df = pd.read_csv('goodreads_data.csv', usecols=['Book', 'Author', 'Avg_Rating', 'Genres', 'URL', 'Description'])
        self.books_df['Description'] = self.books_df['Description'].fillna('').astype(str)
        
        self.songs_df = pd.read_csv('songs_data.csv')
        self.users_df = pd.read_csv('User.csv')
        
        # Initialize feedback data if not exists
        self.initialize_feedback_system()
        
        # Preprocess song features
        self.song_features = ['danceability', 'energy', 'valence', 'tempo', 'acousticness', 'instrumentalness', 'liveness', 'loudness']
        self.songs_df[self.song_features] = self.scaler.fit_transform(self.songs_df[self.song_features])

    def initialize_feedback_system(self):
        """Initialize the feedback system and create necessary files if they don't exist."""
        feedback_file = 'user_feedback.csv'
        if not os.path.exists(feedback_file):
            feedback_df = pd.DataFrame(columns=[
                'username', 'book_title', 'liked', 'clicked', 'saved', 
                'shared', 'timestamp'
            ])
            feedback_df.to_csv(feedback_file, index=False)
        self.feedback_df = pd.read_csv(feedback_file)

        bool_columns = ['liked', 'clicked', 'saved', 'shared']
        for col in bool_columns:
            self.feedback_df[col] = self.feedback_df[col].fillna(False).astype(bool)
        
        # Ensure timestamp column is datetime
        self.feedback_df['timestamp'] = pd.to_datetime(self.feedback_df['timestamp'])

    

    def add_user_feedback(self, username, book_title, feedback_type, value=True):
        """Add user feedback for a book."""
        print(f"\n=== Adding User Feedback ===")
        print(f"Username: {username}")
        print(f"Book Title: {book_title}")
        print(f"Feedback Type: {feedback_type}")
        print(f"Value: {value}")
        timestamp = pd.Timestamp.now()
        print(f"Timestamp: {timestamp}")
        
        # Check if feedback already exists
        mask = (self.feedback_df['username'] == username) & \
               (self.feedback_df['book_title'] == book_title)
        
        print(f"Checking existing feedback...")
        print(f"Found existing feedback: {len(self.feedback_df[mask]) > 0}")
        
        if len(self.feedback_df[mask]) > 0:
            # Update existing feedback
            print("Updating existing feedback...")
            self.feedback_df.loc[mask, feedback_type] = value
            self.feedback_df.loc[mask, 'timestamp'] = timestamp
            print("Existing feedback updated")

            # Update feedback score
            feedback = self.feedback_df.loc[mask].iloc[0]
            score = self.calculate_feedback_score(feedback)
            self.feedback_df.loc[mask, 'feedback_score'] = score
        else:
            # Create new feedback entry
            print("Creating new feedback entry...")
            new_feedback = {
                'username': username,
                'book_title': book_title,
                'liked': False,
                'clicked': False,
                'saved': False,
                'shared': False,
                'timestamp': timestamp,
                'feedback_score': 0.0
            }
            new_feedback[feedback_type] = value
            print(f"New feedback entry: {new_feedback}")
            # Calculate feedback score
            score = self.calculate_feedback_score(pd.Series(new_feedback))
            new_feedback['feedback_score'] = score
            
            self.feedback_df = pd.concat([self.feedback_df, pd.DataFrame([new_feedback])], 
                                       ignore_index=True)
            
            print("New feedback added to DataFrame")
        # Save feedback to file
        print("Saving feedback to file...")
        self.feedback_df.to_csv('user_feedback.csv', index=False)
        return True

    def get_user_feedback_score(self, username, book_title):
        """Calculate a feedback score for a book based on user interactions."""
        mask = (self.feedback_df['username'] == username) & \
               (self.feedback_df['book_title'] == book_title)
        
        if len(self.feedback_df[mask]) > 0:
            feedback = self.feedback_df[mask].iloc[0]
            return {
                'liked': bool(feedback['liked']),
                'saved': bool(feedback['saved']),
                'shared': bool(feedback['shared']),
                'clicked': bool(feedback['clicked'])
            }
        return {
            'liked': False,
            'saved': False,
            'shared': False,
            'clicked': False
        }


    def calculate_feedback_score(self, feedback):
        """Calculate a weighted score based on user interactions."""
        score = 0.0
        
        # Weight different types of feedback
        if feedback['liked']:
            score += 40  # Highest weight for explicit likes
        if feedback['saved']:
            score += 30  # High weight for saves (showing interest)
        if feedback['shared']:
            score += 20  # Medium weight for shares
        if feedback['clicked']:
            score += 10  # Lower weight for clicks
            
        # Normalize to 0-100 scale
        return min(score, 100)
    
    def get_user_feedback_score(self, username, book_title):
        """Get the normalized feedback score for a book."""
        mask = (self.feedback_df['username'] == username) & \
               (self.feedback_df['book_title'] == book_title)
        
        if len(self.feedback_df[mask]) == 0:
            return 0
        
        return float(self.feedback_df[mask].iloc[0]['feedback_score'])
    

    def get_similar_books_by_feedback(self, username, book_title, n=5):
        """Find similar books based on user feedback patterns."""
        # Get users who liked this book
        liked_mask = (self.feedback_df['book_title'] == book_title) & \
                    (self.feedback_df['liked'] == True)
        users_who_liked = set(self.feedback_df[liked_mask]['username'])
        
        if not users_who_liked:
            return []
        
        # Find books these users also liked
        similar_books = []
        for user in users_who_liked:
            user_likes = self.feedback_df[
                (self.feedback_df['username'] == user) & 
                (self.feedback_df['liked'] == True) & 
                (self.feedback_df['book_title'] != book_title)
            ]['book_title']
            similar_books.extend(user_likes)
        
        # Count occurrences and get top N
        if not similar_books:
            return []
            
        book_counts = pd.Series(similar_books).value_counts()
        return book_counts.head(n).index.tolist()
    
    def load_model(self):
        if self._model is None:
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._model

    def get_song_embeddings(self):
        with self._embeddings_lock:
            if self._song_embeddings is None:
                cache_path = 'song_embeddings.joblib'
                if os.path.exists(cache_path):
                    self._song_embeddings = joblib.load(cache_path)
                else:
                    self._song_embeddings = self.load_model().encode(self.songs_df['genre'].tolist())
                    joblib.dump(self._song_embeddings, cache_path)
            return self._song_embeddings

    def get_book_embeddings(self):
        with self._embeddings_lock:
            if self._book_embeddings is None:
                cache_path = 'book_embeddings.joblib'
                if os.path.exists(cache_path):
                    self._book_embeddings = joblib.load(cache_path)
                else:
                    descriptions = self.books_df['Description'].fillna('').tolist()
                    self._book_embeddings = self.load_model().encode(descriptions)
                    joblib.dump(self._book_embeddings, cache_path)
            return self._book_embeddings

    def clean_recommendations(self, recommendations):
        if pd.isna(recommendations) or recommendations == '':
            return set()
        
        if isinstance(recommendations, list):
            books = recommendations
        else:
            try:
                books = eval(recommendations) if '[' in recommendations else recommendations.split(',')
            except:
                books = recommendations.split(',')
        
        return {str(book).strip() for book in books if book}

    def get_user_info(self, username):
        if username not in self._user_cache:
            user_info = self.users_df[self.users_df['User name'] == username].iloc[0]
            self._user_cache[username] = {
                'genres': frozenset(genre.strip() for genre in user_info['Genre'].split(',')),
                'notes': user_info['Notes'],
                'recommendations': self.clean_recommendations(user_info['Recommended Books'])
            }
        return self._user_cache[username]
    
    def calculate_genre_match(self, book_genres, preferred_genres):
        if pd.isna(book_genres):
            return 0
            
        book_genre_set = set(g.strip().lower() for g in book_genres.split(','))
        preferred_genres = set(g.lower() for g in preferred_genres)
        
        # Direct matches (full weight)
        direct_matches = book_genre_set.intersection(preferred_genres)
        direct_score = len(direct_matches) * 1.0
        
        # Enhanced partial matches with more sophisticated scoring
        partial_score = 0
        for book_genre in book_genre_set:
            words_book = set(book_genre.split())
            for pref_genre in preferred_genres:
                words_pref = set(pref_genre.split())
                common_words = words_book.intersection(words_pref)
                if common_words:
                    word_similarity = len(common_words) / max(len(words_book), len(words_pref))
                    partial_score += word_similarity * 0.7  # 70% weight for partial matches
        
        # Consider genre hierarchy (e.g., "epic fantasy" matches with "fantasy")
        hierarchy_score = 0
        for book_genre in book_genre_set:
            for pref_genre in preferred_genres:
                if (book_genre in pref_genre or pref_genre in book_genre) and \
                   book_genre != pref_genre and \
                   len(min(book_genre, pref_genre)) > 3:
                    hierarchy_score += 0.5
        
        total_score = direct_score + partial_score + hierarchy_score
        max_possible_score = max(len(preferred_genres), len(book_genre_set))
        
        # Boost score if there's at least one perfect match
        if direct_matches:
            total_score *= 1.2
        
        return min((total_score / max_possible_score) * 100, 100)

    
        

    def normalize_score(self, score, min_threshold=60):  # Increased minimum threshold
        if isinstance(score, np.ndarray):
            # Clip values to ensure minimum threshold
            normalized = min_threshold + (100 - min_threshold) * (score - score.min()) / (score.max() - score.min() + 1e-10)
            return np.clip(normalized, min_threshold, 100)
        else:
            return min_threshold + (100 - min_threshold) * (score / 100)




    def recommend_books_for_user(self, username, debug=False):
        """Enhanced recommendation function incorporating user feedback."""
        if username not in self.users_df['User name'].values:
            return {"error": f"User '{username}' not found."}

        user_info = self.get_user_info(username)
        preferred_genres = user_info['genres']
        notes = user_info['notes']
        recommended_books = user_info['recommendations']

        # Calculate genre matches and filter
        genre_matches = []
        for book_idx, book_genres in enumerate(self.books_df['Genres']):
            match_score = self.calculate_genre_match(book_genres, preferred_genres)
            if match_score > 40:
                genre_matches.append((book_idx, match_score))

        if not genre_matches:
            return {"error": f"No unrecommended books found for genres: {', '.join(preferred_genres)}."}

        matched_indices = [idx for idx, _ in genre_matches]
        filtered_books = self.books_df.iloc[matched_indices].copy()
        genre_scores = np.array([score for _, score in genre_matches])

        # Remove recommended books
        mask = ~filtered_books['Book'].isin(recommended_books)
        filtered_books = filtered_books[mask]
        genre_scores = genre_scores[mask]

        if filtered_books.empty:
            return {"error": "No unrecommended books found matching your preferences."}

        # Calculate content similarity
        user_embedding = self.load_model().encode([notes])
        filtered_embeddings = self.get_book_embeddings()[filtered_books.index]
        
        cosine_sim = cosine_similarity(user_embedding, filtered_embeddings)[0]
        notes_scores = self.normalize_score(cosine_sim * 100)
        genre_scores = self.normalize_score(genre_scores)
        
        # Add feedback scores
        feedback_scores = np.array([
            self.get_user_feedback_score(username, book_title)
            for book_title in filtered_books['Book']
        ])
        feedback_scores = self.normalize_score(feedback_scores)
        
         # Get collaborative filtering recommendations
        similar_books = set()
        for book_title in filtered_books['Book']:
            similar_books.update(self.get_similar_books_by_feedback(username, book_title))
        
        # Boost scores for collaborative filtering recommendations
        collab_boost = np.zeros_like(feedback_scores)
        for i, book in enumerate(filtered_books['Book']):
            if book in similar_books:
                collab_boost[i] = 30  # Boost score by 20 points
        
        # Combine all scores
        final_scores = (
            notes_scores * 0.35 +      # Content-based
            genre_scores * 0.35 +      # Genre matching
            feedback_scores * 0.2 +   # User feedback
            collab_boost * 0.1        # Collaborative filtering boost
        )
        
        final_scores = self.normalize_score(final_scores, min_threshold=70)
        best_match_idx = np.argmax(final_scores)
        most_similar_book = filtered_books.iloc[best_match_idx]
        
        # Update recommendations
        new_book = most_similar_book['Book']
        if new_book not in recommended_books:
            recommended_books.add(new_book)
            self.users_df.loc[self.users_df['User name'] == username, 'Recommended Books'] = str(list(recommended_books))
            self.users_df.to_csv('User.csv', index=False)
            self._user_cache[username]['recommendations'] = recommended_books

        playlist = self.recommend_playlist_for_book(most_similar_book['Description'])

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
                "genre_match": round(float(genre_scores[best_match_idx]), 1),
                "feedback_match": round(float(feedback_scores[best_match_idx]), 1)
            },
            "playlist": playlist
        }

    
    
    def recommend_playlist_for_book(self, book_description):
        sentiment_score = self.analyzer.polarity_scores(book_description)['compound']
        sentiment_adjustment = (sentiment_score + 1) / 2

        book_embedding = self.load_model().encode([book_description])
        vibe_similarity = cosine_similarity(book_embedding, self.get_song_embeddings())
        adjusted_similarity = vibe_similarity * sentiment_adjustment

        top_song_indices = adjusted_similarity.argsort()[0][-5:][::-1]
        top_songs = self.songs_df.iloc[top_song_indices]

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

# Initialize global recommender
recommender = HybridRecommender()


# Interface functions
def recommend_books_for_user(username, debug=False):
    return recommender.recommend_books_for_user(username, debug)

def recommend_playlist_for_book(book_description):
    return recommender.recommend_playlist_for_book(book_description)