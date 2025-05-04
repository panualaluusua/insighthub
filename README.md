# Reddit Weekly Top

A Python tool to fetch the top weekly posts from selected subreddits and upload them directly to NotebookLM. This tool returns both link posts and text-only posts from the most popular content in your selected subreddits.

## Quick Start

After installation, fetch and upload Reddit posts with a single command:
# Example sub reddits: ChatGPTCoding, Cursor, etc.
```bash
# Fetch and upload top weekly posts from specific subreddits
python -m reddit_weekly_top.scripts.fetch_and_upload -s python programming

# Fetch monthly top posts instead of weekly
python -m reddit_weekly_top.scripts.fetch_and_upload -s dataengineering -l 25 -t month

# Only include posts with high scores
python -m reddit_weekly_top.scripts.fetch_and_upload -s python --min-score 100

# Customize number of posts per subreddit
python -m reddit_weekly_top.scripts.fetch_and_upload -s python -l 5
```

The script will:
1. Fetch posts from the specified subreddits
2. Show you a summary of fetched posts with their scores
3. Save the URLs to a file for reference
4. Upload them to NotebookLM after your confirmation

## Features

- Fetch top weekly posts from multiple subreddits
- Support for both link posts and text-only posts
- Automatically filter out promoted content
- Sort posts by score
- Filter posts by minimum score threshold
- Customizable number of posts per subreddit
- NotebookLM integration for automated source management
- Robust error handling and logging
- Type-safe implementation with full test coverage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reddit-weekly-top.git
cd reddit-weekly-top
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package and development dependencies:
```bash
pip install -e ".[dev]"
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

## Command Line Options

Available options:

Reddit Options:
- `-s, --subreddits`: List of subreddits to fetch posts from (required)
- `-t, --timeframe`: Time window for top posts ("week" or "month", default: "week")
- `-l, --limit`: Number of posts to fetch per subreddit (default: 10)
- `--min-score`: Minimum score threshold for posts (default: 0)

NotebookLM Options:
- `--profile-dir`: Chrome user profile directory
- `--upload-delay`: Delay between URL uploads in seconds (default: 2.0)
- `--max-retries`: Maximum number of upload retries (default: 3)
- `--retry-delay`: Delay between retries in seconds (default: 5.0)
- `--wait-timeout`: Timeout for browser operations in seconds (default: 10)

## Environment Variables

The following environment variables can be set in your `.env` file:

```bash
# Reddit settings
REDDIT_USER_AGENT=your-user-agent

# NotebookLM settings
CHROME_USER_PROFILE=/path/to/chrome/profile
```

## Development

### Running Tests

To run the test suite:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=reddit_weekly_top
```

### Code Style

This project uses Ruff for code formatting and linting. To check your code:

```bash
ruff check .
```

### Type Checking

To run type checking:

```bash
mypy src tests
```

## Prerequisites

- Chrome browser installed
- Chrome WebDriver (automatically managed)
- Python 3.9 or higher
- Required packages (installed via pip)

## Security Notes

- Store sensitive credentials in environment variables or secure credential storage
- Use Chrome profiles to maintain secure sessions
- Never commit credentials to version control
- Consider using a dedicated browser profile for automation

## License

This project is licensed under the MIT License - see the LICENSE file for details. 