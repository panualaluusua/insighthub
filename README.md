# Reddit Weekly Top

A Python tool to fetch the top weekly posts from selected subreddits. This tool returns both link posts and text-only posts from the most popular content in your selected subreddits.

## Quick Start

After installation, fetch Reddit posts with a single command:
# Example sub reddits: ChatGPTCoding, Cursor, etc.
```bash
# Fetch top weekly posts from specific subreddits
python -m reddit_weekly_top.scripts.fetch_posts -s python programming

# Fetch monthly top posts instead of weekly
python -m reddit_weekly_top.scripts.fetch_posts -s dataengineering -l 25 -t month

# Only include posts with high scores
python -m reddit_weekly_top.scripts.fetch_posts -s python --min-score 100

# Customize number of posts per subreddit
python -m reddit_weekly_top.scripts.fetch_posts -s python -l 5
```

The script will:
1. Fetch posts from the specified subreddits
2. Show you a summary of fetched posts with their scores
3. Save the URLs to a file for reference

## Features

- Fetch top posts (weekly or monthly) from multiple subreddits
- Filter posts by minimum score
- Customize the number of posts fetched per subreddit
- Save fetched URLs to a timestamped file

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

Use `python -m reddit_weekly_top.scripts.fetch_posts --help` to see all options:

- `-s`, `--subreddits`: List of subreddits (required)
- `-t`, `--timeframe`: Time window ('week' or 'month', default: 'week')
- `-l`, `--limit`: Max posts per subreddit (default: 10)
- `--min-score`: Minimum post score (default: 0)

## Environment Variables

The following environment variables can be set in your `.env` file:

```bash
# Reddit settings
REDDIT_USER_AGENT=your-user-agent
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

- Python 3.9 or higher
- Required packages (installed via pip)

## Security Notes

- Store sensitive Reddit credentials (if applicable) securely.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.