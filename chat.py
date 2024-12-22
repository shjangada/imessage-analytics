import sqlite3
import nltk
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from statistics import mean

# Initialize NLTK tools and sentiment analyzer
"""
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger_eng')
"""
sia = SentimentIntensityAnalyzer()

# Path to the database
username = "shreyajangada"
DB_PATH = f"/Users/{username}/Library/Messages/chat.db"

# Example politeness markers
POLITENESS_MARKERS = {"please", "thank", "thanks", "kindly", "appreciate", "sorry"}

# Stopwords set
STOP_WORDS = set(stopwords.words("english"))

def preprocess_text(text):
    """Tokenize and preprocess text by removing stopwords."""
    tokens = word_tokenize(text.lower())
    return set(word for word in tokens if word.isalnum() and word not in STOP_WORDS)

def calculate_politeness(messages):
    """Calculate politeness score based on politeness markers."""
    total_words = 0
    polite_words = 0

    for message in messages:
        tokens = word_tokenize(message.lower())
        tagged_words = pos_tag(tokens)
        for word, tag in tagged_words:
            if word in POLITENESS_MARKERS:
                polite_words += 1
            total_words += 1

    return polite_words / total_words if total_words > 0 else 0

def calculate_jaccard_similarity(my_messages, their_messages):
    """Calculate Jaccard similarity between two sets of messages."""
    my_words = set()
    their_words = set()

    for message in my_messages:
        my_words.update(preprocess_text(message))
    for message in their_messages:
        their_words.update(preprocess_text(message))

    intersection = my_words.intersection(their_words)
    union = my_words.union(their_words)

    if not union:  # Avoid division by zero if both sets are empty
        return 0.0

    return len(intersection) / len(union)

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
        """,
    )

    messages = cursor.fetchall()

    # Dictionary to store messages by handle
    handle_messages = {}
    my_sentiment_scores = []

    # Organize messages by handle id
    for handle, text, is_from_me in messages:
        if not text:  # Skip empty or None messages
            continue
        if handle not in handle_messages:
            handle_messages[handle] = {'messages': [], 'sentiment_scores': []}
        handle_messages[handle]['messages'].append((text, is_from_me))
        
        # Get sentiment score for the message
        sentiment_score = sia.polarity_scores(text)['compound']
        handle_messages[handle]['sentiment_scores'].append(sentiment_score)
        
        if is_from_me == 1:
            my_sentiment_scores.append(sentiment_score)

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
    top_10_handles.sort(key=lambda x: x[3], reverse=True)

    if my_sentiment_scores:
        avg_my_sentiment_score = mean(my_sentiment_scores)
        my_positivity = "Positive" if avg_my_sentiment_score > 0 else "Negative" if avg_my_sentiment_score < 0 else "Neutral"
        print(f"\nYour Sentiment: {my_positivity} (Avg Sentiment Score: {avg_my_sentiment_score:.2f})")

    # Print the top 10 handles based on message count
    print("\nThe 10 people you talk to the most, ranked by their positivity:")
    for handle, message_count, positivity, avg_sentiment_score in top_10_handles:
        print(f"{handle}: {message_count} messages, {positivity} (Avg Sentiment Score: {avg_sentiment_score:.2f})")

    # Calculate politeness scores for each handle
    politeness_scores = {}
    blend_rates = {}
    for handle, message_count, positivity, avg_sentiment_score in top_10_handles:
        data = handle_messages[handle]
        messages = [msg[0] for msg in data['messages']]
        my_messages = [msg[0] for msg in data['messages'] if msg[1] == 1]
        their_messages = [msg[0] for msg in data['messages'] if msg[1] == 0]

        politeness_scores[handle] = calculate_politeness(messages)
        blend_rates[handle] = calculate_jaccard_similarity(my_messages, their_messages)

    # Output politeness scores
    print("\nPoliteness Ratings:")
    for handle, score in politeness_scores.items():
        print(f"{handle}: {score:.2f}")

    # Output blend rates, ordered from greatest to least
    print("\nBlend Rates (Jaccard Similarity):")
    sorted_blend_rates = sorted(blend_rates.items(), key=lambda x: x[1], reverse=True)

    for handle, rate in sorted_blend_rates:
        print(f"{handle}: {rate:.2f}")


except Exception as e:
    print(f"Error: {e}")

finally:
    conn.close()
