# Iterate Design - Free Tier Parallel UI Variations

Generate multiple UI variations using free tools (Git worktrees + Claude) for rapid iteration and comparison.

## Free Workflow Overview

This command creates 3 isolated development environments to generate and compare UI variations simultaneously without requiring paid AI tools.

## Git Worktree Setup

### Step 1: Create Parallel Worktrees
```bash
# Create 3 worktrees for different UI approaches
git worktree add ../insighthub-ui-minimal feature/ui-minimal
git worktree add ../insighthub-ui-modern feature/ui-modern  
git worktree add ../insighthub-ui-elegant feature/ui-elegant
```

### Step 2: Install Dependencies (Optional)
```bash
# Only if worktrees need independent dependency management
cd ../insighthub-ui-minimal && npm install
cd ../insighthub-ui-modern && npm install
cd ../insighthub-ui-elegant && npm install
```

## Claude Generation Strategy

Use Claude to generate 3 variations sequentially in each worktree, then compare results:

### Variation 1: Minimal/Clean Style
**Target Directory**: `../insighthub-ui-minimal/`
**Design Philosophy**: 
- Maximum whitespace usage
- Subtle shadows and borders
- Clean typography hierarchy
- Minimal color usage (primary + neutrals)
- Hidden complexity, progressive disclosure

**Claude Prompt Template**:
```
Create a minimal/clean SvelteKit component for [COMPONENT_DESCRIPTION]:

Style Requirements:
- Use maximum whitespace for breathing room
- Apply subtle shadows (shadow-sm, shadow-md)
- Clean typography with Inter font
- Primary color: #3B82F6, neutrals: gray-50 to gray-900
- Hide complex features behind simple interfaces
- Mobile-first responsive design

TypeScript + TailwindCSS + Accessibility required.
Create complete .svelte component file.
```

### Variation 2: Bold/Modern Style  
**Target Directory**: `../insighthub-ui-modern/`
**Design Philosophy**:
- Strong visual hierarchy
- Vibrant colors from design system
- Bold typography and contrast
- Contemporary interaction patterns
- Confident, dynamic appearance

**Claude Prompt Template**:
```
Create a bold/modern SvelteKit component for [COMPONENT_DESCRIPTION]:

Style Requirements:
- Strong visual hierarchy with bold typography
- Vibrant colors: #3B82F6 (primary), #10B981 (secondary), #8B5CF6 (accent)
- High contrast design with bold font weights
- Contemporary animations and interactions
- Confident, modern aesthetic

TypeScript + TailwindCSS + Accessibility required.
Create complete .svelte component file.
```

### Variation 3: Elegant/Sophisticated Style
**Target Directory**: `../insighthub-ui-elegant/`
**Design Philosophy**:
- Refined spacing and typography
- Subtle gradients and shadows
- Professional, polished appearance
- Attention to micro-interactions
- Premium, sophisticated feel

**Claude Prompt Template**:
```
Create an elegant/sophisticated SvelteKit component for [COMPONENT_DESCRIPTION]:

Style Requirements:
- Refined spacing with perfect proportions
- Subtle gradients and elegant shadows
- Professional typography with careful line spacing
- Polished micro-interactions and transitions
- Premium, sophisticated appearance

TypeScript + TailwindCSS + Accessibility required.
Create complete .svelte component file.
```

## Implementation Process

### Phase 1: Setup
1. Create Git worktrees for 3 variations
2. Switch to first worktree
3. Use Claude with Variation 1 prompt
4. Generate component and test locally

### Phase 2: Generate Variations
1. Switch to each worktree sequentially
2. Use appropriate Claude prompt for each style
3. Generate complete SvelteKit component
4. Test basic functionality in browser

### Phase 3: Compare and Select
1. Screenshot each variation
2. Compare side-by-side in browser
3. Evaluate against project requirements:
   - **User Experience**: Which feels most intuitive?
   - **Brand Alignment**: Which matches InsightHub vision?
   - **Technical Quality**: Which has cleanest code?
   - **Performance**: Which loads fastest?
   - **Accessibility**: Which has best a11y support?

### Phase 4: Integration
1. Select winning variation or combine best elements
2. Copy chosen component to main branch
3. Clean up worktrees: `git worktree remove ../insighthub-ui-*`
4. Commit final component with descriptive message

## Quality Checklist for Each Variation

### ✅ Technical Requirements
- [ ] TypeScript interfaces for all props
- [ ] TailwindCSS classes from design system
- [ ] ARIA labels and semantic HTML
- [ ] Mobile-responsive design
- [ ] data-testid attributes for testing

### ✅ Performance Standards
- [ ] Component bundle <10KB
- [ ] No unnecessary dependencies
- [ ] Optimized images and assets
- [ ] Lazy loading where appropriate

### ✅ Design System Compliance
- [ ] Uses approved color palette
- [ ] Follows typography scale
- [ ] Consistent spacing patterns
- [ ] Proper border radius and shadows

### ✅ User Experience
- [ ] Clear visual hierarchy
- [ ] Intuitive interaction patterns
- [ ] Loading and error states
- [ ] Keyboard navigation support

## Example: Content Feed Card Iteration

### Component Description
"Content feed card displaying article title, excerpt, thumbnail, author, and engagement metrics"

### Generated Variations
1. **Minimal**: Clean white card with subtle border, minimal metadata
2. **Modern**: Bold typography, colorful category tags, prominent CTA
3. **Elegant**: Refined spacing, subtle gradients, premium typography

### Selection Criteria
- **Content Priority**: Which highlights content best?
- **Engagement**: Which encourages clicks/interaction?
- **Scanability**: Which supports quick content scanning?
- **Brand Fit**: Which aligns with InsightHub personality?

## Automation Opportunities

### Future Enhancements (Still Free)
1. **Shell Scripts**: Automate worktree creation and cleanup
2. **npm Scripts**: Add package.json scripts for workflow
3. **Playwright Testing**: Automated screenshot comparison
4. **Git Hooks**: Auto-cleanup of abandoned worktrees

### When to Upgrade to Paid Tools
- **Bottleneck**: Manual comparison becomes time-consuming
- **Scale**: Need >5 variations per component
- **Quality**: Need professional design review
- **Speed**: Iteration time >2 hours per component

This free workflow provides 80% of the benefits of paid tools while maintaining complete cost control and learning opportunities. 