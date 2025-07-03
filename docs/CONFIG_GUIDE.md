# InsightHub Configuration Guide

This document provides an overview of the key configuration files used in the InsightHub project for both the backend and frontend.

## Backend Configuration

### `pyproject.toml`

This is the main configuration file for the Python backend, managed by Poetry.

-   **`[tool.poetry.dependencies]`**: Lists the main Python packages required for the application to run, such as `langchain`, `supabase`, `praw`, and `yt-dlp`.
-   **`[tool.poetry.group.dev.dependencies]`**: Lists development-specific packages like `pytest`, `ruff`, and `mypy`.
-   **`[tool.ruff]`**: Configures the Ruff linter, enforcing code style and quality rules (e.g., line length, pydocstyle conventions).
-   **`[tool.mypy]`**: Configures the MyPy type checker to ensure type safety across the Python codebase.

### `pytest.ini`

This file configures the Pytest testing framework.

-   **`addopts`**: Specifies command-line options for running tests, such as `-q` for quiet mode.
-   **`norecursedirs`**: Prevents Pytest from searching for tests in specified directories like `worktrees` and `.git`.

## Frontend Configuration (`insighthub-frontend/`)

### `playwright.config.ts`

This file configures the Playwright end-to-end testing framework.

-   **`testDir`**: Specifies the directory containing E2E tests (`./tests`).
-   **`fullyParallel`**: Enables parallel test execution.
-   **`projects`**: Defines the browsers and devices to test against (Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari).
-   **`webServer`**: Configures the command to start the development server before running tests.

### `vitest.config.js`

This file configures the Vitest unit testing framework for Svelte components.

-   **`test.include`**: Defines the pattern for locating test files.
-   **`test.environment`**: Sets the testing environment (e.g., `happy-dom` to simulate a browser).
-   **`test.setupFiles`**: Specifies setup files to run before tests.
-   **`test.coverage`**: Configures code coverage reporting, including reporters and thresholds.

### `.quality-gate.json`

This file defines the specific metrics and thresholds for the project's quality gate, which is checked during CI/CD.

-   **`conditions`**: Sets thresholds for test coverage, code duplication, and maintainability ratings from SonarQube.
-   **`accessibility`**: Defines the maximum allowed number of accessibility violations by severity.
-   **`performance`**: Sets limits for bundle size and Core Web Vitals (LCP, FID, CLS).

### `lighthouserc.json`

This file configures Lighthouse CI for automated performance and quality audits.

-   **`ci.collect.url`**: Lists the URLs to be audited.
-   **`ci.collect.settings`**: Defines the Lighthouse preset (e.g., `desktop` or `mobile`).
-   **`ci.assert.assertions`**: Sets the minimum scores and maximum numeric values for various performance, accessibility, and SEO metrics. This is where performance budgets are strictly enforced.
-   **`mobile`**: A separate profile with slightly more lenient performance budgets for mobile devices.
