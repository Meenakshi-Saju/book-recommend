from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from recommendation import HybridRecommender
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookRecommenderApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.recommender = HybridRecommender()
        self.setup_routes()

        # CSV file paths
        self.CSV_FILE_USER = 'User.csv'
        self.CSV_FILE_BOOKS = 'goodreads_data.csv'

        # Ensure CSV files are initialized
        self.initialize_csv_files()

    def initialize_csv_files(self):
        """Ensure necessary CSV files exist with appropriate headers."""
        if not os.path.exists(self.CSV_FILE_USER):
            with open(self.CSV_FILE_USER, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['SNo', 'User name', 'PassWord', 'Preferred Genres', 'Notes', 'Recommended Books'])

        if not os.path.exists(self.CSV_FILE_BOOKS):
            with open(self.CSV_FILE_BOOKS, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['SNo', 'Book', 'Author', 'Description', 'Genres', 'Avg_Rating', 'Num_Ratings', 'URL'])

    def setup_routes(self):
        # Routes for user interactions and feedback
        self.app.route('/book-feedback', methods=['POST'])(self.book_feedback)
        self.app.route('/get-user-interactions', methods=['GET'])(self.get_user_interactions)
        self.app.route('/recommend', methods=['POST'])(self.recommend)
        self.app.route('/add-recommendation', methods=['POST'])(self.add_recommendation)
        self.app.route('/search-book', methods=['GET'])(self.search_book)
        self.app.route('/update-genres-notes', methods=['POST'])(self.update_genres_notes)
        self.app.route('/register', methods=['POST'])(self.register)
        self.app.route('/login', methods=['POST'])(self.login)

    def get_user_interactions(self):
        username = request.args.get('username')
        book_title = request.args.get('bookTitle')

        logger.info(f"Getting interactions for user: {username}, book: {book_title}")

        if not username:
            return jsonify({"success": False, "message": "Username is required"}), 400

        try:
            feedback = self.recommender.get_user_feedback_score(username, book_title)
            logger.info(f"Retrieved feedback: {feedback}")
            return jsonify({"success": True, "data": feedback}), 200
        except Exception as e:
            logger.error(f"Error getting user interactions: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"Error retrieving interactions: {str(e)}"}), 500

    def book_feedback(self):
        logger.info("=== Book Feedback Route Started ===")
        data = request.get_json()
        logger.info(f"Received feedback data: {data}")

        username = data.get('username')
        book_title = data.get('bookTitle')
        feedback_type = data.get('feedbackType')
        value = data.get('value', True)

        if not all([username, book_title, feedback_type]):
            logger.error("Missing required fields")
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        try:
            logger.info("Adding feedback to recommender system...")
            self.recommender.add_user_feedback(username, book_title, feedback_type, value)
            logger.info("Feedback successfully added")
            return jsonify({"success": True, "message": "Feedback recorded successfully"}), 200
        except Exception as e:
            logger.error(f"Error in book_feedback: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"Error recording feedback: {str(e)}"}), 500

    def recommend(self):
        data = request.get_json()
        username = data.get('username')
        logger.info(f"Getting recommendation for user: {username}")

        try:
            result = self.recommender.recommend_books_for_user(username, debug=True)
            return jsonify({"success": True, "data": result}), 200
        except Exception as e:
            logger.error(f"Error in recommend: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"Error getting recommendation: {str(e)}"}), 500

    def add_recommendation(self):
        data = request.get_json()

        book_name = data.get('bookName')
        author_name = data.get('authorName')
        genre = data.get('genre')
        description = data.get('description')

        if not all([book_name, author_name, genre, description]):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        try:
            goodreads_data = self.get_goodreads_data(book_name, author_name)
            self.save_book_recommendation(book_name, author_name, genre, description, goodreads_data)
            return jsonify({"success": True, "message": "Recommendation added successfully!"}), 200
        except Exception as e:
            logger.error(f"Error adding recommendation: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"Error adding recommendation: {str(e)}"}), 500

    def get_goodreads_data(self, book_name, author_name):
        search_url = f"https://www.goodreads.com/search?q={book_name}+{author_name}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            result = soup.find('a', class_='bookTitle')

            if result:
                book_link = "https://www.goodreads.com" + result['href']
                book_page = requests.get(book_link, headers=headers)
                book_soup = BeautifulSoup(book_page.content, 'html.parser')

                average_rating = book_soup.select_one('.RatingStatistics__rating')
                ratings_count = book_soup.select_one('.RatingStatistics__meta > span:nth-of-type(1)')

                return {
                    "link": book_link,
                    "average_rating": average_rating.get_text(strip=True) if average_rating else "N/A",
                    "ratings_count": ratings_count.get_text(strip=True) if ratings_count else "N/A"
                }
        return {"link": "N/A", "average_rating": "N/A", "ratings_count": "N/A"}

    def save_book_recommendation(self, book_name, author_name, genre, description, goodreads_data):
        try:
            with open(self.CSV_FILE_BOOKS, mode='r+', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                last_sno = int(rows[-1][0]) if rows else 0

                writer = csv.writer(file)
                new_sno = last_sno + 1
                writer.writerow([
                    new_sno, book_name.strip(), author_name.strip(), description.strip(),
                    genre.strip(), goodreads_data["average_rating"],
                    goodreads_data["ratings_count"], goodreads_data["link"]
                ])
        except Exception as e:
            logger.error(f"Error saving book recommendation: {str(e)}", exc_info=True)
            raise

    def search_book(self):
        query = request.args.get('query', '')
        if not query:
            return jsonify({"success": False, "message": "No query provided."}), 400

        try:
            with open(self.CSV_FILE_BOOKS, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                results = [
                    {
                        'title': row['Book'],
                        'author': row['Author'],
                        'genre': row['Genres'],
                        'description': row['Description'],
                        'url': row.get('URL', '#')
                    }
                    for row in reader if query.lower() in row['Book'].lower()
                ]
                if not results:
                    return jsonify({"success": False, "message": "No books found."}), 404

                return jsonify({"success": True, "data": results}), 200
        except FileNotFoundError:
            return jsonify({"success": False, "message": "Book data file not found."}), 500

    def update_genres_notes(self):
        data = request.get_json()
        username = data.get('username')
        genres = ', '.join(data.get('genres', [])) if data.get('genres') else 'No genres specified'
        notes = data.get('notes', 'No notes provided')

        updated = False

        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                rows = list(reader)

            for row in rows:
                if row[1] == username:
                    row[3] = genres
                    row[4] = notes
                    updated = True
                    break

            with open(self.CSV_FILE_USER, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)

        except FileNotFoundError:
            return jsonify({"success": False, "message": "User database not found."}), 404

        if updated:
            return jsonify({"success": True, "message": "Genres and notes updated successfully!"}), 200
        else:
            return jsonify({"success": False, "message": "Username not found."}), 404

    def register(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                next(reader)
                rows = list(reader)
                last_sno = int(rows[-1][0]) if rows else 0
        except FileNotFoundError:
            last_sno = 0

        new_sno = last_sno + 1
        with open(self.CSV_FILE_USER, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([new_sno, username, password, '', ''])

        return jsonify({"success": True, "message": "Registration successful!"}), 201

    def login(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row[1] == username and row[2] == password:
                        return jsonify({"success": True, "message": "Login successful!"}), 200
        except FileNotFoundError:
            return jsonify({"success": False, "message": "User data file not found."}), 500

        return jsonify({"success": False, "message": "Invalid username or password."}), 401

# Create the application instance
app_instance = BookRecommenderApp()
app = app_instance.app

if __name__ == '__main__':
    app.run(port=5000, debug=True)
