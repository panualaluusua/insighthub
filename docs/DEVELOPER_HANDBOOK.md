# InsightHub Developer Handbook

This handbook provides a comprehensive guide for developers working on the InsightHub project. It covers everything from setting up your development environment to understanding the project's architecture, configuration, testing strategies, and development workflows.

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Prerequisites](#2-prerequisites)
3.  [Backend Setup](#3-backend-setup)
4.  [Frontend Setup](#4-frontend-setup)
5.  [Configuration Guide](#5-configuration-guide)
6.  [Testing Strategy](#6-testing-strategy)
7.  [Development Workflow](#7-development-workflow)
8.  [Key Scripts](#8-key-scripts)

---

## 1. Introduction

Welcome to the InsightHub project! InsightHub is an intelligent content curation hub designed to help knowledge workers manage information overload. It leverages AI to fetch, analyze, and personalize news and content from various sources (Reddit, YouTube).

This handbook aims to be your primary resource for all development-related queries. If you find anything unclear or missing, please contribute to its improvement.

---

## 2. Prerequisites

Before you begin, ensure you have the following installed on your system:

-   **Python 3.13 and Poetry:** For managing Python dependencies and virtual environments.
-   **Node.js 18+ and npm:** For managing JavaScript dependencies and running frontend tools.
-   **Git:** For version control.

---

## 3. Backend Setup

Follow these steps to set up the Python backend:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace with actual repository URL
    cd insight_hub
    ```

2.  **Install Python dependencies:**
    ```bash
    poetry install
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root of the project and add the following lines. These keys are crucial for the AI functionalities.
    ```
    YOUTUBE_API=your_youtube_api_key
    OPENAI_API_KEY=your_openai_api_key
    TRANSCRIPTION_METHOD=openai # or 'local' for faster-whisper
    AUDIO_SPEED_FACTOR=2.0 # Optional: Factor to speed up audio for transcription
    ```

4.  **Run the backend server:**
    ```bash
    poetry run streamlit run src/reddit_weekly_top/app.py
    ```
    The backend server should now be running on `http://localhost:8601`.

---

## 4. Frontend Setup

Follow these steps to set up the SvelteKit frontend:

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
    The frontend development server should now be running on `http://localhost:5173`.

---

## 5. Configuration Guide

For a detailed understanding of the project's configuration files, please refer to the dedicated `CONFIG_GUIDE.md` document:

-   **[CONFIG_GUIDE.md](./CONFIG_GUIDE.md)**

This guide covers `pyproject.toml`, `pytest.ini`, `playwright.config.ts`, `vitest.config.js`, `.quality-gate.json`, and `lighthouserc.json`.

---

## 6. Testing Strategy

InsightHub employs a comprehensive testing strategy covering unit, integration, E2E, performance, and AI-powered testing. For detailed information on how to run tests and contribute to testing, please see:

-   **[TESTING.md](../TESTING.md)**

---

## 7. Development Workflow

Our development process follows a multi-agent Git worktree workflow, emphasizing isolated feature development and structured task management. Key principles include:

-   **Git Worktrees:** Always use Git worktrees for feature development to keep the main repository on the `master` branch clean.
-   **Taskmaster:** Utilize `task-master` for managing tasks, subtasks, and tracking progress.
-   **Automated Quality Audit:** Before marking a task complete, perform an automated audit using the Aider-powered auditor.
-   **Documentation-First:** All significant architectural changes and implementation patterns must be documented in the `docs/` folder.

For a complete overview of the development workflow, refer to:

-   **[GEMINI.md](../GEMINI.md)**

---

## 8. Key Scripts

The `scripts/` directory contains various utility scripts to streamline development tasks. Here's an overview of some important ones:

-   **`analyze-ai-test-results.cjs`**: Analyzes AI test results and generates reports.
-   **`create_worktree.ps1` / `create_worktree.sh`**: Automates the creation of new Git worktrees for isolated development.
-   **`quality-dashboard.js`**: Generates a quality dashboard from audit reports.
-   **`switch_worktree.ps1` / `switch_worktree.sh`**: Helps switch between existing Git worktrees.
-   **`tm-test-guard.ps1` / `tm-test-guard.sh`**: Ensures a Taskmaster task is in "in-progress" status before allowing a test run.
-   **`update_worktree.ps1` / `update_worktree.sh`**: Updates a Git worktree by pulling changes from the main branch.

To run a script, navigate to the project root and execute it (e.g., `.\scripts\create_worktree.ps1` on PowerShell or `./scripts/create_worktree.sh` on Bash).
