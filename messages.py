import sqlite3
from datetime import datetime, timedelta
import nltk
from nltk.corpus import stopwords
import re
import os

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
DB_PATH = os.path.expanduser("~/Library/Messages/chat.db")

try:
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    start_of_year_timestamp = (start_of_year - datetime(2001, 1, 1)).total_seconds() * 1e9

    # Fetch messages from the database
    cursor.execute(
        """
        SELECT text, date, is_from_me, destination_caller_id, date_delivered, date_read
        FROM message
        WHERE text IS NOT NULL
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
            if is_from_me and date_delivered and date_read:
                delivered_time = datetime(2001, 1, 1) + timedelta(seconds=date_delivered / 1e9)
                read_time = datetime(2001, 1, 1) + timedelta(seconds=date_read / 1e9)
                time_to_read += (read_time - delivered_time).total_seconds() / 60.0

        except Exception as e:
            print(f"Error processing message {i + 1}: {e}")

    print(f"\nTotal messages this year: {total_messages}")
    print(f"Messages sent by you: {from_me} ({from_me / total_messages * 100:.2f}%) of total messages.")

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
    print(f"'{target}' was used {fd.get(target, 0)} times.")

    # Define time segments
    time_segments = {
        "Late Night (00:00-03:59)": 0,
        "Early Morning (04:00-07:59)": 0,
        "Morning (08:00-11:59)": 0,
        "Afternoon (12:00-15:59)": 0,
        "Evening (16:00-19:59)": 0,
        "Night (20:00-23:59)": 0
    }

    # Process each message
    for i, (text, date, is_from_me, *_rest) in enumerate(messages):
        try:
            message_date = datetime(2001, 1, 1) + timedelta(seconds=date / 1e9)
            if is_from_me:  # Count only messages sent by you
                hour = message_date.hour
                if 0 <= hour < 4:
                    time_segments["Late Night (00:00-03:59)"] += 1
                elif 4 <= hour < 8:
                    time_segments["Early Morning (04:00-07:59)"] += 1
                elif 8 <= hour < 12:
                    time_segments["Morning (08:00-11:59)"] += 1
                elif 12 <= hour < 16:
                    time_segments["Afternoon (12:00-15:59)"] += 1
                elif 16 <= hour < 20:
                    time_segments["Evening (16:00-19:59)"] += 1
                elif 20 <= hour < 24:
                    time_segments["Night (20:00-23:59)"] += 1
        except Exception as e:
            print(f"Error processing message {i + 1}: {e}")

    # Display time segment analysis
    print("\nMessages Sent by Time of Day:")
    for segment, count in time_segments.items():
        print(f"{segment}: {count} messages")

    # Determine the segment with the most messages
    most_active_segment = max(time_segments, key=time_segments.get)
    print(f"\nYou sent the most messages during: {most_active_segment}")

except Exception as e:
    print(f"Error accessing database: {e}")
finally:
    conn.close()
