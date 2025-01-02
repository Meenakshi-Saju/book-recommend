from recommendation import HybridRecommender
from sklearn.metrics import precision_score, recall_score, ndcg_score
from sklearn.model_selection import train_test_split
import numpy as np

class RecommenderEvaluator:
    def __init__(self, recommender):
        self.recommender = recommender
        
    def create_train_test_split(self, test_size=0.2):
        users = self.recommender.users_df['User name'].unique()
        train_users, test_users = train_test_split(users, test_size=test_size)
        
        for username in test_users:
            user_recs = self.recommender.get_user_info(username)['recommendations']
            if len(user_recs) > 1:  # Only split if more than 1 recommendation
                train_recs, test_recs = train_test_split(list(user_recs), test_size=0.5, train_size=0.5)
                self.recommender._user_cache[username]['recommendations'] = set(train_recs)
                self.recommender._user_cache[username]['held_out_recs'] = set(test_recs)
            else:
                # For users with 1 or 0 recommendations, keep in training
                train_users = np.append(train_users, username)
                test_users = test_users[test_users != username]
        
        return train_users, test_users
    
    def evaluate(self, test_users, k=5):
        metrics = {'precision': [], 'recall': [], 'ndcg': []}
        
        for username in test_users:
            actual = self.recommender.get_user_info(username).get('held_out_recs', set())
            if not actual:
                continue
                
            try:
                rec_result = self.recommender.recommend_books_for_user(username)
                if 'error' in rec_result:
                    continue
                predicted = {rec_result['book']['title']}
                
                relevant_and_recommended = len(actual.intersection(predicted))
                
                # Calculate metrics
                metrics['precision'].append(relevant_and_recommended / len(predicted) if predicted else 0)
                metrics['recall'].append(relevant_and_recommended / len(actual) if actual else 0)
                
                # NDCG calculation
                all_books = list(actual.union(predicted))
                y_true = [1 if book in actual else 0 for book in all_books]
                y_pred = [1 if book in predicted else 0 for book in all_books]
                
                if len(y_true) > 0:
                    metrics['ndcg'].append(ndcg_score([y_true], [y_pred]))
                    
            except Exception as e:
                print(f"Error evaluating user {username}: {str(e)}")
                continue
        
        return {metric: np.mean(scores) if scores else 0 
                for metric, scores in metrics.items()}

def test_recommender():
    print("Initializing recommender...")
    recommender = HybridRecommender()
    evaluator = RecommenderEvaluator(recommender)
    
    print("Creating train/test split...")
    train_users, test_users = evaluator.create_train_test_split()
    print(f"Test set size: {len(test_users)} users")
    
    print("Evaluating recommendations...")
    metrics = evaluator.evaluate(test_users)
    
    print("\nEvaluation Results:")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")
    print(f"NDCG: {metrics['ndcg']:.3f}")

if __name__ == "__main__":
    test_recommender()