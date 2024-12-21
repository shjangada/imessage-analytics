import sqlite3
from datetime import datetime, timedelta
import nltk
from nltk.corpus import stopwords
import string


#username = input("What is your device's username? ")
username = "shreyajangada" #for testing purposes
# Path to iMessage database
DB_PATH = f"/Users/{username}/Library/Messages/chat.db"
nltk.download('stopwords')
#nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
stop_words.update([
    "know", "yes", "much", "okay", "right", "thing", "lot", 
    "got", "make", "even", "say", "today", "still", "last", "things", "first", 
    "makes", "wait", "today", "back", "see", "really", "gonna", "think",
    "need", "wanna", "going", "stuff", "idk", "abt",
    "wait", "last", "right", "stuff", "things", "make", "back", "right", "going", "yeah", "yup"
])
reaction_keywords = ["Loved", "Liked", "Emphasized", "Laughed at", "Disliked"]  # Example keywords

time_to_read = 0

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
        WHERE date >= ? and text IS NOT null
        """,
        (start_of_year_timestamp,)
    )

    messages = cursor.fetchall()

    total_messages = 0
    from_me = 0
    word_count = dict()


    print("Messages This Year:")
    for i, (text, date, is_from_me, destination_caller_id, date_delivered, date_read) in enumerate(messages):
        try:
            message_date = datetime(2001, 1, 1) + timedelta(seconds=date / 1e9)
            total_messages += 1
            if(is_from_me):
                from_me +=1 

            if any(keyword in text for keyword in reaction_keywords):
                continue  # skip reactions

            words_list = text.split()
            #go through all the words in text
            if (is_from_me):
                for i in range(len(words_list)):
                    word_lower = words_list[i].lower()                    
                    if "’" in word_lower or word_lower in stop_words or len(word_lower) < 3:
                        continue
                    if word_lower in word_count:
                        word_count[word_lower] += 1
                    else:
                        word_count[word_lower] = 1

            '''
            direction = "Sent" if is_from_me else "Received"
            print(f"{i + 1}: {text}, {direction}")

            delivered_time = datetime(2001, 1, 1) + timedelta(seconds=date_delivered / 1e9)
            read_time = datetime(2001, 1, 1) + timedelta(seconds=date_read / 1e9)

            # Calculate time difference in minutes
            time_to_read = (read_time - delivered_time).total_seconds() / 60.0
            if (time_to_read > 0):
                print(f"Time taken to read: ", {time_to_read}, "minutes.")
            '''

            # THE FOLLOWING IS NOT WORKING
            if is_from_me and date_delivered is not None and date_read is not None:
                delivered_time = datetime(2001, 1, 1) + timedelta(seconds=date_delivered / 1e9)
                read_time = datetime(2001, 1, 1) + timedelta(seconds=date_read / 1e9)
                time_to_read += (read_time - delivered_time).total_seconds() / 60.0

        except Exception as e:
            print(f"Error processing message {i + 1}: {e}")

    print(f"\nTotal messages this year: {total_messages}")
    print(f"\nMessages sent by you: ", from_me, "(", from_me/total_messages*100, "%) of total messages.")
    
    top_words = sorted(word_count.items(), key=lambda item: item[1], reverse=True)[:10]
    print("\nTop *interesting* words used this year:")
    for word, count in top_words:
        print(f"{word}: {count}")

    print("Average text length: ", sum(word_count.values())/from_me, " words.")
    print("Average time left on delivered: ", time_to_read/from_me, " minutes.")

    curse_list = ["fuck", "damn", "shit", "ass", "crap", "bitch", "dumbass", "fucking", "asshole", "bastard", "pissed", "motherfucker"]

    curse_count = 0

    for word in curse_list:
        curse_count += word_count.get(word.lower())
    
    print("You cursed ", curse_count, "times this year. That's an average of ", round(curse_count/365, 3), " times a day!")

    #target = input("\nIs there any specific word you want to see how much you used? ")
    #print(word_count.get(target.lower()))

except Exception as e:
    print(f"Error accessing database: {e}")
