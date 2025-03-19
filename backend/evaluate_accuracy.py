import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
from recommendation import HybridRecommender

# Initialize the recommender
recommender = HybridRecommender()

# Run evaluation
y_true, y_scores = recommender.get_true_pred_scores()  # Function to return actual labels & confidence scores

# Compute precision, recall, and thresholds
precision, recall, thresholds = precision_recall_curve(y_true, y_scores)

# Plot Precision-Recall Curve
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, marker='.', label="PR Curve")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve for Book Recommendation System")
plt.legend()
plt.grid()
plt.show()
