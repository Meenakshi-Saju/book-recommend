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
from sklearn.metrics import precision_score, recall_score
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
        
        
        self.initialize_feedback_system()
        
        
        self.age_genre_mapping = {
            'under_18': ['Young Adult', 'Fantasy', 'Sci-Fi', 'Adventure', 'Children', 'Middle Grade'],
            '18_to_30': ['Mystery', 'Thriller', 'Contemporary Fiction', 'Romance', 'Science Fiction', 'Fantasy'],
            'over_30': ['Non-fiction', 'Historical Fiction', 'Literary Fiction', 'Biography', 'Self-Help', 'Business']
        }
        
        
        self.hobby_genre_mapping = {
            'reading': ['Literary Fiction', 'Classics', 'Poetry'],
            'gaming': ['Fantasy', 'Sci-Fi', 'Gaming', 'Adventure'],
            'sports': ['Sports', 'Biography', 'Fitness', 'Self-Help'],
            'cooking': ['Cookbooks', 'Food', 'Culinary', 'Memoir'],
            'travel': ['Travel', 'Adventure', 'Geography', 'Cultural'],
            'music': ['Music', 'Biography', 'History', 'Performing Arts'],
            'art': ['Art', 'Design', 'Photography', 'Creativity'],
            'writing': ['Writing', 'Essays', 'Poetry', 'Literary Criticism'],
            'technology': ['Technology', 'Science', 'Programming', 'Computer Science'],
            'gardening': ['Gardening', 'Nature', 'Plants', 'Home'],
            'history': ['History', 'Historical Fiction', 'Biography', 'Politics'],
            'science': ['Science', 'Physics', 'Biology', 'Astronomy'],
            'photography': ['Photography', 'Art', 'Design', 'Visual'],
            'movies': ['Film', 'Entertainment', 'Media Studies', 'Screenwriting'],
            'hiking': ['Outdoors', 'Nature', 'Adventure', 'Travel'],
            'yoga': ['Wellness', 'Spirituality', 'Health', 'Mindfulness'],
            'meditation': ['Spirituality', 'Self-Help', 'Psychology', 'Philosophy'],
            'crafts': ['Crafts', 'DIY', 'Art', 'Design'],
            'fashion': ['Fashion', 'Design', 'Style', 'Biography'],
            'painting': ['Art', 'Painting', 'Biography', 'Creativity']
        }
        
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

    def get_user_feedback(self, username, book_title):
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
            
            # Extract age and hobbies
            age = user_info['Age'] if 'Age' in user_info and pd.notna(user_info['Age']) else ''
            
            if 'Hobbies' in user_info and pd.notna(user_info['Hobbies']):
                hobbies = [h.strip().lower() for h in user_info['Hobbies'].split(',')]
            else:
                hobbies = []
                
            self._user_cache[username] = {
                'genres': frozenset(genre.strip() for genre in user_info['Genre'].split(',') if genre.strip()),
                'notes': str(user_info['Notes']) if pd.notna(user_info['Notes']) else '',
                'recommendations': self.clean_recommendations(user_info['Recommended Books']),
                'age': age,
                'hobbies': hobbies
            }
        return self._user_cache[username]
    
    def get_age_group(self, age):
        """Determine the age group of a user."""
        try:
            age = int(age)
            if age < 18:
                return 'under_18'
            elif age <= 30:
                return '18_to_30'
            else:
                return 'over_30'
        except (ValueError, TypeError):
            # If age is not provided or invalid, default to 18-30 range
            return '18_to_30'
    
    def get_age_appropriate_genres(self, age):
        """Get a list of genre preferences based on age."""
        age_group = self.get_age_group(age)
        return self.age_genre_mapping.get(age_group, [])
    
    def get_hobby_related_genres(self, hobbies):
        """Get a list of genre preferences based on hobbies."""
        related_genres = []
        for hobby in hobbies:
            hobby_lower = hobby.lower()
            for key, genres in self.hobby_genre_mapping.items():
                if key in hobby_lower or hobby_lower in key:
                    related_genres.extend(genres)
        
        # Return unique genres
        return list(set(related_genres))
        
    def calculate_genre_match(self, book_genres, preferred_genres, age_genres=None, hobby_genres=None):
        """
        Calculate how well a book's genres match the user's preferred genres,
        considering age and hobby appropriate genres as well.
        """
        if pd.isna(book_genres):
            return 0
            
        book_genre_set = set(g.strip().lower() for g in book_genres.split(','))
        preferred_genres = set(g.lower() for g in preferred_genres if g)
        
        # Add age and hobby appropriate genres to the preferred genres
        if age_genres:
            age_genres_set = set(g.lower() for g in age_genres)
            preferred_genres = preferred_genres.union(age_genres_set)
            
        if hobby_genres:
            hobby_genres_set = set(g.lower() for g in hobby_genres)
            preferred_genres = preferred_genres.union(hobby_genres_set)
        
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
        
        # Additional boost if there's a direct match with age or hobby genres
        if age_genres and book_genre_set.intersection(set(g.lower() for g in age_genres)):
            total_score *= 1.15  # 15% boost for age-appropriate matches
            
        if hobby_genres and book_genre_set.intersection(set(g.lower() for g in hobby_genres)):
            total_score *= 1.1  # 10% boost for hobby-related matches
        
        return min((total_score / max_possible_score) * 100, 100) if max_possible_score > 0 else 0

    def normalize_score(self, score, min_threshold=60):  # Increased minimum threshold
        if isinstance(score, np.ndarray):
            # Clip values to ensure minimum threshold
            normalized = min_threshold + (100 - min_threshold) * (score - score.min()) / (score.max() - score.min() + 1e-10)
            return np.clip(normalized, min_threshold, 100)
        else:
            return min_threshold + (100 - min_threshold) * (score / 100)

    # def recommend_books_for_user(self, username, debug=False):
    #     """Enhanced recommendation function with prioritized genre filtering and debugging statements."""
    #     if username not in self.users_df['User name'].values:
    #         return {"error": f"User '{username}' not found."}

    #     user_info = self.get_user_info(username)
    #     preferred_genres = {g.lower().strip() for g in user_info['genres']}
    #     notes = user_info['notes']
    #     age = user_info.get('age', '')
    #     hobbies = user_info.get('hobbies', [])

    #     if debug:
    #         print(f"User: {username}")
    #         print(f"Preferred Genres: {preferred_genres}")
    #         print(f"Notes: {notes}")
    #         print(f"Age: {age}")
    #         print(f"Hobbies: {hobbies}")

    #     recommended_books = user_info['recommendations']

    # # Strict fiction vs non-fiction filter
    #     is_fiction = 'Fiction' in preferred_genres
    #     is_non_fiction = 'Non Fiction' in preferred_genres

    #     age_genres = {g.lower().strip() for g in self.get_age_appropriate_genres(age)}
    #     hobby_genres = {g.lower().strip() for g in self.get_hobby_related_genres(hobbies)}
    #     combined_genres = preferred_genres.union(age_genres).union(hobby_genres)

    #     genre_scores = []
    #     genre_penalties = []
    #     valid_indices = []

    #     for book_idx, book_genres in enumerate(self.books_df['Genres']):
    #         if pd.isna(book_genres) or book_genres.strip() == "":
    #             # genre_penalties.append(-50)  # Apply a penalty but don't remove the book
    #             continue 
    #         book_genres = str(book_genres).lower().strip()
    #         book_genre_set = set(book_genres.split(','))


    #         fiction_penalty = -30 if (is_fiction and 'non-fiction' in book_genre_set) or (is_non_fiction and 'fiction' in book_genre_set) else 0


    #         if not any(pref in book_genres for pref in preferred_genres):
    #             continue  # Remove books if they have no partial genre match
        
    #         match_score = self.calculate_genre_match(book_genres, preferred_genres, age_genres, hobby_genres)
    #         if match_score > 35:
    #             genre_scores.append(match_score)
    #             genre_penalties.append(fiction_penalty)  # Store penalty separately
    #             valid_indices.append(book_idx)
    
    #     if debug:
    #         print(f"Valid books after filtering: {len(valid_indices)}")
    
    #     if not valid_indices:
    #         return {"error": "No books found matching your preferences."}

    #     filtered_books = self.books_df.iloc[valid_indices].copy()
    #     genre_scores = np.array(genre_scores)
    #     genre_penalties = np.array(genre_penalties)


    #     genre_scores = self.normalize_score(genre_scores)

    #     mask = ~filtered_books['Book'].isin(recommended_books)
    #     filtered_books = filtered_books[mask]
    #     genre_scores = genre_scores[mask]
    #     genre_penalties = genre_penalties[mask]


    #     if filtered_books.empty:
    #         return {"error": "No new books found matching your preferences."}

    #     if notes.strip():
    #         user_embedding = self.load_model().encode([notes])
    #         filtered_embeddings = self.get_book_embeddings()[filtered_books.index]
    #         cosine_sim = cosine_similarity(user_embedding, filtered_embeddings)[0]
    #         notes_scores = self.normalize_score(cosine_sim * 100)
    #     else:
    #         notes_scores = np.full(len(filtered_books), 70)
    
    #     feedback_scores = np.array([
    #      self.get_user_feedback_score(username, book_title)
    #     for book_title in filtered_books['Book']
    # ])
    #     feedback_scores = self.normalize_score(feedback_scores)

    #     hobby_boost = np.array([
    #         genre_scores[i] * 0.10 if any(hobby in book_genres for hobby in hobby_genres) else 0
    #     for i, book_genres in enumerate(filtered_books['Genres'])
    #         ])


    #     # genre_scores = self.normalize_score(genre_scores[:len(filtered_books)])
    #     # notes_scores = self.normalize_score(notes_scores[:len(filtered_books)])
    #     # feedback_scores = self.normalize_score(feedback_scores[:len(filtered_books)])

    #     final_scores = (
    #    genre_scores * 0.50 +  # Strongest weight
    #     notes_scores * 0.30 +  # Secondary factor
    #     feedback_scores * 0.10 +  # Mild influence
    #     hobby_boost -  # Hobby boost (scaled properly)
    #     genre_penalties  # Penalty for weak matches
    # )
    
    #     best_match_idx = np.argmax(final_scores)
    #     most_similar_book = filtered_books.iloc[best_match_idx]
    
    #     if debug:
    #         print(f"Selected Book: {most_similar_book['Book']}")
    #         print(f"Final Score: {final_scores[best_match_idx]}")

    #     new_book = most_similar_book['Book']
    #     if new_book not in recommended_books:
    #         recommended_books.add(new_book)
    #         self.users_df.loc[self.users_df['User name'] == username, 'Recommended Books'] = str(list(recommended_books))
    #         self.users_df.to_csv('User.csv', index=False)
    #         self._user_cache[username]['recommendations'] = recommended_books

    #     playlist = self.recommend_playlist_for_book(most_similar_book['Description'])

    #     return {
    #     "book": {
    #         "title": most_similar_book['Book'],
    #         "author": most_similar_book['Author'],
    #         "rating": most_similar_book['Avg_Rating'],
    #         "genre": most_similar_book['Genres'],
    #         "url": most_similar_book['URL'],
    #         "description": most_similar_book['Description']
    #     },
    #     "match_scores": {
    #         "overall_match": round(float(final_scores[best_match_idx]), 1),
    #         "notes_match": round(float(notes_scores[best_match_idx]), 1),
    #         "genre_match": round(float(genre_scores[best_match_idx]), 1),
    #         "feedback_match": round(float(feedback_scores[best_match_idx]), 1),
    #     },
    #     "playlist": playlist
    # }

    def get_true_pred_scores(self):
        """Return true labels and computed recommendation scores for Precision-Recall Curve."""
        feedback_df = self.feedback_df  
        recommended_books_df = self.users_df[['User name', 'Recommended Books']]

        y_true = []  # 1 = liked/saved, 0 = not relevant
        y_scores = []  # Use final recommendation scores

        for _, row in recommended_books_df.iterrows():
            user = row['User name']
            rec_books = eval(row['Recommended Books']) if isinstance(row['Recommended Books'], str) else []

            relevant_books = set(feedback_df[(feedback_df['username'] == user) & feedback_df['liked']]['book_title'])

            for book in rec_books:
                y_true.append(1 if book in relevant_books else 0)  # 1 if liked, 0 otherwise
            
            # Get the recommendation score by re-running recommendation logic
                score = self.get_final_recommendation_score(user, book)
                y_scores.append(score)

        return np.array(y_true), np.array(y_scores)

    def get_final_recommendation_score(self, username, book_title):
        """Computes the final recommendation score for a given user and book."""
    # Run recommendation function to get final scores
        recommendations = self.recommend_books_for_user(username, debug=False)
    
        if "book" in recommendations and recommendations["book"]["title"] == book_title:
            return recommendations["match_scores"]["overall_match"]
    
        return 0  # If the book is not recommended, assign a low score




    def recommend_books_for_user(self, username, debug=False):
        """Enhanced recommendation function incorporating user feedback, age, and hobbies."""
        if username not in self.users_df['User name'].values:
            return {"error": f"User '{username}' not found."}

        user_info = self.get_user_info(username)
        preferred_genres = user_info['genres']
        notes = user_info['notes']
        age = user_info.get('age', '')
        hobbies = user_info.get('hobbies', [])
        
        if debug:
            print(f"User: {username}")
            print(f"Age: {age}")
            print(f"Hobbies: {hobbies}")
            print(f"Preferred genres: {preferred_genres}")
            print(f"Notes: {notes}")

        if not notes or pd.isna(notes):
            notes = '' 

        recommended_books = user_info['recommendations']
        
        # Get age-appropriate and hobby-related genres
        age_genres = self.get_age_appropriate_genres(age)
        hobby_genres = self.get_hobby_related_genres(hobbies)
        
        if debug:
            print(f"Age-appropriate genres: {age_genres}")
            print(f"Hobby-related genres: {hobby_genres}")

        # Calculate genre matches and filter
        genre_matches = []
        for book_idx, book_genres in enumerate(self.books_df['Genres']):
            match_score = self.calculate_genre_match(book_genres, preferred_genres, age_genres, hobby_genres)
            if match_score > 20:
                genre_matches.append((book_idx, match_score))
                if debug:
                    print(f"Book {self.books_df.iloc[book_idx]['Book']} matched with score {match_score}")

        if not genre_matches:
            return {"error": f"No books found matching your preferences for genres, age, and hobbies."}
        

        matched_indices = [idx for idx, _ in genre_matches]
        filtered_books = self.books_df.iloc[matched_indices].copy()
        genre_scores = np.array([score for _, score in genre_matches])

        # Remove recommended books
        mask = ~filtered_books['Book'].isin(recommended_books)
        filtered_books = filtered_books[mask]
        genre_scores = genre_scores[mask]
        
        if filtered_books.empty:
            return {"error": "No unrecommended books found matching your preferences."}
        
        try:
            # Calculate content similarity based on notes
            if notes.strip():
                user_embedding = self.load_model().encode([notes])
                filtered_embeddings = self.get_book_embeddings()[filtered_books.index]
                cosine_sim = cosine_similarity(user_embedding, filtered_embeddings)[0]
                notes_scores = self.normalize_score(cosine_sim * 100)
            else:
                # If no notes, use neutral scores
                notes_scores = np.full(len(filtered_books), 70)
        
            # Normalize genre scores
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
                    collab_boost[i] = 30  # Boost score by 30 points
        
            # Combine all scores with updated weightage
            final_scores = (
                notes_scores * 0.35 +   
                genre_scores * 0.35 +    
                feedback_scores * 0.20 + 
                collab_boost * 0.10     
                
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
                    "feedback_match": round(float(feedback_scores[best_match_idx]), 1),
                    "age_appropriate": "Yes" if age_genres and any(g.lower() in most_similar_book['Genres'].lower() for g in age_genres) else "No",
                    "hobby_related": "Yes" if hobby_genres and any(g.lower() in most_similar_book['Genres'].lower() for g in hobby_genres) else "No"
                },
                "playlist": playlist
            }
    
        except Exception as e:
            print(f"Error in recommendation: {str(e)}")
            # Return a simplified recommendation based only on genre if there's an error
            best_genre_idx = np.argmax(genre_scores)
            fallback_book = filtered_books.iloc[best_genre_idx]
        
            return {
                "book": {
                    "title": fallback_book['Book'],
                    "author": fallback_book['Author'],
                    "rating": fallback_book['Avg_Rating'],
                    "genre": fallback_book['Genres'],
                    "url": fallback_book['URL'],
                    "description": fallback_book['Description']
                },
                "match_scores": {
                    "overall_match": round(float(genre_scores[best_genre_idx]), 1),
                    "notes_match": 70.0,  # Default score
                    "genre_match": round(float(genre_scores[best_genre_idx]), 1),
                    "feedback_match": 70.0,  # Default score
                    "age_appropriate": "Yes" if age_genres and any(g.lower() in fallback_book['Genres'].lower() for g in age_genres) else "No",
                    "hobby_related": "Yes" if hobby_genres and any(g.lower() in fallback_book['Genres'].lower() for g in hobby_genres) else "No"
                },
                "playlist": self.recommend_playlist_for_book(fallback_book['Description'])
            }
        

        from sklearn.metrics import precision_score, recall_score

    def evaluate_recommendation_accuracy(self):
        """Evaluate Precision and Recall of the recommendation system."""
    
        feedback_df = self.feedback_df  # Load user feedback data
        recommended_books_df = self.users_df[['User name', 'Recommended Books']]  # Load user recommendations

    # Mark a book as relevant if it was either 'liked' or 'saved'
        feedback_df['relevant'] = feedback_df['liked'] | feedback_df['saved']

        y_true = []  # Actual user preferences (1 = relevant, 0 = not relevant)
        y_pred = []  # System recommendations (1 = recommended, 0 = not recommended)

        for _, row in recommended_books_df.iterrows():
            user = row['User name']
            rec_books = eval(row['Recommended Books']) if isinstance(row['Recommended Books'], str) else []

        # Get the books this user actually liked/saved
            relevant_books = set(feedback_df[(feedback_df['username'] == user) & feedback_df['relevant']]['book_title'])

        # Compare recommendations with actual preferences
            for book in rec_books:
                y_true.append(1 if book in relevant_books else 0)  # 1 if relevant, 0 otherwise
                y_pred.append(1)  # 1 because the system recommended it

        # Identify books that were **relevant but NOT recommended** (False Negatives)
            for book in relevant_books:
                if book not in rec_books:  
                    y_true.append(1)  # Should have been recommended
                    y_pred.append(0)  # But was not recommended

    # Compute Precision & Recall
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)

        return {"Precision": precision, "Recall": recall}









    def get_playlist(self, book_title):
        """Get a playlist recommendation for a given book title."""
        book_data = self.books_df[self.books_df['Book'].str.lower() == book_title.lower()]
        
        if book_data.empty:
            return None
        
        book_description = book_data.iloc[0]['Description']
        
        return self.recommend_playlist_for_book(book_description)
    
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