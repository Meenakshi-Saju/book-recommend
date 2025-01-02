import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from recommendation import recommender

def evaluate_recommendation_system(recommender):
    """
    Evaluates using:
    1. Personalization Score - How different recommendations are for different users
    2. Catalog Coverage Score - How well system explores available books
    """
    def calculate_personalization():
        # Get recommendations for all users
        user_recs = {}
        for username in recommender.users_df['User name']:
            try:
                rec = recommender.recommend_books_for_user(username)
                if 'error' not in rec:
                    user_recs[username] = rec['book']['title']
            except:
                continue
        
        # Calculate uniqueness of recommendations
        total_recs = len(user_recs)
        unique_recs = len(set(user_recs.values()))
        return unique_recs / total_recs if total_recs > 0 else 0

    def calculate_coverage():
        # Get recommendations for 100 random samples
        recommended_books = set()
        total_attempts = 100
        
        for _ in range(total_attempts):
            username = np.random.choice(recommender.users_df['User name'])
            try:
                rec = recommender.recommend_books_for_user(username)
                if 'error' not in rec:
                    recommended_books.add(rec['book']['title'])
            except:
                continue
        
        # Calculate coverage
        total_books = len(recommender.books_df)
        return len(recommended_books) / total_books

    personalization = calculate_personalization()
    coverage = calculate_coverage()
    
    return {
        'Personalization Score': personalization * 100,  # Convert to percentage
        'Catalog Coverage Score': coverage * 100  # Convert to percentage
    }

def print_evaluation_results(metrics):
    print("\n=== Academic Evaluation Results ===\n")
    print(f"1. Personalization Score: {metrics['Personalization Score']:.1f}%")
    print("   (Measures how unique recommendations are across users)")
    print(f"\n2. Catalog Coverage Score: {metrics['Catalog Coverage Score']:.1f}%")
    print("   (Measures how well the system explores available books)")

# Usage
metrics = evaluate_recommendation_system(recommender)
print_evaluation_results(metrics)