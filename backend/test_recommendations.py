import pandas as pd
from recommendation import HybridRecommender
import logging
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc

class RecommendationAccuracyTester:
    def __init__(self, test_data_path='book_tests.csv', user_data_path='User.csv'):
        """Initialize the tester with test dataset and user data"""
        if not os.path.exists(test_data_path):
            raise FileNotFoundError(f"Test data file '{test_data_path}' not found.")
        if not os.path.exists(user_data_path):
            raise FileNotFoundError(f"User data file '{user_data_path}' not found.")
        
        self.test_data = pd.read_csv(test_data_path)
        self.user_data_path = user_data_path
        self.recommender = HybridRecommender()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Set up logging for debugging"""
        logger = logging.getLogger('AccuracyTester')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def clean_book_title(self, title):
        """Clean book title for comparison"""
        return str(title).lower().strip() if pd.notna(title) else ""

    def test_recommendation_accuracy(self):
        """Test the recommendation accuracy using user notes and genres only (ignoring usernames)"""
        total_users = len(self.test_data)
        total_processed = 0
        results = []

        self.logger.info("🔍 Starting recommendation accuracy test...")

        for _, row in self.test_data.iterrows():
            user_notes = str(row['Notes']).strip() if pd.notna(row['Notes']) else ""
            user_genres = str(row['Genre']).split(',') if pd.notna(row['Genre']) else []
            actual_book = self.clean_book_title(row['Recommended Books'])

            if not actual_book:
                continue  # Skip users with no expected book recommendation

            # Create a temporary test user and save it to User.csv
            temp_username = f"test_user_{total_processed}"
            new_user = pd.DataFrame([{
                'Reg No': "TEST123",
                'User name': temp_username, 
                'Password': "test_pass",
                'Genre': ', '.join(user_genres), 
                'Notes': user_notes, 
                'Recommended Books': ''
            }])
            
            # Append new test user to User.csv
            new_user.to_csv(self.user_data_path, mode="a", header=False, index=False)

            # Force recommender to reload User.csv
            self.recommender.users_df = pd.read_csv(self.user_data_path)

            try:
                recommendation = self.recommender.recommend_books_for_user(temp_username)
                total_processed += 1

                if "error" not in recommendation:
                    recommended_book = self.clean_book_title(recommendation['book']['title'])
                    is_match = recommended_book == actual_book

                    results.append({
                        'actual_book': actual_book,
                        'recommended_book': recommended_book,
                        'matched': is_match
                    })

            except Exception as e:
                self.logger.error(f"❌ Error processing recommendation: {str(e)}")

        # Compute Metrics
        TP = sum(1 for result in results if result['matched'])  # True Positives
        FP = sum(1 for result in results if not result['matched'])  # False Positives
        FN = total_processed - TP  # False Negatives

        # Fixed Calculations
        accuracy = TP / total_processed if total_processed > 0 else 0
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Print Debugging Info
        print(f"\n✅ Correct Predictions: {TP}")
        print(f"❌ Incorrect Predictions: {FP}")
        print(f"📌 Total Tested: {total_processed}")
        print(f"📊 Accuracy: {accuracy:.2%}")
        print(f"📌 Precision: {precision:.2%}")
        print(f"📌 Recall: {recall:.2%}")
        print(f"📌 F1 Score: {f1_score:.2%}")

        # Save detailed results
        results_df = pd.DataFrame(results)
        results_df.to_csv('recommendation_test_results.csv', index=False)

        # Generate Visualizations
        self.plot_metrics(accuracy, precision, recall, f1_score)
        self.plot_confusion_matrix(results)
        self.plot_roc_curve(results)

        return {
            'total_tested': total_processed,
            'correct_matches': TP,
            'incorrect_matches': FP,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }

    def plot_metrics(self, accuracy, precision, recall, f1_score):
        """Plot Accuracy, Precision, Recall, F1 Score"""
        metrics = ["Accuracy", "Precision", "Recall", "F1 Score"]
        values = [accuracy, precision, recall, f1_score]

        plt.figure(figsize=(8, 5))
        sns.barplot(x=metrics, y=values, palette="viridis")
        plt.ylim(0, 1)
        plt.title("Recommendation System Performance Metrics")
        plt.ylabel("Score")
        plt.show()

    def plot_confusion_matrix(self, results):
        """Plot a confusion matrix for matches vs mismatches"""
        match_counts = pd.DataFrame(results)['matched'].value_counts()
        match_labels = ['Correct', 'Incorrect']
        match_values = [match_counts.get(True, 0), match_counts.get(False, 0)]

        plt.figure(figsize=(6, 6))
        plt.pie(match_values, labels=match_labels, autopct='%1.1f%%', colors=['green', 'red'])
        plt.title("Recommendation Match vs Mismatch")
        plt.show()

    def plot_roc_curve(self, results):
        """Generate and plot ROC Curve"""
        y_true = [1 if result['matched'] else 0 for result in results]  # Convert to binary (1 = Correct, 0 = Incorrect)
        y_scores = [1 if result['matched'] else 0 for result in results]  # Score is 1 for correct, 0 for incorrect

        fpr, tpr, _ = roc_curve(y_true, y_scores)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', lw=2, label=f"ROC Curve (AUC = {roc_auc:.2f})")
        plt.plot([0, 1], [0, 1], color='gray', linestyle='--')  # Diagonal line (random guess)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve for Recommendation System")
        plt.legend(loc="lower right")
        plt.show()

# Run the test
if __name__ == "__main__":
    tester = RecommendationAccuracyTester()
    results = tester.test_recommendation_accuracy()
