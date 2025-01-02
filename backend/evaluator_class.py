# File 1: evaluator_class.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from recommendation import recommender

class RecommendationEvaluator:
    def __init__(self, recommender):
        self.recommender = recommender
        
    def generate_synthetic_users(self, n_users=100):
        genre_combinations = [
        ['Fantasy', 'Science Fiction', 'Adventure'],
        ['Mystery', 'Thriller', 'Crime'],
        ['Romance', 'Contemporary', 'Drama'],
        ['Historical Fiction', 'Literary Fiction'],
        ['Horror', 'Thriller', 'Mystery']
    ]
    
    # More detailed genre-specific keywords
        genre_keywords = {
            'Fantasy': ['epic fantasy', 'magic systems', 'mythical creatures', 'world-building', 'heroic journey', 
                   'magical elements', 'fantasy adventure', 'enchanted', 'mystical'],
            'Science Fiction': ['space exploration', 'technological advancement', 'futuristic society', 
                          'alien civilization', 'scientific discovery', 'advanced technology'],
            'Mystery': ['detective work', 'criminal investigation', 'mystery solving', 'suspenseful plot', 
                   'complex puzzles', 'crime solving'],
            'Romance': ['emotional journey', 'romantic relationship', 'character development', 'love story',
                   'romantic elements', 'heartwarming'],
            'Historical Fiction': ['historical period', 'historical events', 'period piece', 'historical accuracy',
                             'historical setting', 'historical detail'],
        'Thriller': ['suspense', 'psychological tension', 'thrilling plot', 'fast-paced', 'action-packed'],
        'Horror': ['supernatural elements', 'psychological horror', 'dark atmosphere', 'suspenseful',
                  'horror elements', 'creepy'],
        'Adventure': ['action', 'exploration', 'journey', 'quest', 'exciting plot', 'adventure elements'],
        'Contemporary': ['modern setting', 'realistic fiction', 'current events', 'contemporary issues',
                        'realistic characters'],
        'Crime': ['criminal activity', 'police procedural', 'crime solving', 'detective work',
                 'mystery elements'],
            'Drama': ['emotional depth', 'character-driven', 'dramatic tension', 'realistic conflicts',
                     'life challenges'],
            'Literary Fiction': ['complex themes', 'literary style', 'character study', 'social commentary',
                               'artistic merit']
    }
    
        synthetic_users = []
        for i in range(n_users):
        # Select a genre combination
            combo_idx = np.random.randint(0, len(genre_combinations))
            genre_combo = genre_combinations[combo_idx]
            user_genres = ', '.join(genre_combo)
        
        # Generate more detailed notes using genre-specific keywords
            notes = []
            for genre in genre_combo:
            # Select more keywords per genre
                n_keywords = np.random.randint(3, 6)  # Select 3-5 keywords per genre
                genre_specific_keywords = np.random.choice(genre_keywords[genre], n_keywords)
                notes.extend(genre_specific_keywords)
        
        # Create a more natural-sounding note
            note_templates = [
            "I enjoy {0} and {1}. Looking for books with {2}.",
            "Big fan of {0} especially with {1}. Also interested in {2}.",
            "Love reading about {0}. Also enjoy {1} and {2}.",
            "Seeking books featuring {0} and {1}. {2} is a plus.",
            "Passionate about {0}, particularly when combined with {1}. {2} catches my interest too."
        ]
        
        # Randomly shuffle keywords and use them in template
            np.random.shuffle(notes)
            notes_text = np.random.choice(note_templates).format(
                notes[0] if notes else '',
                notes[1] if len(notes) > 1 else '',
                notes[2] if len(notes) > 2 else ''
        )
        
            synthetic_users.append({
            'User name': f'synthetic_user_{i}',
            'Genre': user_genres,
            'Notes': notes_text,
            'Recommended Books': ''
        })
    
        return pd.DataFrame(synthetic_users)

    
    def evaluate_genre_consistency(self, n_users=50, n_recommendations=5):
        print("Evaluating genre consistency...")
        users_df = self.generate_synthetic_users(n_users)
        genre_matches = []
    
        for _, user in users_df.iterrows():
            user_genres = set(g.strip().lower() for g in user['Genre'].split(','))
        
            recommendations = []
            for _ in range(n_recommendations):
                try:
                    rec = self.recommender.recommend_books_for_user(user['User name'])
                    if 'error' not in rec:
                        recommendations.append(rec)
                except:
                    continue
        
            for rec in recommendations:
                if 'book' in rec:
                    book_genres = set(g.strip().lower() for g in rec['book']['genre'].split(','))
                
                # Calculate direct matches
                    direct_matches = len(user_genres.intersection(book_genres))
                
                # Calculate partial matches (e.g., "epic fantasy" matches with "fantasy")
                    partial_matches = 0
                    for user_genre in user_genres:
                        for book_genre in book_genres:
                            if (user_genre in book_genre or book_genre in user_genre) and \
                                user_genre != book_genre:
                                partial_matches += 0.5
                
                # Calculate final score
                    total_matches = direct_matches + partial_matches
                    max_possible = max(len(user_genres), len(book_genres))
                    match_score = min((total_matches / max_possible) * 100, 100)
                
                    genre_matches.append({
                    'user': user['User name'],
                    'match_score': match_score,
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
        print("Evaluating content similarity...")
        users_df = self.generate_synthetic_users(n_samples)
        similarities = []
    
        model = self.recommender.load_model()
    
        for _, user in users_df.iterrows():
            try:
                rec = self.recommender.recommend_books_for_user(user['User name'])
                if 'error' not in rec and 'book' in rec:
                # Get embeddings for user notes and genres
                    user_notes_embedding = model.encode([user['Notes']])
                    user_genres_embedding = model.encode([user['Genre']])
                
                # Get embeddings for book description and genres
                    book_desc_embedding = model.encode([rec['book']['description']])
                    book_genres_embedding = model.encode([rec['book']['genre']])
                
                # Calculate similarities
                    notes_similarity = cosine_similarity(user_notes_embedding, book_desc_embedding)[0][0]
                    genre_similarity = cosine_similarity(user_genres_embedding, book_genres_embedding)[0][0]
                
                # Combine similarities with weights
                    combined_similarity = (notes_similarity * 0.7 + genre_similarity * 0.3) * 100
                
                    similarities.append({
                    'user': user['User name'],
                    'similarity_score': combined_similarity,
                    'match_score': rec['match_scores']['notes_match']
                })
            except:
                continue
            
        return pd.DataFrame(similarities)