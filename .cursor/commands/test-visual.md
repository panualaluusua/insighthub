# @test-visual - AI-Powered Visual Analysis

Analyze UI components and pages using Playwright MCP's vision capabilities for comprehensive visual testing and improvement suggestions.

## Usage
`@test-visual [target] [analysis-type]`

## Parameters
- `target`: Component, page, or URL to analyze
- `analysis-type`: Type of visual analysis (layout, accessibility, usability, responsiveness, design)

## Examples
```
@test-visual /signin accessibility
@test-visual Button layout
@test-visual ContentFeed usability
@test-visual /dashboard responsiveness
@test-visual MainNavigation design
```

## Analysis Types

### 1. **Layout Analysis**
- Visual hierarchy assessment
- Spacing and alignment evaluation
- Typography consistency check
- Color scheme analysis
- Component composition review

### 2. **Accessibility Analysis**
- Color contrast validation
- Focus indicator visibility
- Text readability assessment
- Interactive element sizing
- Screen reader compatibility

### 3. **Usability Analysis**
- User flow evaluation
- Interaction pattern assessment
- Information architecture review
- Cognitive load analysis
- Error state handling

### 4. **Responsiveness Analysis**
- Breakpoint behavior testing
- Mobile-first design validation
- Touch target sizing
- Content reflow assessment
- Cross-device compatibility

### 5. **Design Analysis**
- Design system consistency
- Brand guideline compliance
- Visual appeal assessment
- Modern design pattern usage
- Competitive analysis

## AI-Powered Features

### Vision Mode Capabilities
- **Screenshot Analysis**: Captures and analyzes visual states
- **Layout Recognition**: Identifies UI patterns and structures
- **Accessibility Scanning**: Detects potential accessibility issues
- **Design Pattern Detection**: Recognizes common UI patterns
- **Anomaly Detection**: Identifies visual inconsistencies

### Intelligent Reporting
- **Visual Diff Generation**: Compares against design standards
- **Improvement Suggestions**: AI-generated recommendations
- **Priority Scoring**: Ranks issues by impact and effort
- **Code Suggestions**: Provides specific implementation fixes
- **Best Practice Guidance**: References industry standards

## Output Format

```
Visual Analysis Report
======================

Target: [component/page]
Analysis Type: [type]
Timestamp: [datetime]

## Summary
- Overall Score: [1-10]
- Critical Issues: [count]
- Recommendations: [count]

## Detailed Findings

### Critical Issues
1. [Issue description]
   - Impact: High/Medium/Low
   - Effort: High/Medium/Low
   - Suggestion: [specific fix]

### Recommendations
1. [Recommendation]
   - Benefit: [description]
   - Implementation: [code/approach]

### Screenshots
- Before: [screenshot]
- Annotations: [annotated screenshot]
- Suggested: [mockup if applicable]
```

## Integration Features

- **Automated Testing**: Generates regression tests based on analysis
- **Design System Updates**: Suggests design token improvements
- **Taskmaster Integration**: Creates tasks for identified issues
- **CI/CD Integration**: Runs analysis on every deployment
- **Performance Metrics**: Tracks visual performance over time

## Cross-Browser Analysis

Automatically tests across:
- Desktop: Chrome, Firefox, Safari
- Mobile: iOS Safari, Android Chrome
- Different viewport sizes
- Various color schemes (light/dark)
- Accessibility tools enabled 