# Testing Guide

This document outlines the testing strategy and guidelines for the InsightHub frontend application, including our cutting-edge **AI-powered testing system**.

## Testing Stack

### Unit Testing
- **Vitest**: Modern testing framework with native ESM support
- **@testing-library/svelte**: Testing utilities for Svelte components
- **@testing-library/jest-dom**: Custom Jest matchers for DOM assertions
- **@testing-library/user-event**: User interaction simulation

### End-to-End Testing
- **Playwright**: Cross-browser testing framework
- **@axe-core/playwright**: Accessibility testing integration

### 🤖 AI-Powered Testing (Enhanced Playwright MCP)
- **Enhanced Playwright MCP**: AI-powered browser automation with vision capabilities
- **AI Visual Analysis**: Intelligent screenshot analysis and pattern recognition
- **AI Bug Detection**: Automated issue identification using AI insights
- **AI Accessibility Testing**: Smart WCAG compliance with AI recommendations
- **AI Performance Monitoring**: Core Web Vitals analysis with optimization suggestions

### Accessibility Testing
- **axe-core**: Automated accessibility testing
- **AI Accessibility Analysis**: Enhanced compliance testing with intelligent insights
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

### 🤖 AI-Powered Tests
```bash
# Run complete AI-powered visual analysis
npm run test:ai

# Run AI tests with browser UI for debugging
npm run test:ai:headed

# Run targeted AI bug detection
npm run test:bug-detection

# Generate comprehensive AI analysis report
npm run analyze:ai

# View detailed AI test reports and visual evidence
npx playwright show-report
```

### Cursor IDE AI Testing Integration
```bash
# 🎯 Comprehensive AI analysis command (use in Cursor)
@test-ai-analyze
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

## 🤖 AI-Powered Testing System

### Overview
Our Enhanced Playwright MCP Testing system provides cutting-edge AI-powered testing capabilities that go beyond traditional automated testing.

### AI Testing Capabilities

#### 1. 🧠 AI Visual Analysis
The AI system takes intelligent screenshots and analyzes visual patterns:

```typescript
// Example from ai-powered-visual.spec.ts
test('AI visual analysis of component states', async ({ page }) => {
  await page.goto('/component-playground');
  
  const variants = ['primary', 'secondary', 'outline'];
  
  for (const variant of variants) {
    await page.selectOption('[data-testid="variant-selector"]', variant);
    
    // AI captures and analyzes visual patterns
    await page.screenshot({ 
      path: `test-results/ai-analysis/component-${variant}.png`,
      fullPage: true 
    });
    
    // AI validates accessibility compliance
    const accessibilityResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    expect(accessibilityResults.violations).toEqual([]);
  }
});
```

#### 2. 🔍 AI Bug Detection
AI analyzes patterns to detect common issues:

```typescript
test('AI bug detection and form validation', async ({ page }) => {
  await page.goto('/signup');
  
  // AI tests form validation patterns
  const emailInput = page.locator('input[type="email"]');
  const submitButton = page.locator('button[type="submit"]');
  
  // Test invalid email with AI pattern recognition
  await emailInput.fill('invalid-email');
  await submitButton.click();
  
  // AI expects intelligent error messaging
  const errorMessage = page.locator('[data-testid="email-error"]');
  await expect(errorMessage).toBeVisible();
  await expect(errorMessage).toContainText(/valid email/i);
  
  // AI captures evidence for analysis
  await page.screenshot({ 
    path: 'test-results/ai-analysis/form-validation-error.png' 
  });
});
```

#### 3. 📱 AI Responsive Design Testing
AI validates responsive behavior across viewports:

```typescript
test('AI responsive design validation', async ({ page }) => {
  const viewports = [
    { width: 375, height: 667, name: 'mobile' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 1920, height: 1080, name: 'desktop' }
  ];
  
  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto('/');
    
    // AI analyzes responsive behavior
    await page.screenshot({ 
      path: `test-results/ai-analysis/responsive-${viewport.name}.png` 
    });
    
    // AI validates component remains functional
    const navigation = page.locator('[data-testid="navigation"]');
    await expect(navigation).toBeVisible();
  }
});
```

#### 4. ⚡ AI Performance Monitoring
AI analyzes Core Web Vitals and performance metrics:

```typescript
test('AI performance analysis', async ({ page }) => {
  await page.goto('/');
  
  // AI measures performance metrics
  const performanceMetrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const metrics = {};
        
        entries.forEach((entry) => {
          if (entry.entryType === 'largest-contentful-paint') {
            metrics.lcp = entry.startTime;
          }
          if (entry.entryType === 'first-input') {
            metrics.fid = entry.processingStart - entry.startTime;
          }
        });
        
        resolve(metrics);
      }).observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });
    });
  });
  
  // AI validates performance benchmarks
  if (performanceMetrics.lcp) {
    expect(performanceMetrics.lcp).toBeLessThan(2500); // AI recommends < 2.5s
  }
});
```

### AI Test Results and Analysis

#### Results Directory Structure
```
test-results/ai-analysis/
├── bug-detection-report.md       # 🤖 Comprehensive AI analysis
├── component-visual-*.png         # 📷 Visual evidence screenshots
├── responsive-*.png               # 📱 Responsive design validation
├── accessibility-report.json      # ♿ AI accessibility findings
├── performance-analysis.md        # ⚡ AI performance insights
└── form-validation-*.png          # 📝 Form interaction evidence
```

#### AI Analysis Script
The `analyze:ai` command runs a comprehensive analysis of all AI test results:

```bash
npm run analyze:ai
```

This script:
- 📊 Categorizes all AI test artifacts
- 🔍 Analyzes screenshots for patterns
- ♿ Reviews accessibility findings
- ⚡ Processes performance metrics
- 🐛 Identifies critical issues
- 💡 Provides AI-powered recommendations

### Integration with Development Workflow

#### During Component Development
1. **After implementing**: Run `@test-ai-analyze` in Cursor
2. **Visual validation**: Review AI screenshots for consistency
3. **Accessibility check**: Verify AI accessibility analysis passes
4. **Performance review**: Check AI performance recommendations

#### During Feature Development
1. **UI changes**: Run `npm run test:ai` for regression analysis
2. **Responsive work**: Use AI viewport validation
3. **Pre-deployment**: Execute complete AI testing suite

#### CI/CD Integration
```yaml
# .github/workflows/ai-testing.yml
name: AI-Powered Testing
on: [push, pull_request]

