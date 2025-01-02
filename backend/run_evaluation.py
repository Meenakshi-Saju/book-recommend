# File 3: run_evaluation.py
from evaluator_class import RecommendationEvaluator
from visualization_utils import create_evaluation_plots
from recommendation import recommender

def main():
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
    
    print("\nEvaluation completed! Check evaluation_plots.png for visualizations.")

if __name__ == "__main__":
    main()