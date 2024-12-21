import sqlite3
import nltk
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer
from statistics import mean

nltk.download('vader_lexicon')

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

username = "shreyajangada"
DB_PATH = f"/Users/{username}/Library/Messages/chat.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get the start of the current year
    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    start_of_year_timestamp = int((start_of_year - datetime(2001, 1, 1)).total_seconds() * 1e9)

    # Query to fetch messages grouped by handle.id, from this year
    cursor.execute(
        """
        SELECT 
            handle.id AS handle,
            message.text,
            message.is_from_me
        FROM 
            message
        JOIN 
            chat_message_join ON message.rowid = chat_message_join.message_id
        JOIN 
            chat ON chat_message_join.chat_id = chat.rowid
        JOIN 
            handle ON handle.id = chat.chat_identifier
        WHERE 
            message.text IS NOT NULL
            AND message.date >= ?
        """,
        (start_of_year_timestamp,)
    )

    messages = cursor.fetchall()

    # Dictionary to store messages and sentiment scores by handle
    handle_messages = {}

    # Organize messages by handle id
    for handle, text, is_from_me in messages:
        if not text:  # Skip empty or None messages
            continue
        if handle not in handle_messages:
            handle_messages[handle] = {'messages': [], 'sentiment_scores': []}
        handle_messages[handle]['messages'].append(text)
        
        # Get sentiment score for the message
        sentiment_score = sia.polarity_scores(text)['compound']
        handle_messages[handle]['sentiment_scores'].append(sentiment_score)

    # Create a list of handles with their message count and average sentiment score
    handle_message_counts = []

    for handle, data in handle_messages.items():
        # Calculate average sentiment score for all messages of the handle
        avg_sentiment_score = mean(data['sentiment_scores'])
        positivity = "Positive" if avg_sentiment_score > 0 else "Negative" if avg_sentiment_score < 0 else "Neutral"
        
        # Store handle, message count, and average sentiment score for sorting
        handle_message_counts.append((handle, len(data['messages']), positivity, avg_sentiment_score))

    # Sort the handles by message count (in descending order)
    handle_message_counts.sort(key=lambda x: x[1], reverse=True)

    # Get the top 10 handles by message count
    top_10_handles = handle_message_counts[:10]

    # Print the top 10 handles based on message count
    print("\nTop 10 Handles by Message Count:")
    for handle, message_count, positivity, avg_sentiment_score in top_10_handles:
        print(f"{handle}: {message_count} messages, {positivity} (Avg Sentiment Score: {avg_sentiment_score:.2f})")

except Exception as e:
    print(f"Error: {e}")

finally:
    conn.close()
