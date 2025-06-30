# Testing Strategy

This document defines the comprehensive testing strategy for the InsightHub project.

## Levels of Testing

1.  **Unit Tests:**
    -   **Backend:** Pytest is used for unit testing individual functions and classes in the Python backend.
    -   **Frontend:** Vitest is used for unit testing Svelte components and utility functions.

2.  **Integration Tests:**
    -   These tests verify the interaction between different parts of the system, such as the frontend and backend API.

3.  **End-to-End (E2E) Tests:**
    -   Playwright is used for E2E testing to simulate real user scenarios in a browser.
    -   This includes tests for user authentication, core application workflows, and accessibility.

4.  **Performance & Visual Regression Testing:**
    -   **Core Web Vitals Monitoring:** Comprehensive tracking of FCP, LCP, FID, CLS, and TTFB across all routes
    -   **Bundle Size Analysis:** Real-time network interception with budget enforcement (JS < 500KB, CSS < 100KB)
    -   **Memory Usage Tracking:** JavaScript heap monitoring with 50MB limits and 80% usage thresholds
    -   **Visual Regression Testing:** Enterprise-grade screenshot testing across 5 viewports with form state testing
    -   **Lighthouse CI Integration:** Dual desktop/mobile performance budgets with resource enforcement
    -   **See:** [Performance & Visual Testing Documentation](../frontend/PERFORMANCE_VISUAL_TESTING.md)

5.  **AI-Assisted Testing:**
    -   We leverage AI tools for visual regression testing and bug detection, as configured in our Playwright setup.

## Quality Gates

### Performance Thresholds
- **Desktop Performance Score:** ≥ 90%
- **Mobile Performance Score:** ≥ 85%
- **First Contentful Paint:** < 1.8s (homepage), < 2.0s (dashboard)
- **Largest Contentful Paint:** < 2.5s (desktop), < 3.0s (mobile)
- **Cumulative Layout Shift:** < 0.1
- **Bundle Sizes:** JS < 500KB, CSS < 100KB, Fonts < 150KB

### Visual Consistency
- **Cross-viewport testing:** 5 different screen sizes (mobile to desktop-large)
- **Form state validation:** Empty, focused, filled, error, and loading states
- **Theme consistency:** Light/dark mode transitions
- **Navigation testing:** Desktop and mobile navigation components

### Test Coverage Requirements
- **Unit Test Coverage:** ≥ 80% line coverage enforced
- **E2E Test Coverage:** All critical user journeys
- **Performance Coverage:** All main routes tested
- **Visual Coverage:** All pages across all supported viewports

## Documentation
- **Frontend Testing Guide:** [docs/frontend/TESTING_GUIDE.md](../frontend/TESTING_GUIDE.md)
- **Performance & Visual Testing:** [docs/frontend/PERFORMANCE_VISUAL_TESTING.md](../frontend/PERFORMANCE_VISUAL_TESTING.md)
- **Quality Assurance:** [docs/frontend/QUALITY_ASSURANCE.md](../frontend/QUALITY_ASSURANCE.md)
