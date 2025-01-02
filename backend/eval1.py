from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict
from recommendation import recommender

def evaluate_recommendation_system(recommender):
    """
    Evaluates the book recommendation system using two metrics
    """
    results = {
        'genre_consistency_scores': [],
        'content_coherence_scores': []
    }
    
    for username in recommender.users_df['User name']:
        try:
            # Get recommendation
            recommendation = recommender.recommend_books_for_user(username)
            if 'error' in recommendation:
                continue
                
            # Get user info
            user_info = recommender.users_df[recommender.users_df['User name'] == username].iloc[0]
            
            # Handle genre field being float
            if isinstance(user_info['Genre'], float):
                preferred_genres = ['Fiction']  # Default genre
            else:
                preferred_genres = [g.strip() for g in user_info['Genre'].split(',')]
            
            user_notes = user_info['Notes']
            
            # 1. Genre Consistency Score - Use the match_scores from recommendation
            genre_score = recommendation['match_scores']['genre_match']
            results['genre_consistency_scores'].append(genre_score)
            
            # 2. Content Coherence Score - Use the notes_match from recommendation
            coherence_score = recommendation['match_scores']['notes_match']
            results['content_coherence_scores'].append(coherence_score)
            
        except Exception as e:
            print(f"Error processing user {username}: {str(e)}")
            continue
    
    metrics = {
        'Genre Consistency Score': np.mean(results['genre_consistency_scores']),
        'Content Coherence Score': np.mean(results['content_coherence_scores']),
    }
    
    return metrics, results

# Rest of the code remains the same

def print_evaluation_results(metrics, results):
    """Prints detailed evaluation results"""
    print("\n=== Recommendation System Evaluation Results ===\n")
    
    print("1. Genre Consistency Score:")
    print(f"   Average: {metrics['Genre Consistency Score']:.2f}%")
    print(f"   Standard Deviation: {np.std(results['genre_consistency_scores']):.2f}%")
    print(f"   Range: {min(results['genre_consistency_scores']):.2f}% - {max(results['genre_consistency_scores']):.2f}%")
    
    print("\n2. Content Coherence Score:")
    print(f"   Average: {metrics['Content Coherence Score']:.2f}%")
    print(f"   Standard Deviation: {np.std(results['content_coherence_scores']):.2f}%")
    print(f"   Range: {min(results['content_coherence_scores']):.2f}% - {max(results['content_coherence_scores']):.2f}%")

# Usage example:
metrics, detailed_results = evaluate_recommendation_system(recommender)
print_evaluation_results(metrics, detailed_results)