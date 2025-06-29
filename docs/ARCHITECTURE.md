# InsightHub Architecture

This document provides a high-level overview of the InsightHub system architecture.

## Core Components

InsightHub is comprised of two main components:

1.  **Backend:** A Python-based application responsible for:
    *   Fetching data from external sources (Reddit, YouTube).
    *   Processing and enriching data using AI/ML models (LangChain).
    *   Providing a Streamlit web interface.
    *   Managing data persistence.

2.  **Frontend:** A SvelteKit single-page application (SPA) that provides the user interface for:
    *   Configuring data sources.
    *   Displaying aggregated content.
    *   Interacting with the AI-powered features.

## Data Flow

1.  The **Frontend** makes requests to the **Backend** API.
2.  The **Backend** fetches data from external APIs (Reddit, YouTube).
3.  This data is then processed by the AI pipeline for summarization, scoring, and personalization.
4.  The processed data is returned to the **Frontend** for display.
