import os
from evaluator import RecommendationEvaluator
from visualization import create_evaluation_plots
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recommendation import recommender

def main():
    # Create results directory if it doesn't exist
    if not os.path.exists('evaluation/results'):
        os.makedirs('evaluation/results')
    
    # Initialize evaluator
    print("Initializing evaluator...")
    evaluator = RecommendationEvaluator(recommender)
    
    # Run evaluation and create plots
    print("Running evaluation and creating plots...")
    results = create_evaluation_plots(evaluator)
    
    # Print summary metrics
    print("\nEvaluation Results:")
    print(f"Average Genre Match Score: {results['genre_match_avg']:.2f}%")
    print(f"Average Content Similarity Score: {results['content_similarity_avg']:.2f}%")
    print(f"Sentiment-Playlist Correlation: {results['sentiment_correlation']:.2f}")
    
    print("\nEvaluation completed! Check evaluation/results/evaluation_plots.png for visualizations.")

if __name__ == "__main__":
    main()