# Execute Parallel Agents

Automate the complete workflow for parallel UI development using Git worktrees and multiple Claude agents.

## Command Overview

This command sets up the entire parallel development environment:
1. Creates multiple Git worktrees for isolated development
2. Installs dependencies in each worktree
3. Launches parallel Claude agents assigned to specific worktrees
4. Each agent implements a different UI style/approach

## Workflow Steps

### 1. Worktree Setup
```bash
# Create 3 parallel worktrees from current branch
git worktree add ../insighthub-ui-minimal feature/ui-minimal
git worktree add ../insighthub-ui-modern feature/ui-modern  
git worktree add ../insighthub-ui-elegant feature/ui-elegant
```

### 2. Dependency Installation
```bash
# Install dependencies in each worktree
cd ../insighthub-ui-minimal && npm install
cd ../insighthub-ui-modern && npm install
cd ../insighthub-ui-elegant && npm install
```

### 3. Parallel Agent Assignment

#### Agent 1: Content-Focused Minimal Design
- **Worktree**: `../insighthub-ui-minimal`
- **Branch**: `feature/ui-minimal`
- **Focus**: Clean, content-first design prioritizing readability
- **Approach**: 
  - Maximize content visibility
  - Minimal navigation elements
  - Clean typography and spacing
  - Subtle interactive elements
  - Performance-optimized

#### Agent 2: Social Media Inspired Layout  
- **Worktree**: `../insighthub-ui-modern`
- **Branch**: `feature/ui-modern`
- **Focus**: Modern social platform aesthetics
- **Approach**:
  - Card-based content layout
  - Rich interaction patterns
  - Real-time update indicators
  - Engaging visual hierarchy
  - Mobile-first responsive design

#### Agent 3: Dashboard-Style Interface
- **Worktree**: `../insighthub-ui-elegant`
- **Branch**: `feature/ui-elegant`
- **Focus**: Information-dense, analytical interface
- **Approach**:
  - Data visualization focus
  - Professional aesthetic
  - Multiple content views
  - Advanced filtering and sorting
  - Power-user oriented features

## Agent Instructions

### Pre-Development Setup
Each agent should:
1. Navigate to assigned worktree directory
2. Verify SvelteKit project setup and dependencies
3. Review existing codebase and current progress
4. Understand assigned UI style and target users
5. Plan implementation approach

### Development Guidelines

#### Shared Technical Standards
- Follow SvelteKit + TypeScript conventions
- Use TailwindCSS for all styling
- Implement responsive mobile-first design
- Ensure accessibility compliance (WCAG 2.1 AA)
- Add comprehensive TypeScript types
- Include proper error handling

#### Style-Specific Requirements

**Agent 1 (Minimal)**:
```typescript
// Design principles for minimal approach
const minimalPrinciples = {
  whitespace: 'maximize for content focus',
  colors: 'neutral palette with single accent',
  typography: 'clear hierarchy, excellent readability',
  interactions: 'subtle, non-intrusive',
  layout: 'content-first, minimal chrome'
};
```

**Agent 2 (Modern)**:
```typescript
// Design principles for modern social approach  
const modernPrinciples = {
  layout: 'card-based content organization',
  interactions: 'rich, engaging, immediate feedback',
  colors: 'vibrant, contemporary palette',
  animations: 'smooth, purposeful micro-interactions',
  features: 'social platform patterns'
};
```

**Agent 3 (Elegant)**:
```typescript
// Design principles for dashboard approach
const elegantPrinciples = {
  information: 'high density, well organized',
  navigation: 'complex but intuitive',
  visualization: 'charts, graphs, analytics',
  workflow: 'efficient power-user experience',
  aesthetics: 'professional, sophisticated'
};
```

### Component Development Priority

#### Phase 1: Core Components (All Agents)
1. Layout and navigation structure
2. Content feed/list components  
3. Authentication forms (login/signup)
4. User profile components
5. Basic interaction patterns

#### Phase 2: Style-Specific Features
**Agent 1**: Content optimization, reading experience
**Agent 2**: Social interactions, real-time features
**Agent 3**: Analytics, advanced filtering, data views

#### Phase 3: Polish and Integration
1. Cross-component consistency
2. Performance optimization
3. Accessibility improvements
4. Testing implementation
5. Documentation

## Quality Assurance

### Code Review Standards
- TypeScript strict mode compliance
- TailwindCSS utility usage
- Component reusability
- Performance considerations
- Accessibility implementation

### Testing Requirements
```typescript
// Each agent should implement:
// 1. Unit tests for components
// 2. Integration tests for user flows
// 3. Visual regression tests
// 4. Accessibility tests

// Example test structure:
describe('Component Name', () => {
  test('renders correctly', () => {
    // Implementation
  });
  
  test('handles user interactions', () => {
    // Implementation  
  });
  
  test('meets accessibility standards', () => {
    // Implementation
  });
});
```

### Performance Benchmarks
- Bundle size: < 50KB per route
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse score: > 90 (all categories)

## Collaboration Workflow

### Daily Sync
1. Each agent commits progress to respective branch
2. Document key decisions and challenges
3. Share reusable components across worktrees
4. Identify cross-cutting concerns

### Component Sharing
```bash
# Script to share components between worktrees
./scripts/sync-components.sh component-name source-worktree target-worktree
```

### Integration Planning
1. Compare implementations across worktrees
2. Identify best practices from each approach
3. Plan unified component library
4. Merge strategies for final implementation

## Evaluation and Selection

### Comparison Matrix
| Criteria | Minimal | Modern | Elegant |
|----------|---------|---------|---------|
| User Experience | Content focus | Engagement | Efficiency |
| Visual Appeal | Clean | Contemporary | Professional |
| Performance | Optimized | Balanced | Feature-rich |
| Accessibility | Excellent | Good | Comprehensive |
| Maintainability | High | Medium | Complex |

### Selection Process
1. User testing with target audience
2. Performance benchmarking
3. Development team evaluation
4. Stakeholder feedback
5. Final decision and consolidation

## Cleanup and Consolidation

### After Selection
```bash
# Merge chosen approach to main branch
git checkout main
git merge feature/ui-[selected-style]

# Clean up worktrees
git worktree remove ../insighthub-ui-minimal
git worktree remove ../insighthub-ui-modern  
git worktree remove ../insighthub-ui-elegant

# Clean up feature branches
git branch -d feature/ui-minimal
git branch -d feature/ui-modern
git branch -d feature/ui-elegant
```

### Component Library Creation
- Extract reusable components
- Create unified design system
- Document component APIs
- Set up Storybook for component showcase
- Establish maintenance workflow

## Success Metrics

### Development Efficiency
- 3x faster iteration than sequential development
- Parallel exploration of design directions
- Reduced decision-making time
- Higher quality final output

### Code Quality
- Consistent implementation standards
- Comprehensive test coverage
- Excellent accessibility compliance
- Optimized performance across approaches

### Team Learning
- Exposure to different UI approaches
- Shared best practices
- Improved design system understanding
- Enhanced collaboration skills 