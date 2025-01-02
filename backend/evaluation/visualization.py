import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def create_evaluation_plots(evaluator):
    """Generate all evaluation plots"""
    plt.style.use('seaborn')
    
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
    sns.histplot(data=genre_results, x='match_score', bins=20, ax=ax1)
    ax1.set_title('Distribution of Genre Match Scores')
    ax1.set_xlabel('Genre Match Score (%)')
    ax1.set_ylabel('Count')
    
    # 2. Sentiment-Playlist Correlation
    ax2 = fig.add_subplot(222)
    sns.scatterplot(data=playlist_results, 
                   x='book_sentiment', 
                   y='playlist_valence',
                   ax=ax2)
    ax2.set_title('Book Sentiment vs Playlist Valence')
    ax2.set_xlabel('Book Sentiment Score')
    ax2.set_ylabel('Playlist Valence')
    
    # 3. Content Similarity Distribution
    ax3 = fig.add_subplot(223)
    sns.histplot(data=similarity_results, x='similarity_score', bins=20, ax=ax3)
    ax3.set_title('Distribution of Content Similarity Scores')
    ax3.set_xlabel('Similarity Score (%)')
    ax3.set_ylabel('Count')
    
    # 4. System Components Performance
    ax4 = fig.add_subplot(224)
    performance_data = {
        'Component': ['Genre Matching', 'Content Similarity', 'Playlist Alignment'],
        'Average Score': [
            genre_results['match_score'].mean(),
            similarity_results['similarity_score'].mean(),
            np.corrcoef(playlist_results['book_sentiment'], 
                       playlist_results['playlist_valence'])[0,1] * 100
        ]
    }
    performance_df = pd.DataFrame(performance_data)
    sns.barplot(data=performance_df, x='Component', y='Average Score', ax=ax4)
    ax4.set_title('System Components Performance')
    ax4.set_ylabel('Score (%)')
    
    plt.tight_layout()
    
    # Save plots
    print("Saving plots...")
    plt.savefig('evaluation/results/evaluation_plots.png', dpi=300, bbox_inches='tight')
    
    # Return metrics
    return {
        'genre_match_avg': genre_results['match_score'].mean(),
        'content_similarity_avg': similarity_results['similarity_score'].mean(),
        'sentiment_correlation': np.corrcoef(playlist_results['book_sentiment'], 
                                           playlist_results['playlist_valence'])[0,1],
        'genre_results': genre_results,
        'playlist_results': playlist_results,
        'similarity_results': similarity_results
    }
