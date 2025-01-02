# visualization_utils.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def create_evaluation_plots(evaluator):
    """Generate all evaluation plots"""
    # Use a basic style that's guaranteed to work
    plt.style.use('default')
    
    # Run evaluations
    print("Running evaluations...")
    genre_results = evaluator.evaluate_genre_consistency()
    playlist_results = evaluator.evaluate_sentiment_playlist_alignment()
    similarity_results = evaluator.evaluate_content_similarity()
    
    # Create plots
    print("Creating plots...")
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Genre Match Distribution
    ax1 = fig.add_subplot(221)
    if not genre_results.empty:
        sns.histplot(data=genre_results, x='match_score', bins=20, ax=ax1, color='skyblue')
    ax1.set_title('Distribution of Genre Match Scores', fontsize=12, pad=20)
    ax1.set_xlabel('Genre Match Score (%)', fontsize=10)
    ax1.set_ylabel('Count', fontsize=10)
    
    # 2. Sentiment-Playlist Correlation
    ax2 = fig.add_subplot(222)
    if not playlist_results.empty:
        sns.scatterplot(data=playlist_results, 
                       x='book_sentiment', 
                       y='playlist_valence',
                       ax=ax2,
                       color='green',
                       alpha=0.5)
    ax2.set_title('Book Sentiment vs Playlist Valence', fontsize=12, pad=20)
    ax2.set_xlabel('Book Sentiment Score', fontsize=10)
    ax2.set_ylabel('Playlist Valence', fontsize=10)
    
    # 3. Content Similarity Distribution
    ax3 = fig.add_subplot(223)
    if not similarity_results.empty:
        sns.histplot(data=similarity_results, x='similarity_score', bins=20, ax=ax3, color='orange')
    ax3.set_title('Distribution of Content Similarity Scores', fontsize=12, pad=20)
    ax3.set_xlabel('Similarity Score (%)', fontsize=10)
    ax3.set_ylabel('Count', fontsize=10)
    
    # 4. System Components Performance
    ax4 = fig.add_subplot(224)
    performance_data = {
        'Component': ['Genre Matching', 'Content Similarity', 'Playlist Alignment'],
        'Average Score': [
            genre_results['match_score'].mean() if not genre_results.empty else 0,
            similarity_results['similarity_score'].mean() if not similarity_results.empty else 0,
            np.corrcoef(playlist_results['book_sentiment'], 
                       playlist_results['playlist_valence'])[0,1] * 100 if not playlist_results.empty else 0
        ]
    }
    performance_df = pd.DataFrame(performance_data)
    sns.barplot(data=performance_df, x='Component', y='Average Score', ax=ax4, color='lightblue')
    ax4.set_title('System Components Performance', fontsize=12, pad=20)
    ax4.set_ylabel('Score (%)', fontsize=10)
    plt.xticks(rotation=45)
    
    # Adjust layout to prevent overlap
    plt.tight_layout(pad=3.0)
    
    # Save plots with high quality
    print("Saving plots...")
    plt.savefig('evaluation_plots.png', dpi=300, bbox_inches='tight')
    
    # Return metrics
    return {
        'genre_match_avg': genre_results['match_score'].mean() if not genre_results.empty else 0,
        'content_similarity_avg': similarity_results['similarity_score'].mean() if not similarity_results.empty else 0,
        'sentiment_correlation': np.corrcoef(playlist_results['book_sentiment'], 
                                           playlist_results['playlist_valence'])[0,1] if not playlist_results.empty else 0,
        'genre_results': genre_results,
        'playlist_results': playlist_results,
        'similarity_results': similarity_results
    }