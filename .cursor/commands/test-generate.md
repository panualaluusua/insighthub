# @test-generate - AI-Powered Test Generation

Generate comprehensive tests for UI components using Playwright MCP with vision capabilities.

## Usage
`@test-generate [component-name] [test-type]`

## Parameters
- `component-name`: Name of the component to test (e.g., "Button", "LoginForm")
- `test-type`: Type of test to generate (unit, integration, e2e, accessibility, visual)

## Examples
```
@test-generate Button accessibility
@test-generate LoginForm e2e
@test-generate ContentFeed visual
@test-generate MainNavigation integration
```

## What This Command Does

1. **Analyzes Component Structure**: Uses Playwright MCP to examine the component's DOM structure, props, and behavior
2. **Generates Test Scenarios**: Creates comprehensive test cases covering:
   - User interactions (click, type, hover, focus)
   - State changes and prop updates
   - Accessibility compliance (WCAG 2.1 AA)
   - Visual regression testing
   - Cross-browser compatibility
   - Mobile responsiveness

3. **Creates Test Files**: Automatically generates:
   - Unit tests with Testing Library
   - E2E tests with Playwright
   - Visual regression tests with screenshots
   - Accessibility tests with axe-core

4. **AI-Powered Assertions**: Uses vision mode to generate intelligent assertions based on visual analysis

## Implementation Strategy

The command leverages Playwright MCP's vision capabilities to:
- Take screenshots of component states
- Analyze visual hierarchy and layout
- Generate context-aware test assertions
- Create realistic user interaction scenarios
- Validate accessibility compliance

## Output Structure

Generated tests follow this structure:
```
tests/
├── unit/
│   └── [component-name].test.ts
├── e2e/
│   └── [component-name].spec.ts
├── visual/
│   └── [component-name].visual.spec.ts
└── accessibility/
    └── [component-name].a11y.spec.ts
```

## Integration with Existing Workflow

- Tests are automatically added to the test suite
- CI/CD pipeline integration included
- Coverage reports updated
- Test results integrated with Taskmaster for tracking 