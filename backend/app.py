from flask import Flask, request, jsonify
from flask_cors import CORS
import csv

import requests
from recommendation import recommend_books_for_user  # Import from recommendation module
from recommendation import recommend_playlist_for_book_entered_by_user
import os
from bs4 import BeautifulSoup




app = Flask(__name__)
CORS(app)

CSV_FILE_USER = 'C:/Users/Sanjana Saju/Documents/meen/S7/FINAL PROJECT/SECOND ATTEMPT/second-attempt/backend/User.csv'
CSV_FILE_BOOKS = 'C:/Users/Sanjana Saju/Documents/meen/S7/FINAL PROJECT/SECOND ATTEMPT/second-attempt/backend/goodreads_data.csv'

if not os.path.exists(CSV_FILE_BOOKS):
    with open(CSV_FILE_BOOKS, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # writer.writerow(['Book Name', 'Author Name', 'Genre', 'Description'])
        writer.writerow(['Book', 'Author', 'Description', 'Genres','Avg_Rating', 'Num_Ratings', 'URL'])



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # genres = ', '.join(data.get('genres', [])) if data.get('genres') else ''
    # notes = data.get('notes', '')  

    try:
        with open(CSV_FILE_USER, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            rows = list(reader)
            if rows:
                last_sno = int(rows[-1][0])
            else:
                last_sno = 0
    except FileNotFoundError:
        last_sno = 0

    new_sno = last_sno + 1
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400
    
    if not genres:
        genres = 'No genres specified'
        
    if not notes:
        notes = 'No notes provided'

    with open(CSV_FILE_USER, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([new_sno, username, password, genres, notes])

    return jsonify({"success": True, "message": "Registration successful!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        with open(CSV_FILE_USER, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row[1] == username and row[2] == password:
                    return jsonify({"success": True, "message": "Login successful!"}), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "User data file not found."}), 500

    return jsonify({"success": False, "message": "Invalid username or password."}), 401



@app.route('/api/save-genres-notes', methods=['POST'])
def save_genres_notes():
    data = request.json
    genres = data.get('genres', [])
    notes = data.get('notes', '')

    # Save genres and notes to the database or file
    print(f"Received genres: {genres}")
    print(f"Received notes: {notes}")

    return jsonify({"success": True, "message": "Genres and notes saved successfully."})


@app.route('/update-genres-notes', methods=['POST'])
def update_genres_notes():
    data = request.get_json()
    username = data.get('username')
    genres = ', '.join(data.get('genres', [])) if data.get('genres') else 'No genres specified'
    notes = data.get('notes', 'No notes provided')

    updated = False

    try:
        # Read all rows from the CSV
        with open(CSV_FILE_USER, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # Update the genres and notes for the given username
        for row in rows:
            if row[1] == username:  # Check if the username matches
                row[3] = genres
                row[4] = notes
                updated = True
                break

        # Write back the updated data to the CSV
        with open(CSV_FILE_USER, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    except FileNotFoundError:
        return jsonify({"success": False, "message": "User database not found."}), 404

    if updated:
        return jsonify({"success": True, "message": "Genres and notes updated successfully!"}), 200
    else:
        return jsonify({"success": False, "message": "Username not found."}), 404


# Recommendation route
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    print("Data received:", data)
    username = data.get('username')

    result = recommend_books_for_user(username, debug=True)  # Set to True if you want debug info

    if "error" in result:
        return jsonify({
            "success": True,
            "message": "No recommendations found for this user. Please check back later."
        }), 200
    
    print("Recommendation result:", result)


    return jsonify({"success": True, "data": result}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Book Recommendation API"}), 200



def get_goodreads_data(book_name, author_name):
    search_url = f"https://www.goodreads.com/search?q={book_name}+{author_name}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        result = soup.find('a', class_='bookTitle')
        
        if result:
            book_link = "https://www.goodreads.com" + result['href']
            book_page = requests.get(book_link, headers=headers)
            book_soup = BeautifulSoup(book_page.content, 'html.parser')
            
            # Using the new selectors provided
            average_rating = book_soup.select_one('.RatingStatistics__rating')
            ratings_count = book_soup.select_one('.RatingStatistics__meta > span:nth-of-type(1)')
            
            return {
                "link": book_link,
                "average_rating": average_rating.get_text(strip=True) if average_rating else "N/A",
                "ratings_count": ratings_count.get_text(strip=True) if ratings_count else "N/A"
            }
        else:
            print("No book found in search results.")
            return {"link": "No book found.", "average_rating": "N/A", "ratings_count": "N/A"}
    else:
        print(f"Failed to retrieve search results. Status code: {response.status_code}")
        return {
            "link": f"Failed to retrieve search results. Status code: {response.status_code}",
            "average_rating": "N/A",
            "ratings_count": "N/A"
        }
    

@app.route('/add-recommendation', methods=['POST'])
def add_recommendation():
    data = request.get_json()
    
    book_name = data.get('bookName')
    author_name = data.get('authorName')
    genre = data.get('genre')
    description = data.get('description')
    
    # Validate required fields
    if not all([book_name, author_name, genre, description]):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400
    
    # Initialize CSV file if it doesn't exist
    if not os.path.exists(CSV_FILE_BOOKS):
        with open(CSV_FILE_BOOKS, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['SNo', 'Book', 'Author', 'Description', 'Genres', 'Avg_Rating', 'Num_Ratings', 'URL'])
            last_sno = 0
    else:
        # Check for duplicates and get last SNo
        try:
            with open(CSV_FILE_BOOKS, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Skip and store headers
                
                # Convert to list to be able to traverse multiple times
                rows = list(reader)
                
                # Check for duplicates
                for row in rows:
                    if row[1].lower().strip() == book_name.lower().strip() and \
                       row[2].lower().strip() == author_name.lower().strip():
                        return jsonify({
                            "success": False,
                            "message": "This book already exists in our recommendations"
                        }), 409
                
                # Get the last SNo
                last_sno = int(rows[-1][0]) if rows else 0
                
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error reading CSV file: {str(e)}"
            }), 500
    
    try:
        # Get Goodreads data
        goodreads_data = get_goodreads_data(book_name, author_name)
        
        # Append the new recommendation
        new_sno = last_sno + 1
        with open(CSV_FILE_BOOKS, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                new_sno,                           # SNo
                book_name.strip(),                 # Book
                author_name.strip(),               # Author
                description.strip(),               # Description
                genre.strip(),                     # Genres
                goodreads_data["average_rating"],  # Avg_Rating
                goodreads_data["ratings_count"],   # Num_Ratings
                goodreads_data["link"]             # URL
            ])
        
        return jsonify({
            "success": True,
            "message": "Recommendation added successfully!"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error adding recommendation: {str(e)}"
        }), 500








@app.route('/song-recommendation', methods=['POST'])
def get_playlist():
    print("Happening!")
    data = request.get_json()
    book_title = data.get('book')  
    
    if not book_title:
        return jsonify({"success": False, "message": "Book title is required"}), 400

    playlist = recommend_playlist_for_book_entered_by_user(book_title)
    
    if not playlist:
        return jsonify({"success": False, "message": "Book not found in database."}), 404

    return jsonify(playlist), 200


@app.route('/search-book', methods=['GET'])
def search_book():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"success": False, "message": "No query provided."}), 400

    try:
        with open(CSV_FILE_BOOKS, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            results = []
            for row in reader:
                if query.lower() in row['Book'].lower():  
                    results.append({
                        'title': row['Book'],
                        'author': row['Author'],
                        'genre': row['Genres'],
                        'description': row['Description'],
                        'url': row.get('URL', '#')  
                    })
            if not results:
                return jsonify({"success": False, "message": "No books found."}), 404

            return jsonify({"success": True, "data": results}), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Book data file not found."}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)

