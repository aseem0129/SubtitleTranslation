import sqlite3
from flask import Flask, request, render_template, jsonify
from utils import get_subtitles, download_subtitles, parse_subtitles, translate_subtitles

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('subtitles.db')
    c = conn.cursor()

    # Create subtitles table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS subtitles
                 (id INTEGER PRIMARY KEY, video_url TEXT, original_text TEXT, translated_text TEXT, target_language TEXT)''')

    # Clear all existing records from the subtitles table
    c.execute('DELETE FROM subtitles')

    # Create usage metrics table for tracking user actions
    c.execute('''CREATE TABLE IF NOT EXISTS usage_metrics
                 (id INTEGER PRIMARY KEY, video_url TEXT, target_language TEXT, request_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()


@app.route('/')
def index():
    # Render the form for user input
    return render_template('index.html')


def log_usage(video_url, target_language):
    conn = sqlite3.connect('subtitles.db')
    c = conn.cursor()

    # Insert the video URL and target language into the usage_metrics table
    c.execute("INSERT INTO usage_metrics (video_url, target_language) VALUES (?, ?)", (video_url, target_language))

    conn.commit()
    conn.close()


@app.route('/translate_video', methods=['POST'])
def translate_video():
    # Get the video URL and target language from the form
    video_url = request.form.get('video_url')
    target_language = request.form.get('target_language')

    # Check if both URL and language are provided
    if not video_url or not target_language:
        return "Error: Both video URL and target language are required.", 400

    # Fetch subtitles from the video URL
    subtitle_url = get_subtitles(video_url)
    if not subtitle_url:
        return "Error: No subtitles found for the video.", 400

    # Download, parse, and translate subtitles
    subtitle_json = download_subtitles(subtitle_url)
    parsed_subtitles = parse_subtitles(subtitle_json)

    # Call the translate_subtitles function with only two arguments
    translated_subtitles = translate_subtitles(parsed_subtitles, target_language)

    # Save subtitles to the database
    save_to_db(video_url, parsed_subtitles, translated_subtitles, target_language)

    # Log the usage metrics
    log_usage(video_url, target_language)

    return "Subtitles have been translated and stored in the database."


def save_to_db(video_url, original_text, translated_text, target_language):
    conn = sqlite3.connect('subtitles.db')
    c = conn.cursor()

    # Insert the original and translated subtitles into the database
    c.execute("INSERT INTO subtitles (video_url, original_text, translated_text, target_language) VALUES (?, ?, ?, ?)",
              (video_url, original_text, translated_text, target_language))

    # Insert the special "end_of_subtitles" line
    c.execute("INSERT INTO subtitles (video_url, original_text, translated_text, target_language) VALUES (?, ?, ?, ?)",
              (video_url, "end_of_subtitles", "end_of_subtitles", target_language))

    conn.commit()
    conn.close()


# Route for getting the next batch of words from the database
@app.route('/get_next_words', methods=['GET'])
def get_next_words():
    # Get the current page number from the query parameters
    page = request.args.get('page', 1, type=int)
    words_per_page = 5
    offset = (page - 1) * words_per_page

    # Connect to the database and fetch all translated subtitles
    conn = sqlite3.connect('subtitles.db')
    c = conn.cursor()
    c.execute("SELECT translated_text FROM subtitles")
    data = c.fetchall()
    conn.close()

    # Combine translated subtitles and split them into individual words
    all_translated_words = " ".join([row[0] for row in data]).split()

    # If there are no more words to display, stop
    if offset >= len(all_translated_words):
        return jsonify({"translated_words": [], "has_more": False})

    # Get the current 5 words for the translated subtitles
    translated_words_to_display = all_translated_words[offset:offset + words_per_page]

    return jsonify({
        "translated_words": translated_words_to_display,
        "has_more": offset + words_per_page < len(all_translated_words)
    })


def print_database_contents():
    conn = sqlite3.connect('subtitles.db')
    c = conn.cursor()

    # Select everything from the subtitles table
    c.execute("SELECT * FROM subtitles")
    data = c.fetchall()

    # Print each row to the terminal
    for row in data:
        print(row)

    conn.close()


@app.route('/metrics', methods=['GET'])
def show_metrics():
    conn = sqlite3.connect('subtitles.db')
    c = conn.cursor()

    # Fetch metrics data: target language and the number of times it has been requested
    c.execute("SELECT target_language, COUNT(*) as count FROM usage_metrics GROUP BY target_language")
    data = c.fetchall()

    conn.close()

    return render_template('metrics.html', data=data)

def print_all_metrics():
    conn = sqlite3.connect('subtitles.db')
    c = conn.cursor()

    # Fetch all records from the usage_metrics table
    c.execute("SELECT * FROM usage_metrics")
    data = c.fetchall()

    # Print each row to the terminal
    print("ID | Video URL | Target Language | Timestamp")
    print("-" * 50)
    for row in data:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

    conn.close()

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    print_all_metrics()
    app.run(debug=True)


















