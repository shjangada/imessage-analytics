import sqlite3
from datetime import datetime, timedelta
import nltk
from nltk.corpus import stopwords


# Download necessary NLTK data
nltk.download('stopwords')

# Set stop words (you may want to adjust or expand this)
stop_words = set(stopwords.words('english'))
stop_words.update([
    "know", "yes", "much", "okay", "right", "thing", "lot", 
    "got", "make", "even", "say", "today", "still", "last", "things", "first", 
    "makes", "wait", "back", "see", "really", "gonna", "think",
    "need", "wanna", "going", "stuff", "idk", "abt",
    "yeah", "yup"
])
reaction_keywords = ["Loved", "Liked", "Emphasized", "Laughed at", "Disliked"]

time_to_read = 0

# Path to iMessage database
username = "shreyajangada"  # Update this with your username
DB_PATH = f"/Users/{username}/Library/Messages/chat.db"

try:
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    start_of_year_timestamp = (start_of_year - datetime(2001, 1, 1)).total_seconds() * 1e9

    # Fetch messages from this year with non-NULL text
    cursor.execute(
        """
        SELECT text, date, is_from_me, destination_caller_id, date_delivered, date_read
        FROM message
        WHERE text IS NOT null
        """,
    )

    messages = cursor.fetchall()

    total_messages = 0
    from_me = 0
    words_list = []

    print("Messages All Time:")
    for i, (text, date, is_from_me, destination_caller_id, date_delivered, date_read) in enumerate(messages):
        try:
            message_date = datetime(2001, 1, 1) + timedelta(seconds=date / 1e9)
            total_messages += 1
            if is_from_me:
                from_me += 1

            if any(keyword in text for keyword in reaction_keywords):
                continue  # Skip reactions

            words = text.split()
            # Add words to list for frequency distribution (consider only words not in stopwords and short words)
            if is_from_me:
                for word in words:
                    word_lower = word.lower()
                    if "’" in word_lower or word_lower in stop_words or len(word_lower) < 3:
                        continue
                    word_clean = re.sub(r'\W+', '', word_lower)  # Remove non-alphanumeric characters
                    if word_clean:
                        words_list.append(word_clean)

            # Calculate time to read if applicable
            if is_from_me and date_delivered is not None and date_read is not None:
                delivered_time = datetime(2001, 1, 1) + timedelta(seconds=date_delivered / 1e9)
                read_time = datetime(2001, 1, 1) + timedelta(seconds=date_read / 1e9)
                time_to_read += (read_time - delivered_time).total_seconds() / 60.0

        except Exception as e:
            print(f"Error processing message {i + 1}: {e}")

    print(f"\nTotal messages this year: {total_messages}")
    print(f"Messages sent by you: {from_me} ({from_me/total_messages*100:.2f}%) of total messages.")

    # Create a frequency distribution using NLTK's FreqDist
    fd = nltk.FreqDist(words_list)

    # Display frequency distribution in tabular format
    print("\nFrequency Distribution Table (Top 10):")
    fd.tabulate(10)

    # Average text length (in words)
    avg_text_length = sum(len(text.split()) for text, *_ in messages) / total_messages
    print(f"\nAverage text length: {avg_text_length:.2f} words.")

    # Curse word count
    curse_list = ["fuck", "damn", "shit", "ass", "crap", "bitch", "dumbass", "fucking", "asshole", "bastard", "pissed", "motherfucker"]
    curse_count = sum(fd[word] for word in curse_list if word in fd)
    print(f"You cursed {curse_count} times.")

    # Optionally, query a specific word
    target = input("\nIs there any specific word you want to see how much you used? ").lower()
    print(f"'{target}' was used {fd[target]} times.")

except Exception as e:
    print(f"Error accessing database: {e}")
finally:
    conn.close()
