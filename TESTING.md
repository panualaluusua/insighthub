# Testing Guide

This document outlines the testing strategy and guidelines for the InsightHub frontend application.

## Testing Stack

### Unit Testing
- **Vitest**: Modern testing framework with native ESM support
- **@testing-library/svelte**: Testing utilities for Svelte components
- **@testing-library/jest-dom**: Custom Jest matchers for DOM assertions
- **@testing-library/user-event**: User interaction simulation

### End-to-End Testing
- **Playwright**: Cross-browser testing framework
- **@axe-core/playwright**: Accessibility testing integration

### Accessibility Testing
- **axe-core**: Automated accessibility testing
- **Manual testing**: Keyboard navigation and screen reader testing

## Test Structure

```
src/
├── lib/
│   └── components/
│       ├── base/
│       │   ├── Button.test.ts
│       │   ├── Input.test.ts
│       │   └── Card.test.ts
│       ├── auth/
│       │   ├── LoginForm.test.ts
│       │   └── SignUpForm.test.ts
│       └── content/
│           ├── ContentCard.test.ts
│           ├── ContentFeed.test.ts
│           └── ContentFilters.test.ts
└── test-setup.js

tests/
├── auth.spec.ts
├── navigation.spec.ts
├── content-feed.spec.ts
└── accessibility.spec.ts
```

## Running Tests

### Unit Tests
```bash
# Run all unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests in UI mode
npm run test:ui
```

### End-to-End Tests
```bash
# Run all E2E tests
npm run test:e2e

# Run E2E tests in headed mode
npm run test:e2e:headed

# Run E2E tests for specific browser
npm run test:e2e -- --project=chromium
```

### Accessibility Tests
```bash
# Run accessibility tests
npm run test:a11y

# Run accessibility audit
npm run audit:a11y
```

## Writing Tests

### Unit Test Guidelines

#### Component Testing
```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import Component from './Component.svelte';

describe('Component', () => {
  it('renders correctly', () => {
    render(Component, { props: { title: 'Test' } });
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('handles user interactions', async () => {
    const handleClick = vi.fn();
    render(Component, { props: { onClick: handleClick } });
    
    await fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```

#### What to Test
- **Rendering**: Component renders with correct content and structure
- **Props**: Component responds correctly to different prop values
- **User Interactions**: Click, input, keyboard navigation work as expected
- **State Changes**: Component updates correctly when state changes
- **Accessibility**: Proper ARIA attributes, keyboard navigation, focus management
- **Error Handling**: Component handles errors gracefully

#### What NOT to Test
- Implementation details (internal state, private methods)
- Third-party library behavior
- Styling (unless it affects functionality)
- Browser-specific behavior (covered by E2E tests)

### End-to-End Test Guidelines

#### Page Testing
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/feature');
  });

  test('should work correctly', async ({ page }) => {
    await page.click('button');
    await expect(page.locator('text=Success')).toBeVisible();
  });
});
```

#### What to Test
- **User Workflows**: Complete user journeys from start to finish
- **Cross-Browser Compatibility**: Ensure features work across browsers
- **Responsive Design**: Test on different viewport sizes
- **Performance**: Page load times, interaction responsiveness
- **Accessibility**: Full accessibility audit with axe-core

### Accessibility Testing

#### Automated Testing
```typescript
import AxeBuilder from '@axe-core/playwright';

test('should be accessible', async ({ page }) => {
  await page.goto('/page');
  
  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

#### Manual Testing Checklist
- [ ] Keyboard navigation works for all interactive elements
- [ ] Focus indicators are visible and clear
- [ ] Screen reader announcements are appropriate
- [ ] Color contrast meets WCAG AA standards
- [ ] Images have appropriate alt text
- [ ] Forms have proper labels and error messages
- [ ] Headings follow logical hierarchy

## Coverage Requirements

### Unit Tests
- **Statements**: 80% minimum
- **Branches**: 80% minimum
- **Functions**: 80% minimum
- **Lines**: 80% minimum

### Critical Components
The following components require 100% coverage:
- Authentication components (LoginForm, SignUpForm)
- Base components (Button, Input, Card)
- Navigation components (MainNavigation, Sidebar)

## Test Data

### Mock Data
Use consistent mock data across tests:

```typescript
const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User'
};

const mockContent = {
  id: '1',
  title: 'Test Article',
  summary: 'Test summary',
  source: 'Test Source',
  url: 'https://example.com'
};
```

### Test Environment
- Use `test-setup.js` for global test configuration
- Mock external dependencies (APIs, browser APIs)
- Use fake timers for time-dependent tests
- Clean up after each test

## Continuous Integration

### GitHub Actions
Tests run automatically on:
- Pull requests
- Pushes to main branch
- Nightly builds

### Quality Gates
- All tests must pass
- Coverage thresholds must be met
- No accessibility violations
- No TypeScript errors
- No linting errors

## Best Practices

### General
1. **Write tests first** (TDD approach when possible)
2. **Keep tests simple** and focused on one behavior
3. **Use descriptive test names** that explain what is being tested
4. **Arrange, Act, Assert** pattern for test structure
5. **Mock external dependencies** to isolate component behavior

### Performance
1. **Use `beforeEach`** for common setup
2. **Clean up** after tests to prevent memory leaks
3. **Use `screen.getByRole`** over `querySelector` for better performance
4. **Batch assertions** when testing multiple related behaviors

### Maintainability
1. **Extract common test utilities** into helper functions
2. **Use page object model** for E2E tests
3. **Keep test data** in separate files
4. **Document complex test scenarios**
5. **Review tests** during code reviews

## Debugging Tests

### Unit Tests
```bash
# Debug specific test
npm run test -- --reporter=verbose Component.test.ts

# Debug with browser
npm run test:ui
```

### E2E Tests
```bash
# Debug with browser open
npm run test:e2e:headed

# Debug specific test
npx playwright test auth.spec.ts --debug

# Generate test report
npx playwright show-report
```

### Common Issues
1. **Timing issues**: Use `waitFor` for async operations
2. **Mock problems**: Ensure mocks are properly reset
3. **DOM queries**: Use semantic queries from Testing Library
4. **Accessibility**: Check for proper ARIA attributes and roles

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library Docs](https://testing-library.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Axe Accessibility Rules](https://dequeuniversity.com/rules/axe/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) 