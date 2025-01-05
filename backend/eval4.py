import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import random

# Create synthetic test data
def generate_test_data():
    # Sample book titles
    books = [
        "The Alchemist", "1984", "Dune", "Foundation", 
        "Neuromancer", "Snow Crash", "The Hobbit",
        "Ender's Game", "The Name of the Wind", "The Way of Kings",
        "The Final Empire", "The Lies of Locke Lamora",
        "The Night Circus", "Red Rising", "The Martian"
    ]
    
    # Generate synthetic users with reading preferences
    users = []
    for i in range(20):  # Generate 20 users
        username = f"user_{i}"
        # Randomly assign 2-5 favorite books to each user
        favorite_books = random.sample(books, random.randint(2, 5))
        users.append({
            'username': username,
            'favorites': favorite_books,
            'genre_preference': random.choice(['fantasy', 'sci-fi', 'general'])
        })
    
    return users, books

class TestRecommender:
    def __init__(self, users, books):
        self.users = users
        self.books = books
        
    def recommend_books_for_user(self, username):
        # Find the user
        user = next((u for u in self.users if u['username'] == username), None)
        if not user:
            return {'error': 'User not found'}
            
        # Simple recommendation logic: recommend books they haven't read
        # with some randomization to create more interesting patterns
        unread_books = [b for b in self.books if b not in user['favorites']]
        num_recommendations = random.randint(2, 4)
        recommended_books = random.sample(unread_books, min(num_recommendations, len(unread_books)))
        
        return {'books': recommended_books}

def analyze_recommendation_diversity(recommender):
    # Create recommendation graph
    G = nx.Graph()
    recommendations = defaultdict(list)
    
    # Get recommendations for each user
    for user in recommender.users:
        username = user['username']
        try:
            rec = recommender.recommend_books_for_user(username)
            if 'books' in rec:
                for book in rec['books']:
                    G.add_edge(username, book)
                    recommendations[username].append(book)
        except Exception as e:
            print(f"Error processing user {username}: {e}")
            continue
    
    # Calculate metrics
    avg_clustering = nx.average_clustering(G)
    unique_books = len(set(b for books in recommendations.values() for b in books))
    total_users = len(recommendations)
    diversity_score = unique_books / len(recommender.books) if recommender.books else 0
    
    # Create visualization
    plt.figure(figsize=(15, 10))
    
    # Set node colors
    node_colors = ['lightblue' if node.startswith('user_') else 'lightgreen' 
                  for node in G.nodes()]
    
    # Draw network
    pos = nx.spring_layout(G, k=1, iterations=50)
    nx.draw(G, pos, node_color=node_colors, with_labels=True, 
            node_size=1000, font_size=8, font_weight='bold')
    
    plt.title("Recommendation Network Analysis\n"
             f"Diversity Score: {diversity_score:.2f}\n"
             f"Network Clustering: {avg_clustering:.2f}\n"
             f"Users: {total_users}, Unique Books: {unique_books}")
    
    plt.savefig('recommendation_diversity.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    return {
        'diversity_score': diversity_score * 100,
        'clustering_coefficient': avg_clustering * 100,
        'unique_recommendations': unique_books,
        'total_users': total_users,
        'average_recommendations_per_user': sum(len(r) for r in recommendations.values()) / total_users if total_users > 0 else 0
    }

# Run the analysis
users, books = generate_test_data()
recommender = TestRecommender(users, books)
metrics = analyze_recommendation_diversity(recommender)

print("\nRecommendation Diversity Analysis Results")
print(f"Diversity Score: {metrics['diversity_score']:.1f}%")
print(f"Network Clustering: {metrics['clustering_coefficient']:.1f}%")
print(f"Unique Recommendations: {metrics['unique_recommendations']}")
print(f"Total Users: {metrics['total_users']}")
print(f"Avg Recommendations Per User: {metrics['average_recommendations_per_user']:.1f}")