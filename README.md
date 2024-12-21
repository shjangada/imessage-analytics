# iMessage Analytics Wrapped

This project analyzes your iMessage data to create a wrap-up similar to Spotify Wrapped, providing deep insights into your messaging patterns and communication style.

## Important Note
Currently, the tool analyzes messages from all time instead of just the current year. While the original intention was to provide year-specific analytics like Spotify Wrapped, some users (including the developer) have encountered issues where recent iMessages may not load completely from the local database. If you encounter similar issues, the tool defaults to analyzing your entire message history instead of limiting to the current year.

## Features

### Message Analysis
* **Message Counts**: Tracks total messages and sent/received ratio with percentage breakdowns
* **Word Usage**: Analyzes your most frequently used words, filtering out common stop words
* **Message Length**: Calculates average text length in words
* **Curse Word Tracking**: Monitors usage of specified curse words
* **Custom Word Lookup**: Allows users to check frequency of specific words

### Sentiment Analysis
* **Conversation Tone**: Uses VADER sentiment analysis to evaluate message positivity/negativity
* **Top Contact Rankings**: Ranks your top 10 contacts by message count with sentiment scores
* **Sentiment Trends**: Labels conversations as Positive, Negative, or Neutral based on average sentiment

### Technical Features
* **Smart Filtering**: 
  * Enhanced stop words list tailored for casual conversations
  * Reaction filtering to ignore system messages like "Liked" or "Loved"
  * Minimum word length requirements to focus on meaningful content

## Prerequisites
* Python 3.9+
* Required Python packages:
  * `sqlite3`
  * `nltk`
  * `datetime`
  * `string`

## Installation

1. Install required packages:
```bash
pip install nltk
```

2. Download required NLTK data:
```python
python -m nltk.downloader stopwords
python -m nltk.downloader vader_lexicon
```

## Future Plans
* **Enhanced Visualization**: 
  * Interactive charts and graphs
  * Timeline views of messaging patterns
  * Sentiment distribution visualizations
* **Extended Analysis**:
  * Response time patterns analysis
  * Emoji usage tracking
  * Time-of-day messaging patterns
* **Platform Development**:
  * Web application interface
  * Shareable reports
  * Spotify Wrapped-style animated presentations
* **Advanced Analytics**:
  * Conversation topic modeling
  * Language style matching analysis
  * Relationship dynamics insights
* **Time Period Selection**:
  * Add reliable year-specific filtering once database access issues are resolved
  * Options for custom date ranges

## Usage
The script requires access to your iMessage database located at:
```
/Users/{username}/Library/Messages/chat.db
```
Replace `{username}` with your system username before running.

## Limitations
* Current iMessage database access may be incomplete for recent messages on some systems
* Default behavior analyzes all-time messages instead of year-specific data
* Analysis accuracy depends on local database completeness

## Note
This tool is for personal use only. Be mindful of privacy considerations when analyzing message data.