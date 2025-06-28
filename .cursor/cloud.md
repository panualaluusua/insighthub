# InsightHub UI Guidelines (Free Tier Focus)

## Framework Configuration
- **Framework**: SvelteKit + TypeScript + TailwindCSS
- **PWA**: Progressive Web App enabled
- **Database**: Supabase integration
- **Testing**: Vitest + Playwright (both free)
- **AI Tools**: Claude/Cursor (existing subscription)

## 🆓 Current Tier 1 (Free) Workflow
- **Primary AI**: Claude/Cursor (already available)
- **Parallel Development**: Git worktrees (free)
- **Design System**: TailwindCSS (open source)
- **Testing**: Playwright + Vitest (open source)
- **Deployment**: Vercel free tier

## Design System

### Colors
- **Primary**: #3B82F6 (blue-500)
- **Secondary**: #10B981 (emerald-500)  
- **Accent**: #8B5CF6 (violet-500)
- **Gray Scale**: Tailwind gray palette
- **Success**: #059669 (emerald-600)
- **Warning**: #D97706 (amber-600)
- **Error**: #DC2626 (red-600)

### Typography
- **Font Family**: Inter (primary), system-ui (fallback)
- **Heading Scale**: text-4xl, text-3xl, text-2xl, text-xl, text-lg
- **Body Text**: text-base, text-sm
- **Font Weights**: font-normal (400), font-medium (500), font-semibold (600), font-bold (700)

### Spacing System
- **Base Unit**: 4px (0.25rem)
- **Component Padding**: 4, 6, 8, 12, 16px
- **Layout Margins**: 16, 24, 32, 48px
- **Grid Gaps**: 4, 6, 8, 12, 16px

### Component Standards
- **Border Radius**: rounded-md (6px), rounded-lg (8px)
- **Shadows**: shadow-sm, shadow-md, shadow-lg
- **Transitions**: duration-200, ease-in-out
- **Focus States**: focus:ring-2 focus:ring-blue-500

## Free UI Generation Guidelines

### Component Creation Process
1. **Research**: Analyze similar components in the wild
2. **Wireframe**: Simple text description or ASCII art
3. **Generate**: Use Claude to create 3 variations
4. **Test**: Manual browser testing
5. **Refine**: Iterate based on feedback

### Claude UI Generation Instructions
- **Output Format**: Always create single SvelteKit component files
- **Styling**: Use only TailwindCSS classes from our design system
- **TypeScript**: Include proper type definitions for all props
- **Accessibility**: Add ARIA labels and semantic HTML
- **Mobile-First**: Responsive design required
- **Testing**: Include data-testid attributes for Playwright

### Parallel Generation Pattern
When creating UI variations, use this prompt structure:
```
Create 3 variations of [component description]:

Variation 1: Minimal/Clean approach
- Maximum whitespace
- Subtle borders and shadows
- Clean typography hierarchy

Variation 2: Bold/Modern approach  
- Strong visual hierarchy
- Vibrant colors from design system
- Bold typography

Variation 3: Elegant/Sophisticated approach
- Refined spacing and typography
- Subtle gradients and shadows
- Professional appearance

Each variation should be a complete SvelteKit component with TypeScript.
```

## Content-Specific Guidelines

### Content Feed Components
- **Card Design**: Consistent card structure with image, title, excerpt
- **Infinite Scroll**: Virtual scrolling for performance
- **Loading States**: Skeleton screens during data fetch
- **Error States**: Graceful error handling with retry options

### Authentication Components
- **Form Styling**: Consistent input styling with validation states
- **Button States**: Loading, disabled, success, error states
- **Progressive Enhancement**: Work without JavaScript
- **Security**: Proper form validation and error messages

### PWA Interface
- **Mobile-First**: Touch-friendly interface design
- **Offline States**: Clear offline indicators and cached content
- **App-like Feel**: Native app interaction patterns
- **Performance**: Optimize for mobile networks

## Quality Standards (Free Tier)

### Performance Targets
- **Bundle Size**: <50KB per page
- **First Paint**: <1.5s on 3G
- **Interactive**: <3s on 3G
- **Lighthouse Score**: >90

### Accessibility Requirements
- **WCAG**: 2.1 AA compliance
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Proper ARIA labels
- **Color Contrast**: 4.5:1 minimum ratio

### Testing Standards
- **Unit Tests**: >80% component coverage
- **E2E Tests**: Critical user journeys
- **Visual Testing**: Manual review process
- **Cross-Device**: Mobile, tablet, desktop

## Upgrade Path to Paid Tools

### When to Consider Tier 2 ($40-60/month)
- Team size > 2 developers
- UI iteration speed becomes bottleneck
- Need for advanced visual design tools
- Client work requires premium quality

### When to Consider Tier 3 ($100+/month)
- Production app > 1000 users
- Multiple client projects
- Revenue justifies investment
- Advanced testing and deployment needs

### Migration Strategy
1. **Measure Current Metrics**: Document baseline performance
2. **Identify Bottlenecks**: Where free tools limit productivity
3. **ROI Calculation**: Estimate value of paid tools
4. **Gradual Adoption**: Add one paid tool at a time
5. **Track Improvements**: Measure impact of each upgrade 