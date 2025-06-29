# Getting Started with InsightHub Development

This guide will walk you through setting up the complete development environment for InsightHub, including both the backend and frontend.

## Prerequisites

- Python 3.13 and Poetry
- Node.js 18+ and npm
- Git

## Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd insight_hub
    ```

2.  **Install Python dependencies:**
    ```bash
    poetry install
    ```

3.  **Set up environment variables:**
    
    You will need to set the `YOUTUBE_API` environment variable. You can do this by creating a `.env` file in the root of the project and adding the following line:
    
    ```
    YOUTUBE_API=your_youtube_api_key
    ```

4.  **Run the backend server:**
    ```bash
    poetry run streamlit run src/reddit_weekly_top/app.py
    ```

## Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd insighthub-frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```

You should now have the backend running on `http://localhost:8601` and the frontend on `http://localhost:5173`.