jobs:
  ai-testing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright browsers
        run: npx playwright install
      
      - name: Run AI-powered tests
        run: npm run test:ai
      
      - name: Upload AI test results
        uses: actions/upload-artifact@v3
        with:
          name: ai-test-results
          path: test-results/ai-analysis/
```

### AI Testing Best Practices

#### ✅ DO:
- **Run AI tests regularly** during development
- **Review AI-generated screenshots** for visual validation
- **Follow AI accessibility recommendations** immediately
- **Use AI performance insights** for optimization
- **Analyze AI bug reports** thoroughly
- **Update tests when UI patterns change**

#### ❌ DON'T:
- **Ignore AI accessibility violations**
- **Skip AI testing before releases**
- **Dismiss AI performance recommendations**
- **Forget to run AI analysis after major UI changes**
- **Override AI findings without investigation**

### Interpreting AI Test Results

#### Visual Analysis Screenshots
- **Component states**: Verify all variants render correctly
- **Responsive views**: Check layout adaptation across viewports
- **Interaction states**: Validate hover, focus, and active states
- **Error states**: Confirm error messaging displays properly

#### Accessibility Reports
- **Zero violations goal**: AI accessibility analysis should show no WCAG violations
- **Intelligent recommendations**: Follow AI suggestions for improvement
- **Keyboard navigation**: Verify AI validates proper tab order
- **Screen reader compatibility**: Check AI assessment of ARIA attributes

#### Performance Insights
- **Core Web Vitals**: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **Bundle analysis**: Review AI recommendations for size optimization
- **Loading patterns**: Check AI analysis of critical rendering path
- **Performance budgets**: Validate against AI-suggested thresholds

#### Bug Detection Reports
- **Critical issues**: Address any AI-detected critical problems immediately
- **Pattern recognition**: Review AI insights on common issue patterns
- **Cross-browser**: Check AI analysis of browser compatibility
- **Form validation**: Verify AI assessment of user input handling

### Advanced AI Testing Features

#### Custom AI Test Scenarios
Create specialized AI tests for your specific use cases:

```typescript
test('AI custom pattern analysis', async ({ page }) => {
  // Define your custom testing patterns
  await page.goto('/custom-component');
  
  // AI analyzes specific interaction patterns
  await page.locator('[data-testid="custom-element"]').click();
  
  // Capture AI evidence for custom scenarios
  await page.screenshot({ 
    path: 'test-results/ai-analysis/custom-pattern.png' 
  });
});
```

#### AI Test Configuration
Customize AI behavior via Playwright configuration:

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'AI-Powered Tests',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 }
      },
      testMatch: '**/ai-powered-*.spec.ts'
    }
  ]
});
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library Docs](https://testing-library.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Enhanced Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Axe Accessibility Rules](https://dequeuniversity.com/rules/axe/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Core Web Vitals](https://web.dev/vitals/)
- [AI Testing Best Practices](https://playwright.dev/docs/test-ai) 