import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt
from tqdm import tqdm
import random
import copy

class RecommenderEvaluator:
    def __init__(self, recommender):
        """Initialize the evaluator with your recommender system."""
        self.recommender = recommender
        self.results = {}
    
    def create_synthetic_users(self, n=10, base_genres=None):
        """Create synthetic users with controlled preferences for testing."""
        if base_genres is None:
            base_genres = [
                "Fantasy", "Mystery", "Romance", "Science Fiction", 
                "Historical Fiction", "Thriller", "Young Adult", "Literary Fiction"
            ]
        
        # Create synthetic users with specific genre preferences
        synthetic_users = []
        for i in range(n):
            # Select 2-3 primary genres
            primary_genres = random.sample(base_genres, random.randint(2, 3))
            
            # Create user data
            age = random.choice([15, 25, 35, 45])
            hobbies = random.sample(["reading", "gaming", "sports", "music", "art", "travel"], 2)
            
            user = {
                'User name': f'synthetic_user_{i}',
                'Genre': ','.join(primary_genres),
                'Age': age,
                'Hobbies': ','.join(hobbies),
                'Notes': f"I enjoy books with {' and '.join(primary_genres)}. Looking for engaging stories.",
                'Recommended Books': ''
            }
            synthetic_users.append(user)
        
        return pd.DataFrame(synthetic_users)
    
    def evaluate_synthetic_users(self, n_users=10):
        """Test the system with synthetic users and verify genre alignment."""
        print("\n=== Synthetic User Evaluation ===")
        
        # Back up original users dataframe
        original_users = self.recommender.users_df.copy()
        
        # Create synthetic users
        synthetic_users = self.create_synthetic_users(n_users)
        
        # Temporarily replace users with synthetic ones
        self.recommender.users_df = synthetic_users
        self.recommender._user_cache = {}  # Clear cache
        
        results = {
            'genre_match_scores': [],
            'age_appropriate': [],
            'hobby_related': []
        }
        
        # Get recommendations for each synthetic user
        for _, user in tqdm(synthetic_users.iterrows(), desc="Testing synthetic users", total=len(synthetic_users)):
            username = user['User name']
            try:
                recommendation = self.recommender.recommend_books_for_user(username)
                
                if 'error' not in recommendation:
                    # Collect evaluation metrics
                    results['genre_match_scores'].append(recommendation['match_scores']['genre_match'])
                    results['age_appropriate'].append(1 if recommendation['match_scores']['age_appropriate'] == "Yes" else 0)
                    results['hobby_related'].append(1 if recommendation['match_scores']['hobby_related'] == "Yes" else 0)
            except Exception as e:
                print(f"Error for user {username}: {str(e)}")
        
        # Restore original users
        self.recommender.users_df = original_users
        self.recommender._user_cache = {}  # Clear cache
        
        # Calculate summary statistics  
        genre_match_avg = np.mean(results['genre_match_scores'])
        age_appropriate_pct = np.mean(results['age_appropriate']) * 100
        hobby_related_pct = np.mean(results['hobby_related']) * 100
        
        print(f"Average genre match score: {genre_match_avg:.2f}")
        print(f"Age-appropriate recommendations: {age_appropriate_pct:.2f}%")
        print(f"Hobby-related recommendations: {hobby_related_pct:.2f}%")
        
        self.results['synthetic_evaluation'] = {
            'genre_match_avg': genre_match_avg,
            'age_appropriate_pct': age_appropriate_pct,
            'hobby_related_pct': hobby_related_pct,
            'raw_data': results
        }
        
        return self.results['synthetic_evaluation']
    
    def leave_one_out_validation(self, n_samples=None):
        """
        For users with multiple book recommendations, hide one and see if 
        the system can recommend something similar.
        """
        print("\n=== Leave-One-Out Validation ===")
        
        # Get users with multiple recommended books
        users_with_recommendations = []
        for _, user in self.recommender.users_df.iterrows():
            username = user['User name']
            user_info = self.recommender.get_user_info(username)
            if len(user_info['recommendations']) > 1:
                users_with_recommendations.append(username)
        
        if not users_with_recommendations:
            print("No users with multiple recommendations found for leave-one-out testing")
            return None
        
        # Sample users for testing
        if n_samples and n_samples < len(users_with_recommendations):
            test_users = random.sample(users_with_recommendations, n_samples)
        else:
            test_users = users_with_recommendations
        
        print(f"Testing {len(test_users)} users with leave-one-out validation")
        
        # Backup original data
        original_users_df = self.recommender.users_df.copy()
        original_cache = copy.deepcopy(self.recommender._user_cache)
        
        results = {
            'genre_similarity': [],
            'successfully_recovered': 0,
            'total_tested': 0
        }
        
        for username in tqdm(test_users, desc="Leave-one-out testing"):
            try:
                # Get user's current recommendations
                user_info = self.recommender.get_user_info(username)
                original_recommendations = list(user_info['recommendations'])
                
                if not original_recommendations:
                    continue
                
                # Select a random book to hide
                hidden_book = random.choice(original_recommendations)
                
                # Create modified recommendations list
                modified_recommendations = [b for b in original_recommendations if b != hidden_book]
                
                # Update user with modified recommendations
                self.recommender.users_df.loc[
                    self.recommender.users_df['User name'] == username, 
                    'Recommended Books'
                ] = str(modified_recommendations)
                
                # Clear cache for this user
                if username in self.recommender._user_cache:
                    del self.recommender._user_cache[username]
                
                # Get new recommendation
                recommendation = self.recommender.recommend_books_for_user(username)
                
                if 'error' not in recommendation:
                    # Check if hidden book was recommended again
                    new_book = recommendation['book']['title']
                    recovered = (new_book == hidden_book)
                    
                    # Get genre similarity between hidden and recommended book
                    hidden_book_data = self.recommender.books_df[
                        self.recommender.books_df['Book'] == hidden_book
                    ]
                    
                    if not hidden_book_data.empty:
                        hidden_genres = hidden_book_data.iloc[0]['Genres']
                        new_book_genres = recommendation['book']['genre']
                        
                        # Calculate genre similarity
                        genre_sim = self.calculate_genre_similarity(hidden_genres, new_book_genres)
                        results['genre_similarity'].append(genre_sim)
                        
                        results['successfully_recovered'] += int(recovered)
                        results['total_tested'] += 1
            except Exception as e:
                print(f"Error testing user {username}: {str(e)}")
        
        # Restore original data
        self.recommender.users_df = original_users_df
        self.recommender._user_cache = original_cache
        
        # Calculate summary metrics
        recovery_rate = (results['successfully_recovered'] / results['total_tested'] * 100) if results['total_tested'] > 0 else 0
        avg_genre_similarity = np.mean(results['genre_similarity']) if results['genre_similarity'] else 0
        
        print(f"Books directly recovered: {results['successfully_recovered']}/{results['total_tested']} ({recovery_rate:.2f}%)")
        print(f"Average genre similarity between hidden and recommended books: {avg_genre_similarity:.2f}")
        
        self.results['leave_one_out'] = {
            'recovery_rate': recovery_rate,
            'avg_genre_similarity': avg_genre_similarity,
            'raw_data': results
        }
        
        return self.results['leave_one_out']
    
    def calculate_genre_similarity(self, genres1, genres2):
        """Calculate similarity between two genre strings."""
        if pd.isna(genres1) or pd.isna(genres2):
            return 0
            
        # Convert to sets of genres
        if isinstance(genres1, str) and isinstance(genres2, str):
            genres1_set = set(g.strip().lower() for g in genres1.split(','))
            genres2_set = set(g.strip().lower() for g in genres2.split(','))
            
            # Calculate Jaccard similarity
            intersection = len(genres1_set.intersection(genres2_set))
            union = len(genres1_set.union(genres2_set))
            
            return intersection / union if union > 0 else 0
        return 0
    
    def evaluate_preference_stability(self, n_users=10, n_variations=3):
        """
        Test how stable recommendations are when slightly varying user preferences.
        We want some change but not complete randomness.
        """
        print("\n=== Preference Stability Evaluation ===")
        
        # Backup original data
        original_users_df = self.recommender.users_df.copy()
        original_cache = copy.deepcopy(self.recommender._user_cache)
        
        # Sample users for testing
        if n_users < len(self.recommender.users_df):
            test_users = random.sample(self.recommender.users_df['User name'].tolist(), n_users)
        else:
            test_users = self.recommender.users_df['User name'].tolist()
        
        results = {
            'stability_scores': [],
            'recommendation_diversity': []
        }
        
        for username in tqdm(test_users, desc="Testing preference stability"):
            try:
                # Get original user data
                user_idx = self.recommender.users_df[self.recommender.users_df['User name'] == username].index[0]
                original_genres = self.recommender.users_df.loc[user_idx, 'Genre']
                
                if pd.isna(original_genres) or original_genres == '':
                    continue
                    
                original_recommendation = self.recommender.recommend_books_for_user(username)
                if 'error' in original_recommendation:
                    continue
                    
                original_book = original_recommendation['book']['title']
                    
                # Create variations of this user
                genre_list = [g.strip() for g in original_genres.split(',')]
                recommendations = [original_book]
                
                for i in range(n_variations):
                    # Create slightly modified genre preferences
                    if len(genre_list) > 1:
                        # Remove one random genre
                        modified_genres = random.sample(genre_list, len(genre_list)-1)
                    else:
                        # Add a random genre
                        random_genre = random.choice([
                            "Fantasy", "Mystery", "Thriller", "Romance", 
                            "Science Fiction", "Historical Fiction"
                        ])
                        modified_genres = genre_list + [random_genre]
                    
                    # Update user with modified preferences
                    self.recommender.users_df.loc[user_idx, 'Genre'] = ','.join(modified_genres)
                    
                    # Clear cache
                    if username in self.recommender._user_cache:
                        del self.recommender._user_cache[username]
                    
                    # Get new recommendation
                    modified_recommendation = self.recommender.recommend_books_for_user(username)
                    if 'error' not in modified_recommendation:
                        recommendations.append(modified_recommendation['book']['title'])
                
                # Calculate stability (how many unique recommendations)
                unique_recommendations = len(set(recommendations))
                stability_score = 1 - (unique_recommendations - 1) / len(recommendations)
                
                results['stability_scores'].append(stability_score)
                results['recommendation_diversity'].append(unique_recommendations)
            except Exception as e:
                print(f"Error testing user {username}: {str(e)}")
        
        # Restore original data
        self.recommender.users_df = original_users_df
        self.recommender._user_cache = original_cache
        
        # Calculate average stability
        avg_stability = np.mean(results['stability_scores']) if results['stability_scores'] else 0
        avg_diversity = np.mean(results['recommendation_diversity']) if results['recommendation_diversity'] else 0
        
        print(f"Average recommendation stability: {avg_stability:.2f} (1.0 = completely stable, 0.0 = completely random)")
        print(f"Average recommendation diversity: {avg_diversity:.2f} unique recommendations per user+variations")
        
        self.results['preference_stability'] = {
            'avg_stability': avg_stability,
            'avg_diversity': avg_diversity,
            'raw_data': results
        }
        
        return self.results['preference_stability']
    
    def evaluate_feedback_impact(self, n_users=10):
        """Test how user feedback affects recommendations."""
        print("\n=== Feedback Impact Evaluation ===")
        
        # Backup original data
        original_feedback_df = self.recommender.feedback_df.copy()
        
        # Sample users for testing
        if n_users < len(self.recommender.users_df):
            test_users = random.sample(self.recommender.users_df['User name'].tolist(), n_users)
        else:
            test_users = self.recommender.users_df['User name'].tolist()
        
        results = {
            'feedback_impact_scores': []
        }
        
        for username in tqdm(test_users, desc="Testing feedback impact"):
            try:
                # Get initial recommendation
                initial_rec = self.recommender.recommend_books_for_user(username)
                if 'error' in initial_rec:
                    continue
                
                # Add positive feedback for this book
                self.recommender.add_user_feedback(
                    username=username,
                    book_title=initial_rec['book']['title'],
                    feedback_type='liked',
                    value=True
                )
                
                # Get new recommendation after feedback
                new_rec = self.recommender.recommend_books_for_user(username)
                if 'error' in new_rec:
                    continue
                
                # Check if feedback affected the recommendation
                feedback_impact = new_rec['match_scores']['feedback_match'] - initial_rec['match_scores']['feedback_match']
                results['feedback_impact_scores'].append(feedback_impact)
                
            except Exception as e:
                print(f"Error testing user {username}: {str(e)}")
        
        # Restore original feedback data
        self.recommender.feedback_df = original_feedback_df
        self.recommender.feedback_df.to_csv('user_feedback.csv', index=False)
        
        # Calculate average feedback impact
        avg_impact = np.mean(results['feedback_impact_scores']) if results['feedback_impact_scores'] else 0
        
        print(f"Average feedback impact on recommendations: {avg_impact:.2f} points")
        
        self.results['feedback_impact'] = {
            'avg_impact': avg_impact,
            'raw_data': results
        }
        return self.results['feedback_impact']
    
    def evaluate_song_playlist_relevance(self, n_books=20):
        """Evaluate how relevant recommended songs are to book content."""
        print("\n=== Song-Book Relevance Evaluation ===")
        
        # Sample books for testing
        if n_books < len(self.recommender.books_df):
            test_books = self.recommender.books_df.sample(n_books)
        else:
            test_books = self.recommender.books_df
        
        results = {
            'genre_match_scores': [],
            'sentiment_alignment_scores': []
        }
        
        genre_mappings = {
            # Book genres to music genres mappings
            'fantasy': ['instrumental', 'soundtrack', 'classical', 'epic', 'folk'],
            'sci-fi': ['electronic', 'ambient', 'synthwave', 'experimental'],
            'romance': ['pop', 'r&b', 'love songs', 'ballad'],
            'mystery': ['jazz', 'noir', 'ambient', 'instrumental'],
            'thriller': ['rock', 'alternative', 'industrial', 'electronic'],
            'horror': ['metal', 'industrial', 'dark ambient', 'gothic'],
            'historical': ['classical', 'folk', 'traditional', 'soundtrack'],
            'adventure': ['rock', 'pop rock', 'soundtrack', 'world'],
            'young adult': ['pop', 'indie', 'alternative', 'rock'],
            'children': ['pop', 'soundtrack', 'folk', 'world'],
            'literary fiction': ['jazz', 'classical', 'indie', 'folk'],
            'comedy': ['pop', 'funk', 'comedy', 'upbeat'],
            'drama': ['classical', 'soundtrack', 'instrumental', 'indie'],
            'non-fiction': ['instrumental', 'ambient', 'jazz', 'classical']
        }
        
        from nltk.sentiment import SentimentIntensityAnalyzer
        sentiment_analyzer = SentimentIntensityAnalyzer()
        
        for _, book in tqdm(test_books.iterrows(), desc="Testing book-playlist matches", total=len(test_books)):
            try:
                # Get book info
                title = book['Book']
                description = book['Description']
                genres = book['Genres'].lower() if not pd.isna(book['Genres']) else ''
                
                # Get playlist for this book
                playlist = self.recommender.recommend_playlist_for_book(description)
                
                if not playlist:
                    continue
                
                # Calculate genre match score
                book_genre_keywords = set()
                for genre, keywords in genre_mappings.items():
                    if any(g in genres for g in [genre, genre + 's']):
                        book_genre_keywords.update(keywords)
                
                if not book_genre_keywords:
                    # If no direct genre matches, take common words from the genres
                    book_genre_keywords = set(word.lower() for g in genres.split(',') 
                                           for word in g.split() if len(word) > 3)
                
                # Evaluate genre match between book and songs
                genre_match_scores = []
                for song in playlist:
                    song_genre = song['genre'].lower()
                    # Check how many genre keywords match
                    matches = sum(keyword in song_genre for keyword in book_genre_keywords)
                    # Normalize by number of possible matches
                    score = matches / len(book_genre_keywords) if book_genre_keywords else 0
                    genre_match_scores.append(score)
                
                # Calculate sentiment alignment
                try:
                    book_sentiment = sentiment_analyzer.polarity_scores(description)['compound']
                    
                    sentiment_alignment_scores = []
                    for song in playlist:
                        # Use valence as song sentiment (0-1)
                        song_sentiment = song['valence']
                        # Normalize book sentiment to 0-1 range
                        norm_book_sentiment = (book_sentiment + 1) / 2
                        # Calculate alignment (1 - absolute difference)
                        alignment = 1 - abs(norm_book_sentiment - song_sentiment)
                        sentiment_alignment_scores.append(alignment)
                    
                    # Average sentiment alignment for this book's playlist
                    results['sentiment_alignment_scores'].append(np.mean(sentiment_alignment_scores))
                except:
                    # Skip sentiment analysis if error occurs
                    pass
                
                # Average genre match for this book's playlist
                results['genre_match_scores'].append(np.mean(genre_match_scores))
                
            except Exception as e:
                print(f"Error evaluating book {title}: {str(e)}")
        
        # Calculate overall metrics
        avg_genre_match = np.mean(results['genre_match_scores']) if results['genre_match_scores'] else 0
        avg_sentiment_alignment = np.mean(results['sentiment_alignment_scores']) if results['sentiment_alignment_scores'] else 0
        
        print(f"Average genre match between books and playlists: {avg_genre_match:.2f}")
        print(f"Average sentiment alignment between books and playlists: {avg_sentiment_alignment:.2f}")
        
        self.results['book_playlist_relevance'] = {
            'avg_genre_match': avg_genre_match,
            'avg_sentiment_alignment': avg_sentiment_alignment,
            'raw_data': results
        }
        
        return self.results['book_playlist_relevance']
        
    def evaluate_user_satisfaction_simulation(self, n_users=10, feedback_iterations=3):
        """Simulate user satisfaction by generating feedback over multiple iterations."""
        print("\n=== User Satisfaction Simulation ===")
        
        # Backup original data
        original_feedback_df = self.recommender.feedback_df.copy()
        original_users_df = self.recommender.users_df.copy()
        
        # Sample or create synthetic users
        synthetic_users = self.create_synthetic_users(n_users)
        
        # Temporarily add synthetic users
        self.recommender.users_df = pd.concat([self.recommender.users_df, synthetic_users], ignore_index=True)
        self.recommender._user_cache = {}  # Clear cache
        
        results = {
            'satisfaction_trend': [],
            'diversity_trend': []
        }
        
        recommended_books = {}
        
        for username in tqdm(synthetic_users['User name'], desc="Simulating user satisfaction"):
            try:
                user_data = synthetic_users[synthetic_users['User name'] == username].iloc[0]
                preferred_genres = user_data['Genre'].split(',')
                
                # Track recommendations for this user
                recommended_books[username] = set()
                user_satisfaction = []
                
                for iteration in range(feedback_iterations):
                    # Get recommendation
                    recommendation = self.recommender.recommend_books_for_user(username)
                    if 'error' in recommendation:
                        continue
                        
                    book = recommendation['book']
                    book_title = book['title']
                    book_genres = book['genre'].split(',')
                    
                    # Add to recommended set
                    recommended_books[username].add(book_title)
                    
                    # Calculate satisfaction based on genre match and rating
                    genre_overlap = len(set(g.strip().lower() for g in preferred_genres) & 
                                      set(g.strip().lower() for g in book_genres))
                    
                    rating_factor = float(book['rating']) / 5.0 if book['rating'] else 0.7
                    
                    # Simulate user satisfaction (higher for better genre matches and ratings)
                    satisfaction = (genre_overlap / max(len(preferred_genres), 1)) * 0.7 + rating_factor * 0.3
                    satisfaction = min(satisfaction * 100, 100)  # Scale to 0-100
                    
                    user_satisfaction.append(satisfaction)
                    
                    # Simulate user feedback (more likely to like if satisfaction is high)
                    like_probability = satisfaction / 100
                    liked = random.random() < like_probability
                    
                    # Save feedback
                    self.recommender.add_user_feedback(
                        username=username,
                        book_title=book_title,
                        feedback_type='liked',
                        value=liked
                    )
                    
                    # Also simulate click and save behaviors
                    if liked:
                        self.recommender.add_user_feedback(
                            username=username,
                            book_title=book_title,
                            feedback_type='clicked',
                            value=True
                        )
                        
                        save_probability = 0.7  # 70% chance to save a liked book
                        if random.random() < save_probability:
                            self.recommender.add_user_feedback(
                                username=username,
                                book_title=book_title,
                                feedback_type='saved',
                                value=True
                            )
                
                # Record satisfaction trend for this user
                if user_satisfaction:
                    # Check if satisfaction improved
                    satisfaction_trend = user_satisfaction[-1] - user_satisfaction[0]
                    results['satisfaction_trend'].append(satisfaction_trend)
                    
                    # Calculate diversity (unique recommendations)
                    diversity = len(recommended_books[username])
                    results['diversity_trend'].append(diversity)
            
            except Exception as e:
                print(f"Error simulating user {username}: {str(e)}")
        
        # Restore original data
        self.recommender.users_df = original_users_df
        self.recommender.feedback_df = original_feedback_df
        self.recommender.feedback_df.to_csv('user_feedback.csv', index=False)
        self.recommender._user_cache = {}  # Clear cache
        
        # Calculate overall metrics
        avg_satisfaction_trend = np.mean(results['satisfaction_trend']) if results['satisfaction_trend'] else 0
        avg_diversity = np.mean(results['diversity_trend']) if results['diversity_trend'] else 0
        
        print(f"Average satisfaction trend: {avg_satisfaction_trend:.2f} points")
        print(f"Average recommendation diversity: {avg_diversity:.2f} unique books")
        
        self.results['user_satisfaction'] = {
            'avg_satisfaction_trend': avg_satisfaction_trend,
            'avg_diversity': avg_diversity,
            'raw_data': results
        }
        
        return self.results['user_satisfaction']
    
    def run_comprehensive_evaluation(self, n_users=10, n_books=20):
        """Run all evaluation methods and generate a comprehensive report."""
        print("\n===== COMPREHENSIVE EVALUATION =====")
        
        try:
            self.evaluate_synthetic_users(n_users)
        except Exception as e:
            print(f"Error in synthetic user evaluation: {str(e)}")
            
        try:
            self.leave_one_out_validation(n_users)
        except Exception as e:
            print(f"Error in leave-one-out validation: {str(e)}")
            
        try:
            self.evaluate_preference_stability(n_users)
        except Exception as e:
            print(f"Error in preference stability evaluation: {str(e)}")
            
        try:
            self.evaluate_feedback_impact(n_users)
        except Exception as e:
            print(f"Error in feedback impact evaluation: {str(e)}")
            
        try:
            self.evaluate_song_playlist_relevance(n_books)
        except Exception as e:
            print(f"Error in song-book relevance evaluation: {str(e)}")
            
        try:
            self.evaluate_user_satisfaction_simulation(n_users)
        except Exception as e:
            print(f"Error in user satisfaction simulation: {str(e)}")
            
        return self.generate_evaluation_report()
    


    def generate_evaluation_report(self):


        """Generate a summary report of all evaluation metrics."""
        print("\n===== EVALUATION SUMMARY REPORT =====")
    
        report = {
        "overall_score": 0,
        "metrics": {}
    }
    
    # Define weights for different metrics
        weights = {
        "synthetic_evaluation": 0.15,
        "leave_one_out": 0.20,
        "preference_stability": 0.15,
        "feedback_impact": 0.15,
        "book_playlist_relevance": 0.15,
        "user_satisfaction": 0.20
    }
    
        scores = []
    
        # Process synthetic evaluation results
        if 'synthetic_evaluation' in self.results:
            data = self.results['synthetic_evaluation']
            score = (data['genre_match_avg'] * 0.6 + 
                 data['age_appropriate_pct'] * 0.2 +
                 data['hobby_related_pct'] * 0.2) / 100
        
            report["metrics"]["synthetic_evaluation"] = {
            "score": score * 100,
            "details": {
                "genre_match_avg": data['genre_match_avg'],
                "age_appropriate_pct": data['age_appropriate_pct'],
                "hobby_related_pct": data['hobby_related_pct']
            }
        }
            scores.append(score * weights["synthetic_evaluation"])
    
    # Process leave-one-out validation results
        if 'leave_one_out' in self.results:
            data = self.results['leave_one_out']
            score = (data['recovery_rate'] * 0.4 + 
                 data['avg_genre_similarity'] * 100 * 0.6) / 100
        
            report["metrics"]["leave_one_out"] = {
            "score": score * 100,
            "details": {
                "recovery_rate": data['recovery_rate'],
                "avg_genre_similarity": data['avg_genre_similarity']
            }
        }
            scores.append(score * weights["leave_one_out"])
    
    # Process preference stability results
        if 'preference_stability' in self.results:
            data = self.results['preference_stability']
        # We want some stability (0.7) but also some diversity (0.3)
            stability_score = data['avg_stability'] * 0.7 + (1 - data['avg_stability']) * 0.3
        
            report["metrics"]["preference_stability"] = {
            "score": stability_score * 100,
            "details": {
                "avg_stability": data['avg_stability'],
                "avg_diversity": data['avg_diversity']
            }
        }
            scores.append(stability_score * weights["preference_stability"])
    
    # Process feedback impact results
        if 'feedback_impact' in self.results:
            data = self.results['feedback_impact']
        # Normalize impact to 0-1 scale (considering 20 points as maximum impact)
            impact_score = min(data['avg_impact'] / 20, 1)
        
            report["metrics"]["feedback_impact"] = {
            "score": impact_score * 100,
            "details": {
                "avg_impact": data['avg_impact']
            }
        }
            scores.append(impact_score * weights["feedback_impact"])
    
    # Process book-playlist relevance results
        if 'book_playlist_relevance' in self.results:
            data = self.results['book_playlist_relevance']
            score = (data['avg_genre_match'] * 0.6 + 
                 data['avg_sentiment_alignment'] * 0.4)
        
            report["metrics"]["book_playlist_relevance"] = {
            "score": score * 100,
            "details": {
                "avg_genre_match": data['avg_genre_match'],
                "avg_sentiment_alignment": data['avg_sentiment_alignment']
            }
        }
            scores.append(score * weights["book_playlist_relevance"])
    
    # Process user satisfaction simulation results
        if 'user_satisfaction' in self.results:
            data = self.results['user_satisfaction']
        # Normalize satisfaction trend (10 points as maximum improvement)
            satisfaction_score = min(max(data['avg_satisfaction_trend'] / 10, 0), 1) * 0.7
        # Diversity score (assuming 3 unique books is optimal in the simulation period)
            diversity_score = min(data['avg_diversity'] / 3, 1) * 0.3
            total_score = satisfaction_score + diversity_score
        
            report["metrics"]["user_satisfaction"] = {
            "score": total_score * 100,
            "details": {
                "avg_satisfaction_trend": data['avg_satisfaction_trend'],
                "avg_diversity": data['avg_diversity']
            }
        }
            scores.append(total_score * weights["user_satisfaction"])
    
    # Calculate overall score
        if scores:
            report["overall_score"] = sum(scores) * 100 / sum(weights.values())
    
    # Print report summary
        print("\nEvaluation Report Summary:")
        print(f"Overall Recommendation System Score: {report['overall_score']:.2f}/100")
        print("\nIndividual Metrics:")
    
        for metric, data in report["metrics"].items():
            print(f"- {metric.replace('_', ' ').title()}: {data['score']:.2f}/100")
    
    # Provide insights based on results
        print("\nKey Insights:")
    
        if 'synthetic_evaluation' in report["metrics"]:
            score = report["metrics"]["synthetic_evaluation"]["score"]
            if score < 70:
                print("- The system struggles with accurately matching synthetic user preferences. Consider refining genre matching algorithms.")
            else:
                print("- The system shows good performance with synthetic user preferences, indicating solid baseline recommendation capability.")
    
        if 'leave_one_out' in report["metrics"]:
            score = report["metrics"]["leave_one_out"]["score"]
            if score < 70:
                print("- The system has difficulty recovering previously liked content. Consider enhancing collaborative filtering components.")
            else:
                print("- The system demonstrates good ability to recommend content similar to previously liked items.")
    
        if 'preference_stability' in report["metrics"]:
            score = report["metrics"]["preference_stability"]["score"]
            if score < 60:
                print("- Recommendations are too unstable or too rigid when user preferences change slightly. Consider balancing diversity and stability.")
            else:
                print("- The system shows appropriate balance between stability and diversity in recommendations.")
    
        if 'feedback_impact' in report["metrics"]:
            score = report["metrics"]["feedback_impact"]["score"]
            if score < 60:
                print("- User feedback doesn't sufficiently impact future recommendations. Consider increasing feedback weight in your algorithm.")
            else:
                print("- User feedback appropriately influences future recommendations.")
    
        if 'book_playlist_relevance' in report["metrics"]:
            score = report["metrics"]["book_playlist_relevance"]["score"]
            if score < 70:
                print("- Book-playlist pairing needs improvement. Consider enhancing content-based similarity measures.")
            else:
                print("- Book and music recommendations show good thematic and emotional alignment.")
    
        if 'user_satisfaction' in report["metrics"]:
            score = report["metrics"]["user_satisfaction"]["score"]
            if score < 70:
                print("- Simulated user satisfaction trends indicate potential issues with recommendation quality over time.")
            else:
                print("- Simulated users show increasing satisfaction with recommendations over time.")
    
    # Generate recommendations for improvement
        print("\nRecommendations for Improvement:")
        lowest_metric = None
        lowest_score = float('inf')
    
        for metric, data in report["metrics"].items():
            if data["score"] < lowest_score:
                lowest_score = data["score"]
                lowest_metric = metric
    
        if lowest_metric:
            if lowest_metric == "synthetic_evaluation":
                print("1. Enhance genre matching algorithms to better align with user preferences.")
                print("2. Refine age and hobby-appropriate content filtering.")
            elif lowest_metric == "leave_one_out":
                print("1. Strengthen collaborative filtering components of your hybrid system.")
                print("2. Improve content-based similarity measures between books.")
            elif lowest_metric == "preference_stability":
                print("1. Adjust sensitivity of recommendation changes when preferences shift.")
                print("2. Implement controlled exploration to balance familiarity and discovery.")
            elif lowest_metric == "feedback_impact":
                print("1. Increase the weight of explicit user feedback in your recommendation algorithm.")
                print("2. Implement fast adaptation to new user feedback patterns.")
            elif lowest_metric == "book_playlist_relevance":
                print("1. Refine sentiment analysis for better emotional matching.")
                print("2. Enhance genre mapping between books and music.")
            elif lowest_metric == "user_satisfaction":
                print("1. Focus on improving recommendation quality over multiple interactions.")
                print("2. Balance recommendation diversity with user preference alignment.")
    
    # Add visualization code
        self.visualize_results(report)
    
        return report
    


    def visualize_results(self, report):
        """Generate visualizations for the evaluation results."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        
        # Create a bar chart of metric scores
            metrics = []
            scores = []
        
            for metric, data in report["metrics"].items():
                metrics.append(metric.replace('_', ' ').title())
                scores.append(data["score"])
        
            plt.figure(figsize=(12, 6))
            bars = plt.bar(metrics, scores, color='steelblue')
            plt.axhline(y=report["overall_score"], color='r', linestyle='-', label=f'Overall Score: {report["overall_score"]:.2f}')
            plt.ylim(0, 100)
            plt.ylabel('Score (/100)')
            plt.title('Recommendation System Evaluation Metrics')
            plt.xticks(rotation=45, ha='right')
        
        # Add score labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{height:.1f}', ha='center', va='bottom')
        
            plt.tight_layout()
            plt.legend()
            plt.savefig('evaluation_metrics.png')
            print("\nEvaluation visualization saved as 'evaluation_metrics.png'")
        
        # Create radar chart if we have multiple metrics
            if len(metrics) >= 3:
                plt.figure(figsize=(10, 8))
            
            # Compute angles for radar chart
                angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
                angles += angles[:1]  # Close the loop
            
            # Create scores list (also close the loop)
                radar_scores = scores + [scores[0]]
            
            # Create radar chart
                ax = plt.subplot(111, polar=True)
                ax.plot(angles, radar_scores, 'o-', linewidth=2, label='Metrics')
                ax.fill(angles, radar_scores, alpha=0.25)
            
            # Set labels and ticks
                ax.set_thetagrids(np.degrees(angles[:-1]), metrics)
                ax.set_ylim(0, 100)
                ax.set_title('Recommendation System Evaluation Radar')
            
                plt.tight_layout()
                plt.savefig('evaluation_radar.png')
                print("Evaluation radar chart saved as 'evaluation_radar.png'")
            
        except Exception as e:
            print(f"Could not generate visualizations: {str(e)}")




if __name__ == "__main__":
    from recommendation import recommender

    print("Initializing Recommender Evaluator...")
    evaluator = RecommenderEvaluator(recommender)  # Now it will be defined

    print("Running comprehensive evaluation...")
    report = evaluator.run_comprehensive_evaluation()

    print("Evaluation complete! Here is the summary report:")
    print(report)


    




    

