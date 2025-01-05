import unittest
import numpy as np
import pandas as pd
from recommendation import recommender

class TestRecommendationSystem(unittest.TestCase):
    def setUp(self):
        self.recommender = recommender
        # Add test user with clear preferences
        if 'TestUser' not in self.recommender.users_df['User name'].values:
            test_user = pd.DataFrame({
                'User name': ['TestUser'],
                'Genre': ['Fiction, Fantasy, Adventure'],
                'Notes': ['I love epic fantasy books with magic and adventure'],
                'Recommended Books': ['[]']
            })
            self.recommender.users_df = pd.concat([self.recommender.users_df, test_user], ignore_index=True)
        
    def test_cold_start(self):
        """Test system handles new users with minimal data"""
        result = self.recommender.recommend_books_for_user('nonexistent_user')
        self.assertIn('error', result)
        
    def test_recommendation_consistency(self):
        rec1 = self.recommender.recommend_books_for_user('TestUser')
        rec2 = self.recommender.recommend_books_for_user('TestUser')
    
    # Check that both recommendations maintain high quality scores
        self.assertGreater(rec1['match_scores']['overall_match'], 70)
        self.assertGreater(rec2['match_scores']['overall_match'], 70)
    
    # Check that both recommendations match user genres
        self.assertGreater(rec1['match_scores']['genre_match'], 60)
        self.assertGreater(rec2['match_scores']['genre_match'], 60)
        
    def test_recommendation_consistency(self):
        """Test consistency of recommendations for same user"""
        rec1 = self.recommender.recommend_books_for_user('TestUser')
        rec2 = self.recommender.recommend_books_for_user('TestUser')
        
        self.assertEqual(rec1['book']['title'], rec2['book']['title'])
        
    def test_playlist_generation(self):
        """Test playlist generation quality"""
        sample_description = "A thrilling adventure story with dramatic twists"
        playlist = self.recommender.recommend_playlist_for_book(sample_description)
        
        self.assertIsInstance(playlist, list)
        self.assertGreater(len(playlist), 0)
        self.assertLessEqual(len(playlist), 5)
        
        for song in playlist:
            self.assertIn('song', song)
            self.assertIn('artist', song)
            self.assertIsInstance(song['popularity'], (int, float))
            
    def test_genre_matching(self):
        """Test genre matching logic"""
        score = self.recommender.calculate_genre_match("Fantasy, Adventure", ["Epic Fantasy"])
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
        
    def test_feedback_integration(self):
        """Test feedback system integration"""
        username = 'TestUser'
        book_title = self.recommender.books_df['Book'].iloc[0]
        
        self.recommender.add_user_feedback(username, book_title, 'liked', True)
        feedback = self.recommender.get_user_feedback_score(username, book_title)
        self.assertIsInstance(feedback, (int, float))
        
    def test_embedding_consistency(self):
        """Test embedding generation consistency"""
        desc = "Sample book description"
        emb1 = self.recommender.load_model().encode([desc])
        emb2 = self.recommender.load_model().encode([desc])
        self.assertTrue(np.allclose(emb1, emb2))

if __name__ == '__main__':
    unittest.main(verbosity=2)