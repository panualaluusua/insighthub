# Frontend Testing Guide

This guide covers the comprehensive testing infrastructure for the InsightHub frontend, including unit testing, integration testing, accessibility testing, performance monitoring, and visual regression testing.

## Table of Contents

1. [Testing Stack Overview](#testing-stack-overview)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [End-to-End Testing](#end-to-end-testing)
5. [Accessibility Testing](#accessibility-testing)
6. [Performance Testing](#performance-testing)
7. [Visual Regression Testing](#visual-regression-testing)
8. [Test Commands](#test-commands)
9. [Writing Tests](#writing-tests)
10. [Best Practices](#best-practices)
11. [CI/CD Integration](#cicd-integration)

## Testing Stack Overview

Our frontend uses a multi-layered testing approach:

- **Unit Testing**: Vitest + Testing Library for component testing
- **E2E Testing**: Playwright for cross-browser end-to-end testing
- **Performance**: Lighthouse CI + Custom performance monitoring
- **Visual Regression**: Playwright screenshot testing
- **Accessibility**: axe-core integration with Playwright
- **Type Safety**: TypeScript for compile-time error detection

## Unit Testing

### Framework: Vitest + Testing Library

Unit tests are located in `src/lib/components/*.test.ts` files alongside components.

#### Test Setup

The test environment includes:
- **DOM Environment**: JSDOM for browser API simulation
- **Mocks**: Pre-configured mocks for IntersectionObserver, ResizeObserver, matchMedia
- **Providers**: Mock Supabase client and store contexts
- **Accessibility**: Built-in axe-core integration

```typescript
// Example component test
import { describe, it, expect } from 'vitest';
import { renderWithProviders, userEvent } from '../test-utils/render';
import Button from './Button.svelte';

describe('Button Component', () => {
  it('renders with required props', () => {
    const component = renderWithProviders(Button, {
      props: {
        label: 'Test Button',
        onClick: () => {}
      }
    });

    expect(component.getByRole('button')).toBeInTheDocument();
    expect(component.getByText('Test Button')).toBeInTheDocument();
  });
});
```

#### Test Utilities

**`src/lib/test-utils/render.ts`** provides:
- `renderWithProviders()`: Renders components with mock contexts
- `mockSupabaseClient`: Pre-configured Supabase mock
- `getAccessibilityViolations()`: Accessibility testing helper
- `measureRenderTime()`: Performance testing helper

## Integration Testing

Integration tests verify component interactions and data flow. These tests use the same Vitest setup but focus on multiple components working together.

```typescript
// Example integration test
test('form submission flow', async () => {
  const user = userEvent.setup();
  const mockSubmit = vi.fn();
  
  const component = renderWithProviders(SignUpForm, {
    props: { onSubmit: mockSubmit }
  });

  await user.type(component.getByLabelText('Email'), 'test@example.com');
  await user.type(component.getByLabelText('Password'), 'password123');
  await user.click(component.getByRole('button', { name: 'Sign Up' }));

  expect(mockSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123'
  });
});
```

## End-to-End Testing

### Framework: Playwright

E2E tests are in the `tests/` directory and cover complete user workflows.

#### Configuration

**`playwright.config.ts`** includes:
- Cross-browser testing (Chromium, Firefox, WebKit)
- Mobile viewport testing
- CI/CD optimizations
- Accessibility testing integration

```typescript
// Example E2E test
import { test, expect } from '@playwright/test';

test('user authentication flow', async ({ page }) => {
  await page.goto('/signin');
  
  await page.fill('[data-testid="email-input"]', 'test@example.com');
  await page.fill('[data-testid="password-input"]', 'password123');
  await page.click('[data-testid="signin-button"]');
  
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByText('Welcome')).toBeVisible();
});
```

#### Key Test Files

- `accessibility.spec.ts`: Accessibility compliance testing
- `auth.spec.ts`: Authentication workflows
- `navigation.spec.ts`: Navigation and routing
- `visual-regression.spec.ts`: Visual consistency testing
- `performance-monitoring.spec.ts`: Performance metrics validation

## Accessibility Testing

### Automated Accessibility Testing

Every page and component is tested for WCAG compliance using axe-core:

```typescript
test('homepage accessibility', async ({ page }) => {
  await page.goto('/');
  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

### Manual Accessibility Testing Checklist

- [ ] Keyboard navigation works for all interactive elements
- [ ] Screen reader announcements are appropriate
- [ ] Color contrast meets WCAG AA standards
- [ ] Focus indicators are visible and clear
- [ ] Form labels are properly associated
- [ ] Error messages are accessible

## Performance Testing

### Lighthouse CI Integration

**`lighthouserc.json`** defines performance budgets:

```json
{
  "assertions": {
    "categories:performance": ["error", {"minScore": 0.9}],
    "first-contentful-paint": ["error", {"maxNumericValue": 1800}],
    "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
    "first-input-delay": ["error", {"maxNumericValue": 100}],
    "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}]
  }
}
```

### Core Web Vitals Monitoring

**`tests/performance-monitoring.spec.ts`** provides comprehensive performance tracking:

#### Core Web Vitals Measurement
- **First Contentful Paint (FCP)**: < 1.8s (homepage), < 2.0s (dashboard)
- **Largest Contentful Paint (LCP)**: < 2.5s using Performance Observer API
- **First Input Delay (FID)**: < 100ms with real user interaction timing
- **Cumulative Layout Shift (CLS)**: < 0.1 with automatic layout shift detection
- **Time to First Byte (TTFB)**: < 600ms (homepage), < 800ms (dashboard)
- **Time to Interactive (TTI)**: Measured via Navigation Timing API

#### Advanced Performance Analysis
- **Bundle Size Analysis**: Real-time network interception tracking JavaScript (< 500KB), CSS (< 100KB), fonts (< 100KB)
- **Resource Count Monitoring**: Script files (< 20), stylesheets (< 5), images, fonts
- **Memory Usage Tracking**: JavaScript heap size monitoring with 50MB limit and 80% usage threshold
- **Interactive Performance Testing**: Button click responsiveness and UI interaction timing
- **Network Performance Analysis**: Request timing, response analysis, and resource loading metrics

```typescript
// Example: Memory monitoring implementation
const memoryInfo = await page.evaluate(() => {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    return {
      usedJSHeapSize: memory.usedJSHeapSize,
      totalJSHeapSize: memory.totalJSHeapSize,
      jsHeapSizeLimit: memory.jsHeapSizeLimit
    };
  }
  return null;
});
```

### Enhanced Lighthouse CI Configuration

**`lighthouserc.json`** defines comprehensive performance budgets with dual desktop/mobile configurations:

#### Desktop Performance Budgets
```json
{
  "categories:performance": ["error", {"minScore": 0.9}],
  "first-contentful-paint": ["error", {"maxNumericValue": 1800}],
  "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
  "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
  "total-blocking-time": ["error", {"maxNumericValue": 200}],
  "speed-index": ["error", {"maxNumericValue": 2500}],
  "interactive": ["error", {"maxNumericValue": 2800}]
}
```

#### Mobile Performance Budgets (More Lenient)
- Performance Score: ≥ 85% (vs 90% desktop)
- FCP: < 2.2s (vs 1.8s desktop)
- LCP: < 3.0s (vs 2.5s desktop)
- TBT: < 350ms (vs 200ms desktop)

#### Resource Budgets Enforcement
- **Scripts**: 500KB max, 20 files max
- **Stylesheets**: 100KB max, 5 files max
- **Images**: 1MB max, 20 files max  
- **Fonts**: 150KB max, 5 files max
- **Documents**: 100KB max

### Bundle Size Analysis

Automated tracking of:
- JavaScript bundle size: < 500KB
- CSS bundle size: < 100KB
- Font files: < 150KB
- Image files: < 1MB
- Script count: < 20 files
- Network request analysis with response timing

## Visual Regression Testing

### Comprehensive Screenshot Testing with Playwright

**`tests/visual-regression.spec.ts`** provides enterprise-grade visual consistency testing:

#### Full Page Coverage
- **Complete Route Testing**: Homepage, dashboard, feed, signin, signup, theme pages
- **Full Page Screenshots**: Captures entire page with disabled animations for consistency
- **Viewport Screenshots**: Above-the-fold content testing for faster feedback

#### Advanced Responsive Design Testing
Tests across **5 different viewport sizes**:
- **Mobile**: 375×667 (iPhone SE)
- **Tablet**: 768×1024 (iPad Portrait)  
- **Tablet Landscape**: 1024×768 (iPad Landscape)
- **Desktop**: 1440×900 (Standard Desktop)
- **Desktop Large**: 1920×1080 (Large Desktop)

```typescript
// Example: Multi-viewport responsive testing
const viewports = [
  { width: 375, height: 667, name: 'mobile' },
  { width: 768, height: 1024, name: 'tablet' },
  { width: 1024, height: 768, name: 'tablet-landscape' },
  { width: 1440, height: 900, name: 'desktop' },
  { width: 1920, height: 1080, name: 'desktop-large' }
];
```

#### Navigation Component Testing
- **Desktop Navigation**: Full navigation component screenshots
- **Mobile Navigation**: Mobile nav trigger and expanded menu testing
- **Navigation States**: Open/closed states with transition handling

#### Form State Comprehensive Testing
- **Empty Form State**: Baseline form appearance
- **Focus States**: Individual input field focus indicators
- **Filled States**: Forms with entered data
- **Validation Error States**: Error messages and invalid field styling
- **Loading States**: Form submission and processing states

#### Theme Consistency Validation
- **Default Theme**: Baseline theme appearance
- **Theme Toggle Testing**: Light/dark mode transitions
- **Theme Persistence**: Visual consistency after theme changes

#### Loading and Error State Capture
- **Loading States**: Network request delays simulated to capture loading UI
- **Error States**: Form validation errors and API error states
- **Timeout Handling**: Controlled delays for stable screenshot capture

### Screenshot Management Best Practices

- **Baseline Creation**: Initial screenshots generated on first test run
- **Automatic Updates**: Use `npm run test:visual:update` to update baselines
- **Diff Analysis**: Failed tests generate visual diffs in `test-results/`
- **Animation Disable**: All screenshots taken with `animations: 'disabled'`
- **Network Stability**: `waitForLoadState('networkidle')` ensures stable captures

### Test Commands Enhancement

```bash
# Visual regression specific commands
npm run test:visual            # Run visual regression tests
npm run test:visual:update     # Update visual baselines
npm run test:visual:headed     # Run with browser UI for debugging
npm run test:visual:mobile     # Run mobile-specific visual tests
npm run test:visual:desktop    # Run desktop-specific visual tests
```

```typescript
test('responsive homepage design', async ({ page }) => {
  const viewports = [
    { width: 375, height: 667, name: 'mobile' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 1440, height: 900, name: 'desktop' }
  ];

  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto('/');
    await expect(page).toHaveScreenshot(`homepage-${viewport.name}.png`);
  }
});
```

## Test Commands

```bash
# Unit tests
npm run test                    # Run unit tests
npm run test:watch             # Run tests in watch mode
npm run test:coverage          # Generate coverage report
npm run test:ui                # Open Vitest UI

# E2E tests
npm run test:e2e               # Run all E2E tests
npm run test:e2e:headed        # Run with browser UI
npm run test:e2e:debug         # Run with debugger

# Specific test types
npm run test:accessibility     # Run accessibility tests only
npm run test:visual            # Run visual regression tests
npm run test:performance       # Run performance tests

# Lighthouse CI
npm run lighthouse             # Run Lighthouse audits
npm run lighthouse:ci          # Run in CI mode

# Test management
npm run test:install           # Install Playwright browsers
npm run test:report            # Open test report
npm run test:clean             # Clean test artifacts
```

## Writing Tests

### Component Test Template

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { renderWithProviders, userEvent, getAccessibilityViolations } from '../test-utils/render';
import ComponentName from './ComponentName.svelte';

describe('ComponentName', () => {
  describe('Basic Rendering', () => {
    it('renders with required props', () => {
      const component = renderWithProviders(ComponentName, {
        props: { /* required props */ }
      });
      
      expect(component.getByRole('...')).toBeInTheDocument();
    });

    it('takes a snapshot', () => {
      const component = renderWithProviders(ComponentName, {
        props: { /* props */ }
      });
      
      expect(component.container.firstChild).toMatchSnapshot();
    });
  });

  describe('Interactions', () => {
    it('handles user interactions', async () => {
      const user = userEvent.setup();
      const mockHandler = vi.fn();
      
      const component = renderWithProviders(ComponentName, {
        props: { onClick: mockHandler }
      });

      await user.click(component.getByRole('button'));
      expect(mockHandler).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has no accessibility violations', async () => {
      const component = renderWithProviders(ComponentName, {
        props: { /* props */ }
      });

      const violations = await getAccessibilityViolations(component.container);
      expect(violations).toHaveLength(0);
    });
  });
});
```

### E2E Test Template

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup common to all tests
    await page.goto('/');
  });

  test('should perform main user flow', async ({ page }) => {
    // Arrange
    await page.waitForLoadState('networkidle');

    // Act
    await page.click('[data-testid="action-button"]');
    await page.fill('[data-testid="input-field"]', 'test value');

    // Assert
    await expect(page.getByText('Expected result')).toBeVisible();
  });

  test('should handle error states', async ({ page }) => {
    // Test error handling
  });
});
```

## Best Practices

### Test Organization

1. **Arrange, Act, Assert**: Structure tests clearly
2. **Descriptive Names**: Use descriptive test and describe block names
3. **Single Responsibility**: One assertion per test when possible
4. **Test Independence**: Tests should not depend on each other

### Performance Testing

1. **Realistic Conditions**: Test under realistic network and device conditions
2. **Multiple Runs**: Use average of multiple runs for performance metrics
3. **Regression Prevention**: Monitor performance trends over time
4. **Budget Enforcement**: Fail builds that exceed performance budgets

### Accessibility Testing

1. **Automated + Manual**: Combine automated tools with manual testing
2. **Real Devices**: Test with actual assistive technologies when possible
3. **Multiple Impairments**: Consider various disability types
4. **Progressive Enhancement**: Test with JavaScript disabled

### Visual Testing

1. **Consistent Environment**: Use consistent viewport sizes and themes
2. **Stable Content**: Avoid time-dependent or random content in screenshots
3. **Critical Paths**: Focus on user-critical visual elements
4. **Cross-Browser**: Test visual consistency across browsers

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Frontend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:coverage
      
      - name: Install Playwright
        run: npx playwright install
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Run Lighthouse CI
        run: npm run lighthouse:ci
      
      - name: Upload test artifacts
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: test-results
          path: |
            test-results/
            playwright-report/
            coverage/
```

### Quality Gates

Tests must pass these criteria:

- **Unit Test Coverage**: > 80%
- **E2E Test Pass Rate**: 100%
- **Accessibility Violations**: 0
- **Performance Score**: > 90
- **Visual Regression**: No unexpected changes

### Monitoring

- **Performance Trends**: Track Core Web Vitals over time
- **Test Reliability**: Monitor flaky test rates
- **Coverage Trends**: Ensure coverage doesn't decrease
- **Bundle Size**: Alert on significant size increases

## Troubleshooting

### Common Issues

**Tests timing out**:
- Increase timeout in playwright.config.ts
- Add proper wait conditions
- Check for infinite loops or blocking operations

**Visual regression failures**:
- Review screenshot diffs in test-results/
- Update baselines if changes are intentional
- Check for non-deterministic content

**Performance test failures**:
- Check for resource loading issues
- Verify network conditions
- Review bundle size changes

**Accessibility violations**:
- Review specific axe-core violations
- Check color contrast ratios
- Verify ARIA labels and roles

### Debug Commands

```bash
# Debug specific test
npm run test:e2e -- --debug --grep "test name"

# Run with browser UI
npm run test:e2e:headed

# Generate trace for debugging
npm run test:e2e -- --trace on

# Update visual baselines
npm run test:visual:update
```

---

This testing infrastructure ensures high-quality, accessible, and performant frontend code. For questions or improvements, please refer to the team's testing standards documentation. 