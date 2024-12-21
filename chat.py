import sqlite3
from datetime import datetime

# username = input("What is your device's username? ")
username = "shreyajangada"  # for testing purposes

# Path to iMessage database
DB_PATH = f"/Users/{username}/Library/Messages/chat.db"

try:
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Calculate timestamp for the start of the year (nanoseconds since 2001-01-01)
    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    start_of_year_timestamp = int((start_of_year - datetime(2001, 1, 1)).total_seconds() * 1e9)
    
    # Query for top 5 chats with sent/received breakdown
    cursor.execute(
        """
        SELECT 
            handle.id AS handle, -- Chat identifier (e.g., phone number/email)
            SUM(CASE WHEN message.is_from_me = 1 THEN 1 ELSE 0 END) AS sent_count, -- Sent messages
            SUM(CASE WHEN message.is_from_me = 0 THEN 1 ELSE 0 END) AS received_count -- Received messages
        FROM 
            message
        JOIN 
            chat_message_join ON message.rowid = chat_message_join.message_id
        JOIN 
            chat ON chat_message_join.chat_id = chat.rowid
        LEFT JOIN 
            handle ON handle.id = chat.chat_identifier
        WHERE 
            message.text IS NOT NULL -- Ensure message has text
            AND handle.id IS NOT NULL -- Ensure handle exists
            AND message.date >= ? -- Filter by date (start of the year)
        GROUP BY 
            handle.id -- Group by chat handle
        ORDER BY 
            sent_count + received_count DESC -- Order by message count
        LIMIT 5; -- Limit to top 5 chats
        """,
        (start_of_year_timestamp,)
    )

    # Fetch and display the results
    top_chats = cursor.fetchall()

    print("\nTop 5 Chats This Year:")
    for handle, sent_count, received_count in top_chats:
        print(f"{handle}: {sent_count + received_count} total messages. {sent_count} sent, {received_count} received.")

except Exception as e:
    print(f"Error fetching top chats: {e}")

finally:
    # Ensure the database connection is closed
    conn.close()
