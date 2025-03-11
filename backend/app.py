from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
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
        CORS(self.app, resources={
        r"/*": {
            "origins": ["http://localhost:4200"],  # Your Angular app URL
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
        self.recommender = HybridRecommender()
        self.setup_routes()
        # self.app.after_request(self.after_request)

        # CSV file paths
        self.CSV_FILE_USER = 'User.csv'
        self.CSV_FILE_BOOKS = 'goodreads_data.csv'

        # Ensure CSV files are initialized
        self.initialize_csv_files()

    def initialize_csv_files(self):
        """Enhanced CSV initialization with error handling"""
        try:
            if not os.path.exists(self.CSV_FILE_USER):
                logger.info("Creating new user CSV file")
                with open(self.CSV_FILE_USER, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['SNo', 'User name', 'PassWord', 'Genre', 'Notes', 'Recommended Books', 'Age', 'Hobbies'])

            if not os.path.exists(self.CSV_FILE_BOOKS):
                logger.info("Creating new books CSV file")
                with open(self.CSV_FILE_BOOKS, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['SNo', 'Book', 'Author', 'Description', 'Genres', 'Avg_Rating', 'Num_Ratings', 'URL'])

        except Exception as e:
            logger.error(f"Error initializing CSV files: {str(e)}", exc_info=True)
            raise

    def setup_routes(self):
        # Routes for user interactions and feedback
        self.app.route('/get-user-preferences/<username>', methods=['GET'])(self.get_user_preferences)
        self.app.route('/book-feedback', methods=['POST'])(self.book_feedback)
        self.app.route('/get-user-interactions', methods=['GET'])(self.get_user_interactions)
        self.app.route('/recommend', methods=['POST'])(self.recommend)
        self.app.route('/add-recommendation', methods=['POST'])(self.add_recommendation)
        self.app.route('/search-book', methods=['GET'])(self.search_book)
        self.app.route('/update-genres-notes', methods=['POST'])(self.update_genres_notes)
        self.app.route('/update-profile', methods=['POST'])(self.update_profile)
        self.app.route('/register', methods=['POST'])(self.register)
        self.app.route('/login', methods=['POST'])(self.login)
        self.app.route('/song-recommendation', methods=['POST'])(self.login)
        self.app.route('/get-user-profile/<username>', methods=['GET'])(self.get_user_profile)
        # self.app.route('/song-recommendation', methods=['POST', 'OPTIONS'])(self.get_song_recommendations)
    
    def get_playlist(self):
        print("Processing playlist request")
        data = request.get_json()
        book_title = data.get('book')  
    
        if not book_title:
            return jsonify({"success": False, "message": "Book title is required"}), 400

        playlist = self.recommender.get_playlist(book_title)
    
        if not playlist:
            return jsonify({"success": False, "message": "Book not found in database."}), 404

        return jsonify({"success": True, "data": playlist}), 200

    def get_user_preferences(self, username):
        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row[1] == username:
                        return jsonify({
                        "success": True,
                        "data": {
                            "genres": row[3].split(', ') if row[3] else [],
                            "notes": row[4]
                        }
                    }), 200
            return jsonify({"success": False, "message": "User not found"}), 404
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": "Failed to get preferences"}), 500
    
    def get_user_profile(self, username):
        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row[1] == username:
                        # Check if we have age and hobbies fields (handle backwards compatibility)
                        age = row[6] if len(row) > 6 else ""
                        hobbies = row[7].split(', ') if len(row) > 7 and row[7] else []
                        
                        return jsonify({
                            "success": True,
                            "data": {
                                "genres": row[3].split(', ') if row[3] else [],
                                "notes": row[4],
                                "age": age,
                                "hobbies": hobbies
                            }
                        }), 200
            return jsonify({"success": False, "message": "User not found"}), 404
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": "Failed to get user profile"}), 500

    def after_request(self, response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    


    def get_user_interactions(self):
        """Enhanced user interactions endpoint"""
        try:
            username = request.args.get('username')
            book_title = request.args.get('bookTitle')

            logger.info(f"Getting interactions for user: {username}, book: {book_title}")

            if not username or not book_title:
                return jsonify({
                    "success": False,
                    "message": "Both username and bookTitle are required"
                }), 400

            feedback = self.recommender.get_user_feedback_score(username, book_title)
            logger.info(f"Retrieved feedback: {feedback}")
            
            return jsonify({
                "success": True,
                "data": feedback
            }), 200

        except Exception as e:
            logger.error(f"Error getting user interactions: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": f"Error retrieving interactions: {str(e)}"
            }), 500

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
        """Enhanced recommendation endpoint with better error handling and logging"""
        try:
            data = request.get_json()
            username = data.get('username')
            
            if not username:
                logger.error("No username provided in recommendation request")
                return jsonify({
                    "success": False,
                    "message": "Username is required"
                }), 400

            logger.info(f"Getting recommendation for user: {username}")
            logger.info(f"Request payload: {data}")

            # Check if user exists first
            user_exists = False
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row[1] == username:
                        user_exists = True
                        break

            if not user_exists:
                logger.error(f"User {username} not found in database")
                return jsonify({
                    "success": False,
                    "message": f"User {username} not found"
                }), 404

            # Get recommendation with detailed error catching
            try:
                result = self.recommender.recommend_books_for_user(username, debug=True)
                
                if not result:
                    logger.error(f"No recommendation generated for user: {username}")
                    return jsonify({
                        "success": False,
                        "message": "No recommendations available"
                    }), 404

                if "error" in result:
                    logger.error(f"Recommendation error for user {username}: {result['error']}")
                    return jsonify({
                        "success": False,
                        "message": result["error"]
                    }), 404

                logger.info(f"Successfully generated recommendation for user {username}")
                logger.info(f"Recommendation result: {result}")
                
                return jsonify({
                    "success": True,
                    "data": result
                }), 200

            except Exception as rec_error:
                logger.error(f"Recommendation generation error: {str(rec_error)}", exc_info=True)
                return jsonify({
                    "success": False,
                    "message": f"Failed to generate recommendation: {str(rec_error)}"
                }), 500

        except Exception as e:
            logger.error(f"General recommendation endpoint error: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": f"Error processing recommendation request: {str(e)}"
            }), 500

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
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        data = request.get_json()
        username = data.get('username')
        genres = ', '.join(data.get('genres', [])) if data.get('genres') else 'No genres specified'
        notes = data.get('notes', 'No notes provided')

        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                rows = list(reader)

            user_found = False
            for row in rows:
                if row[1] == username:
                    row[3] = genres
                    row[4] = notes
                    user_found = True
                    break

            if not user_found:
                return jsonify({"success": False, "message": "User not found"}), 404

            with open(self.CSV_FILE_USER, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)

            return jsonify({"success": True, "message": "Preferences updated successfully!"}), 200

        except Exception as e:
            logger.error(f"Update preferences error: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": "Failed to update preferences"}), 500
    
    def update_profile(self):
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        data = request.get_json()
        username = data.get('username')
        age = data.get('age', '')
        hobbies = ', '.join(data.get('hobbies', [])) if data.get('hobbies') else ''

        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                rows = list(reader)

            user_found = False
            for row in rows:
                if row[1] == username:
                    # Ensure we have enough columns for age and hobbies
                    while len(row) < 8:
                        row.append('')
                    
                    row[6] = str(age)  # Age at index 6
                    row[7] = hobbies   # Hobbies at index 7
                    user_found = True
                    break

            if not user_found:
                return jsonify({"success": False, "message": "User not found"}), 404

            with open(self.CSV_FILE_USER, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)

            return jsonify({"success": True, "message": "Profile updated successfully!"}), 200

        except Exception as e:
            logger.error(f"Update profile error: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": "Failed to update profile"}), 500

    def register(self):
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        age = data.get('age', '')
        hobbies = ', '.join(data.get('hobbies', [])) if data.get('hobbies') else ''

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required"}), 400

        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                rows = list(reader)
                last_sno = int(rows[-1][0]) if rows else 0

            new_sno = last_sno + 1
            with open(self.CSV_FILE_USER, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([new_sno, username, password, '', '', '', age, hobbies])

            return jsonify({"success": True, "message": "Registration successful!"}), 201

        except Exception as e:
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": "Registration failed"}), 500
        

    def login(self):
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            with open(self.CSV_FILE_USER, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row[1] == username and row[2] == password:
                        return jsonify({"success": True, "message": "Login successful!"}), 200

            return jsonify({"success": False, "message": "Invalid username or password"}), 401

        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": "Login failed"}), 500

# Create the application instance
app_instance = BookRecommenderApp()
app = app_instance.app

if __name__ == '__main__':
    app.run(port=5000, debug=True)