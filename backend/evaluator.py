import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import KFold
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score
import random
from recommendation import recommender

class RecommenderEvaluator:
    def __init__(self, recommender):
        self.recommender = recommender
        self.books_df = recommender.books_df
        self.songs_df = recommender.songs_df
        self.users_df = recommender.users_df
        
    def generate_synthetic_interactions(self, n_interactions=100):
        """Generate synthetic user interactions based on genre preferences."""
        interactions = []
        
        for _, user in self.users_df.iterrows():
            user_genres = set(g.strip() for g in user['Genre'].split(','))
            
            # Find books matching user genres
            matching_books = []
            for _, book in self.books_df.iterrows():
                try:
                # Safely parse the genres as a list of strings
                    book_genres = set(genre.strip().lower() for genre in book['Genres'].strip('[]').split(','))
                except AttributeError:
                    book_genres = set()
                if any(ug.lower() in [bg.lower() for bg in book_genres] for ug in user_genres):
                    matching_books.append(book['Book'])
            
            # Generate synthetic interactions
            if matching_books:
                n_user_interactions = random.randint(3, 10)
                for _ in range(n_user_interactions):
                    book = random.choice(matching_books)
                    # Simulate higher likelihood of positive interaction for genre-matched books
                    liked = random.random() < 0.7
                    interactions.append({
                        'username': user['User name'],
                        'book_title': book,
                        'liked': liked,
                        'clicked': True,
                        'saved': liked and random.random() < 0.8,
                        'shared': liked and random.random() < 0.4
                    })
        
        return pd.DataFrame(interactions)

    def evaluate_genre_coverage(self):
        """Evaluate how well the system covers different genres."""
        all_genres = set()
        genre_counts = {}
        
        for genres in self.books_df['Genres']:
            try:
            # Safely parse genres as a list of strings
                genre_list = [g.strip() for g in genres.strip('[]').split(',')]
            except AttributeError:
                genre_list = []  # Handle missing or malformed genres
            all_genres.update(genre_list)
            for genre in genre_list:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
                
        coverage_stats = {
            'total_genres': len(all_genres),
            'genre_distribution': {k: v/len(self.books_df) for k, v in genre_counts.items()},
            'coverage_score': len(all_genres) / (len(self.books_df) * 0.1)  # Normalized score
        }
        
        return coverage_stats
    
    def evaluate_content_diversity(self, n_recommendations=5):
        """Evaluate diversity of recommendations across different user profiles."""
        diversity_scores = []
        
        for _, user in self.users_df.iterrows():
            username = user['User name']
            recommendations = []
            
            # Get multiple recommendations
            for _ in range(n_recommendations):
                try:
                    rec = self.recommender.recommend_books_for_user(username)
                    if 'error' not in rec:
                        recommendations.append(rec['book']['title'])
                except:
                    continue
            
            if len(recommendations) > 1:
                # Calculate diversity based on unique recommendations
                diversity_score = len(set(recommendations)) / len(recommendations)
                diversity_scores.append(diversity_score)
        
        return {
            'mean_diversity': np.mean(diversity_scores),
            'std_diversity': np.std(diversity_scores)
        }
    
    def evaluate_cold_start(self):
        """Evaluate system performance for new users with minimal information."""
        test_genres = [
            "Fiction",
            "Mystery, Thriller",
            "Romance, Fantasy",
            "Science Fiction, Horror",
            "Classics, Literature"
        ]
        
        cold_start_scores = []
        for genres in test_genres:
            # Create temporary test user
            test_user = {
                'User name': f'test_user_{len(cold_start_scores)}',
                'Genre': genres,
                'Notes': 'Test user for cold start evaluation',
                'Recommended Books': ''
            }
            
            try:
                recommendation = self.recommender.recommend_books_for_user(test_user['User name'])
                if 'error' not in recommendation:
                    # Score based on genre match
                    genre_match = self.recommender.calculate_genre_match(
                        recommendation['book']['genre'],
                        genres.split(', ')
                    )
                    cold_start_scores.append(genre_match)
            except:
                continue
                
        return {
            'mean_cold_start_score': np.mean(cold_start_scores),
            'std_cold_start_score': np.std(cold_start_scores),
            'n_successful_recs': len(cold_start_scores)
        }

    def plot_genre_distribution(self):
        """Plot genre distribution of recommendations."""
        genre_stats = self.evaluate_genre_coverage()
        
        plt.figure(figsize=(12, 6))
        genres = list(genre_stats['genre_distribution'].keys())
        values = list(genre_stats['genre_distribution'].values())
        
        plt.bar(genres, values)
        plt.xticks(rotation=45, ha='right')
        plt.title('Genre Distribution in Recommendations')
        plt.ylabel('Proportion of Recommendations')
        plt.tight_layout()
        
        return plt

    def plot_recommendation_scores(self):
        """Plot distribution of recommendation match scores."""
        scores = []
        for _, user in self.users_df.iterrows():
            try:
                rec = self.recommender.recommend_books_for_user(user['User name'])
                if 'error' not in rec:
                    scores.append(rec['match_scores'])
            except:
                continue
        
        if scores:
            scores_df = pd.DataFrame(scores)
            
            plt.figure(figsize=(10, 6))
            sns.boxplot(data=scores_df)
            plt.title('Distribution of Recommendation Match Scores')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            return plt

    def generate_evaluation_report(self):
        """Generate comprehensive evaluation report."""
        # Generate synthetic interactions for testing
        interactions = self.generate_synthetic_interactions()
        
        # Run all evaluations
        genre_coverage = self.evaluate_genre_coverage()
        diversity = self.evaluate_content_diversity()
        cold_start = self.evaluate_cold_start()
        
        return {
            'genre_coverage': genre_coverage,
            'content_diversity': diversity,
            'cold_start_performance': cold_start,
            'synthetic_interactions': len(interactions)
        }

# Example usage
evaluator = RecommenderEvaluator(recommender)

# 1. Genre Distribution Plot
plt.figure(1)
evaluator.plot_genre_distribution()
plt.savefig('genre_distribution.png')

# 2. Recommendation Scores Plot
plt.figure(2)
evaluator.plot_recommendation_scores()
plt.savefig('recommendation_scores.png')

results = evaluator.generate_evaluation_report()

print("\nEvaluation Results:")
print(f"Genre Coverage Score: {results['genre_coverage']['coverage_score']:.2f}")
print(f"Mean Content Diversity: {results['content_diversity']['mean_diversity']:.2f}")
print(f"Cold Start Performance: {results['cold_start_performance']['mean_cold_start_score']:.2f}")