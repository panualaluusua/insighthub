# Backend API Reference

This document details the API endpoints provided by the FastAPI backend.

*(This is a placeholder. As the API is developed, this document should be updated with details on each endpoint, including request/response formats and authentication requirements.)*

## Endpoints

### `/api/v1/reddit`

-   **GET:** Fetches top posts from Reddit.
    -   **Query Parameters:** `subreddits`, `timeframe`, `limit`
    -   **Returns:** A list of Reddit post objects.

### `/api/v1/youtube`

-   **GET:** Fetches latest videos from YouTube channels.
    -   **Query Parameters:** `channels`, `limit`
    -   **Returns:** A list of YouTube video objects.
