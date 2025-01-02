import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

# Add parent directory to path so we can import the recommender
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recommendation import recommender

class RecommendationEvaluator:
    def __init__(self, recommender):
        self.recommender = recommender
        
    def generate_synthetic_users(self, n_users=100):
        """Generate synthetic users with controlled preferences"""
        genres = ['Fantasy', 'Science Fiction', 'Mystery', 'Romance', 'Historical Fiction', 
                 'Literary Fiction', 'Thriller', 'Horror', 'Adventure', 'Contemporary']
        
        synthetic_users = []
        for i in range(n_users):
            # Randomly select 2-4 preferred genres
            n_genres = np.random.randint(2, 5)
            user_genres = ', '.join(np.random.choice(genres, n_genres, replace=False))
            
            # Generate reading preferences/notes
            genre_keywords = {
                'Fantasy': ['magic', 'dragons', 'adventure', 'epic', 'quest'],
                'Science Fiction': ['space', 'technology', 'future', 'scientific', 'alien'],
                'Mystery': ['detective', 'crime', 'suspense', 'investigation', 'clues'],
                'Romance': ['love', 'relationship', 'emotional', 'passion', 'romantic']
            }
            
            notes = []
            for genre in user_genres.split(', '):
                if genre in genre_keywords:
                    notes.extend(np.random.choice(genre_keywords[genre], 2))
            
            notes = ' '.join(notes)
            
            synthetic_users.append({
                'User name': f'synthetic_user_{i}',
                'Genre': user_genres,
                'Notes': notes,
                'Recommended Books': ''
            })
            
        return pd.DataFrame(synthetic_users)
    
    def evaluate_genre_consistency(self, n_users=50, n_recommendations=5):
        """Evaluate how well recommendations match user genre preferences"""
        print("Evaluating genre consistency...")
        users_df = self.generate_synthetic_users(n_users)
        genre_matches = []
        
        for _, user in users_df.iterrows():
            user_genres = set(g.strip() for g in user['Genre'].split(','))
            
            # Get multiple recommendations
            recommendations = []
            for _ in range(n_recommendations):
                try:
                    rec = self.recommender.recommend_books_for_user(user['User name'])
                    if 'error' not in rec:
                        recommendations.append(rec)
                except:
                    continue
            
            # Calculate genre overlap for each recommendation
            for rec in recommendations:
                if 'book' in rec:
                    book_genres = set(g.strip() for g in rec['book']['genre'].split(','))
                    overlap = len(user_genres.intersection(book_genres)) / len(user_genres)
                    genre_matches.append({
                        'user': user['User name'],
                        'match_score': overlap * 100,
                        'overall_score': rec['match_scores']['overall_match']
                    })
        
        return pd.DataFrame(genre_matches)
    
    def evaluate_sentiment_playlist_alignment(self, n_samples=100):
        """Evaluate alignment between book sentiment and playlist mood"""
        print("Evaluating playlist-sentiment alignment...")
        
        results = []
        books = self.recommender.books_df.sample(n_samples)
        
        for _, book in books.iterrows():
            description = book['Description']
            sentiment = self.recommender.analyzer.polarity_scores(description)['compound']
            
            playlist = self.recommender.recommend_playlist_for_book(description)
            avg_valence = np.mean([song['valence'] for song in playlist])
            avg_energy = np.mean([song['energy'] for song in playlist])
            
            results.append({
                'book_sentiment': sentiment,
                'playlist_valence': avg_valence,
                'playlist_energy': avg_energy,
                'book_title': book['Book']
            })
            
        return pd.DataFrame(results)
    
    def evaluate_content_similarity(self, n_samples=50):
        """Evaluate semantic similarity between user notes and recommended books"""
        print("Evaluating content similarity...")
        users_df = self.generate_synthetic_users(n_samples)
        similarities = []
        
        model = self.recommender.load_model()
        
        for _, user in users_df.iterrows():
            try:
                rec = self.recommender.recommend_books_for_user(user['User name'])
                if 'error' not in rec and 'book' in rec:
                    user_embedding = model.encode([user['Notes']])
                    book_embedding = model.encode([rec['book']['description']])
                    similarity = cosine_similarity(user_embedding, book_embedding)[0][0]
                    
                    similarities.append({
                        'user': user['User name'],
                        'similarity_score': similarity * 100,
                        'match_score': rec['match_scores']['notes_match']
                    })
            except:
                continue
                
        return pd.DataFrame(similarities)