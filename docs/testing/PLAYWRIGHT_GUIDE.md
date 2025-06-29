# Playwright Testing Guide

This guide provides instructions and best practices for writing and running Playwright tests in the InsightHub project.

## Running Tests

-   **Run all E2E tests:**
    ```bash
    npm run test:e2e
    ```

-   **Run tests in UI mode:**
    ```bash
    npm run test:e2e:ui
    ```

-   **Run accessibility tests:**
    ```bash
    npm run test:a11y
    ```

## Writing Tests

-   Place new test files in the `insighthub-frontend/tests` directory.
-   Use descriptive file names (e.g., `authentication.spec.ts`).
-   Follow the Page Object Model pattern where appropriate to keep tests clean and maintainable.
-   Use the `@playwright/test` library for assertions and test structure.
