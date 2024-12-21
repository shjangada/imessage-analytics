# iMessage Analytics Wrapped

This project analyzes your iMessage data and creates a year-in-review similar to Spotify Wrapped. It provides insights into your messaging habits, including:

- **Message Counts**: Total messages, sent/received breakdown.
- **Top Words**: Your most frequently used "interesting" words.
- **Response Times**: Average time taken to read messages.
- **Top Chats**: Your top 5 most active conversations.
- **Word Choice Dynamics**: Insights into specific types of word choices and patterns.

## Features

- **Custom Stop Words**: Enhanced analysis with the `nltk` library, incorporating additional stop words tailored to casual text conversations.
- **Reaction Filtering**: Ignores reactions like "Liked" or "Loved" to focus on meaningful messages.
- **Detailed Breakdown**: Insight into the dynamics of your most frequent chats.

## Future Plans

- **Sentiment Analysis**: Use natural language processing (NLP) to analyze the tone of your texts and those of your most frequent contacts.
- **Web App**: Transform this script into a user-friendly web application.
- **Data Visualization**: Integrate charts and graphs to represent data visually.
- **Spotify Wrapped-style Summary**: Generate a summary report in a visually appealing format.

## Prerequisites

- **Python 3.9+**
- **Dependencies**:
  - `sqlite3`
  - `nltk`
  - `datetime`
  - `string`

Install the required NLTK data by running:
```bash
python -m nltk.downloader stopwords
