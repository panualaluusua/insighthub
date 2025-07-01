# InsightHub: Reddit & YouTube Aggregator v1.0.1

A Streamlit-based web application that aggregates content from Reddit and YouTube, making it easy to discover and organize interesting content from your favorite subreddits and YouTube channels.

## Quick Start

1. Install Poetry if you haven't already:
```bash
pip install poetry
```

2. Install the required dependencies (Poetry will create and manage a virtual environment for you):
```bash
poetry install
```

3. Activate the Poetry shell:
```bash
poetry shell
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your YouTube API key:
YOUTUBE_API=your_youtube_api_key
```

5. Run the Streamlit app:
```bash
poetry run streamlit run src/reddit_weekly_top/app.py
```

## Features

- Aggregate content from multiple Reddit subreddits
- Fetch latest videos from YouTube channels
- Organize content by categories
- Generate podcast prompts for NotebookLM
- Copy URLs for easy sharing
- Modern, user-friendly interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/insight-hub.git
cd insight-hub
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

## Environment Variables

Set up your environment variables in a `.env` file:

```bash
# YouTube API key (required for YouTube functionality)
YOUTUBE_API=your_youtube_api_key

# Reddit settings
REDDIT_USER_AGENT=InsightHub/1.0
```

## Development

### Running in Development

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

To run the test suite:
```bash
pytest
```

To run tests with coverage:
```bash
pytest --cov=reddit_weekly_top
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

## Git Worktree Workflows

This project utilizes Git worktrees to facilitate parallel development and isolated environments. We have two primary worktree workflows:

### UI Development Worktree Workflow

To isolate UI development, we use a dedicated Git worktree at `../ui-dev` on the `ui-development` branch. Scripts are provided in `scripts/` for convenience.

#### Setup (run from project root):

**With Git Bash:**
```sh
bash scripts/create_worktree.sh
```

**With PowerShell:**
```powershell
./scripts/create_worktree.ps1
```

This will create a new worktree at `../ui-dev` checked out to the `ui-development` branch.

#### Switching to the worktree:
- **Bash:** `bash scripts/switch_worktree.sh`
- **PowerShell:** `./scripts/switch_worktree.ps1`

#### Updating the worktree:
- **Bash:** `bash scripts/update_worktree.sh`
- **PowerShell:** `./scripts/update_worktree.ps1`

#### Notes
- The `ui-dev/` directory is ignored by git via `.gitignore`.
- Use the worktree for all major UI development and experiments.
- Merge changes back to main via pull requests as usual.

### Dual-Agent Workflow

For general-purpose parallel development, such as running a secondary AI agent (like Gemini CLI for documentation) or working on a separate feature/bugfix without affecting your primary development environment, we use a more generic dual-agent worktree workflow.

This workflow allows you to create worktrees for any branch in a dedicated parent directory, preventing context switching and keeping tasks isolated.

For a detailed guide on setting up and using the Dual-Agent Workflow, including best practices and step-by-step instructions, please refer to:

- [`.cursor/rules/dual-agent-workflow.mdc`](.cursor/rules/dual-agent-workflow.mdc)

This is a test line for the PowerShell Aider audit workflow.