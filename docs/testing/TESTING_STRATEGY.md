# Testing Strategy

This document defines the testing strategy for the InsightHub project.

## Levels of Testing

1.  **Unit Tests:**
    -   **Backend:** Pytest is used for unit testing individual functions and classes in the Python backend.
    -   **Frontend:** Vitest is used for unit testing Svelte components and utility functions.

2.  **Integration Tests:**
    -   These tests verify the interaction between different parts of the system, such as the frontend and backend API.

3.  **End-to-End (E2E) Tests:**
    -   Playwright is used for E2E testing to simulate real user scenarios in a browser.
    -   This includes tests for user authentication, core application workflows, and accessibility.

4.  **AI-Assisted Testing:**
    -   We leverage AI tools for visual regression testing and bug detection, as configured in our Playwright setup.
