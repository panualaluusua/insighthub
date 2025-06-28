# @test-detect - AI-Powered Bug Detection

Automatically detect bugs, issues, and potential problems in UI components using Playwright MCP's intelligent analysis capabilities.

## Usage
`@test-detect [scope] [severity]`

## Parameters
- `scope`: What to analyze (component, page, app, changed-files)
- `severity`: Bug severity filter (critical, high, medium, low, all)

## Examples
```
@test-detect app critical
@test-detect LoginForm all
@test-detect changed-files high
@test-detect /dashboard medium
```

## Detection Categories

### 1. **Functional Bugs**
- Broken interactions (clicks, forms, navigation)
- JavaScript errors and exceptions
- API call failures
- State management issues
- Event handling problems

### 2. **Visual Bugs**
- Layout breaks and overlaps
- Missing or broken images
- CSS rendering issues
- Responsive design failures
- Typography problems

### 3. **Accessibility Bugs**
- Missing alt text
- Poor color contrast
- Keyboard navigation issues
- Screen reader incompatibility
- Focus management problems

### 4. **Performance Issues**
- Slow loading components
- Memory leaks
- Excessive re-renders
- Large bundle sizes
- Unoptimized images

### 5. **Security Vulnerabilities**
- XSS vulnerabilities
- Exposed sensitive data
- Insecure API calls
- Missing CSRF protection
- Weak authentication

## AI-Powered Detection Methods

### Vision-Based Analysis
- **Screenshot Comparison**: Detects visual regressions
- **Layout Analysis**: Identifies structural problems
- **Color Analysis**: Finds contrast and consistency issues
- **Text Recognition**: Validates content accuracy
- **Pattern Recognition**: Spots UI inconsistencies

### Behavioral Analysis
- **User Flow Testing**: Simulates real user interactions
- **Error Simulation**: Tests error handling scenarios
- **Edge Case Detection**: Finds boundary condition failures
- **Performance Profiling**: Identifies bottlenecks
- **Security Scanning**: Detects vulnerabilities

### Code Analysis Integration
- **Static Analysis**: Reviews code for potential issues
- **Dependency Scanning**: Checks for vulnerable packages
- **Best Practice Validation**: Ensures coding standards
- **Type Safety**: Validates TypeScript compliance
- **Linting Integration**: Combines with ESLint/Prettier

## Detection Output

```
Bug Detection Report
===================

Scope: [analyzed scope]
Severity Filter: [filter applied]
Scan Duration: [time taken]
Timestamp: [datetime]

## Summary
- Total Issues Found: [count]
- Critical: [count] | High: [count] | Medium: [count] | Low: [count]
- New Issues: [count] | Regression Issues: [count]

## Critical Issues (Immediate Action Required)
1. **[Bug Title]**
   - Component: [component name]
   - Type: [functional/visual/accessibility/performance/security]
   - Description: [detailed description]
   - Impact: [user impact description]
   - Steps to Reproduce: [step-by-step]
   - Expected vs Actual: [comparison]
   - Fix Suggestion: [AI-generated fix]
   - Code Location: [file:line]
   - Screenshot: [if applicable]

## Recommendations
- **Quick Fixes**: [list of easy wins]
- **Priority Order**: [suggested fix sequence]
- **Prevention**: [how to avoid similar issues]
- **Testing Strategy**: [additional tests needed]
```

## Automated Actions

### Issue Tracking Integration
- **Taskmaster Tasks**: Automatically creates tasks for bugs
- **Priority Assignment**: Sets priority based on severity
- **Assignment Logic**: Routes to appropriate team members
- **Progress Tracking**: Monitors fix implementation

### CI/CD Integration
- **Pre-commit Hooks**: Runs detection before commits
- **PR Analysis**: Analyzes pull requests for new bugs
- **Deployment Blocking**: Prevents deployment with critical bugs
- **Regression Testing**: Validates fixes don't break other features

### Notification System
- **Slack Integration**: Sends alerts for critical issues
- **Email Reports**: Daily/weekly bug summaries
- **Dashboard Updates**: Real-time bug tracking
- **Mobile Alerts**: Push notifications for urgent issues

## Machine Learning Features

### Pattern Recognition
- **Bug Pattern Learning**: Learns from historical bugs
- **Predictive Analysis**: Predicts likely bug locations
- **Similarity Detection**: Finds similar issues across codebase
- **Root Cause Analysis**: Identifies underlying causes

### Continuous Improvement
- **False Positive Reduction**: Learns from user feedback
- **Detection Accuracy**: Improves over time
- **Custom Rules**: Adapts to project-specific patterns
- **Performance Optimization**: Faster scanning with experience

## Integration with Development Workflow

### IDE Integration
- **Real-time Detection**: Highlights issues as you code
- **Quick Fixes**: Provides one-click solutions
- **Contextual Help**: Shows relevant documentation
- **Code Suggestions**: AI-powered improvements

### Testing Integration
- **Test Generation**: Creates tests for found bugs
- **Regression Prevention**: Ensures bugs don't return
- **Coverage Analysis**: Identifies untested code paths
- **Test Optimization**: Improves test effectiveness 