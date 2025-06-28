# InsightHub Component Library Guidelines

## Overview

This document outlines the standards and best practices for developing components in the InsightHub component library.

## Component Structure

### File Organization
```
src/lib/
├── components/
│   ├── Button.svelte          # Base components
│   ├── Input.svelte
│   ├── Card.svelte
│   ├── ContentCard.svelte     # Domain-specific components
│   └── ...
├── types/
│   └── index.ts               # All TypeScript interfaces
└── index.ts                   # Main exports
```

### Component Template
```svelte
<script lang="ts">
  import type { ComponentProps } from '../types/index.js';

  // Props with defaults
  export let prop1: ComponentProps['prop1'] = 'default';
  export let prop2: ComponentProps['prop2'] = false;
  
  // BaseComponentProps
  let className: string = '';
  export { className as class };
  export let id: string | undefined = undefined;
  export let testId: string | undefined = undefined;

  // Computed styles
  $: computedClasses = `base-classes ${className}`;
</script>

<div
  {id}
  class={computedClasses}
  data-testid={testId}
  on:click
  on:focus
  on:blur
>
  <slot />
</div>
```

## TypeScript Standards

### Interface Naming
- Component props interfaces: `ComponentNameProps` (e.g., `ButtonProps`)
- Extend `BaseComponentProps` for common props
- Use specific types over `any`

### Props Declaration
```typescript
// ✅ Good
export let variant: ButtonProps['variant'] = 'primary';

// ❌ Bad  
export let variant = 'primary';
```

### Event Handlers
```typescript
// ✅ Good - Optional with proper typing
export let onClick: (() => void) | undefined = undefined;

// ❌ Bad - Required without type
export let onClick: any;
```

## Styling Standards

### TailwindCSS Usage
- Use design system colors: `primary-*`, `secondary-*`, `gray-*`
- Follow spacing scale: `p-4`, `m-6`, `gap-3`
- Use consistent border radius: `rounded-lg`, `rounded-md`

### Responsive Design
```svelte
<!-- ✅ Good - Mobile first -->
<div class="p-4 md:p-6 lg:p-8">

<!-- ❌ Bad - Desktop first -->
<div class="p-8 md:p-6 sm:p-4">
```

### State Variants
```typescript
$: variantClasses = {
  primary: 'bg-primary-600 text-white',
  secondary: 'bg-gray-200 text-gray-900',
  outline: 'border-primary-600 text-primary-600'
}[variant];
```

## Accessibility Standards

### Required Attributes
- `data-testid` for testing
- `aria-label` for screen readers when needed
- `role` attributes for semantic meaning
- Proper focus management

### Keyboard Navigation
```svelte
<button
  on:click={handleClick}
  on:keydown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
```

### Color Contrast
- Ensure WCAG 2.1 AA compliance
- Test with accessibility tools
- Use semantic colors for status

## Component API Design

### Props
- Keep props minimal and focused
- Use sensible defaults
- Make optional props truly optional
- Use union types for variants

### Events
```svelte
<!-- ✅ Good - Forward all events -->
<button
  on:click
  on:focus
  on:blur
  on:mouseenter
  on:mouseleave
>

<!-- ✅ Good - Custom event handlers -->
<button on:click={handleClick}>
```

### Slots
```svelte
<!-- ✅ Good - Default slot for content -->
<div class="card">
  <slot />
</div>

<!-- ✅ Good - Named slots for structure -->
<div class="modal">
  <slot name="header" />
  <slot />
  <slot name="footer" />
</div>
```

## Testing Standards

### Component Testing
```typescript
// Example test structure
describe('Button Component', () => {
  test('renders with default props', () => {
    // Test implementation
  });
  
  test('handles click events', () => {
    // Test implementation
  });
  
  test('applies variant styles correctly', () => {
    // Test implementation
  });
  
  test('meets accessibility standards', () => {
    // Test implementation
  });
});
```

### Required Tests
- Rendering with default props
- All prop variations
- Event handling
- Accessibility compliance
- Error states

## Performance Guidelines

### Bundle Size
- Keep components lightweight
- Avoid unnecessary dependencies
- Use dynamic imports for large components

### Rendering
- Use `$:` reactive statements efficiently
- Avoid complex computations in templates
- Consider virtualization for large lists

## Documentation

### Component Props
```typescript
export interface ButtonProps extends BaseComponentProps {
  /** Button visual style variant */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  
  /** Whether button is disabled */
  disabled?: boolean;
  
  /** Show loading spinner */
  loading?: boolean;
  
  /** Click event handler */
  onClick?: () => void;
}
```

### Usage Examples
```svelte
<!-- Basic usage -->
<Button>Click me</Button>

<!-- With props -->
<Button 
  variant="primary" 
  size="lg" 
  loading={isLoading}
  onClick={handleSubmit}
>
  Submit
</Button>
```

## Best Practices

### Do's ✅
- Use TypeScript interfaces for all props
- Follow consistent naming conventions
- Implement proper accessibility
- Test all component variants
- Use design system tokens
- Forward DOM events
- Include loading/error states

### Don'ts ❌
- Use `any` type
- Hardcode colors or spacing
- Skip accessibility attributes
- Create overly complex components
- Ignore responsive design
- Forget error handling
- Mix business logic with presentation

## Design System Integration

### Colors
```typescript
// Use design system colors
const colors = {
  primary: 'primary-600',
  secondary: 'gray-200',
  success: 'green-600',
  warning: 'yellow-600',
  error: 'red-600'
};
```

### Typography
```css
/* Use consistent typography classes */
.heading-1 { @apply text-3xl font-bold text-gray-900; }
.heading-2 { @apply text-2xl font-semibold text-gray-900; }
.body-text { @apply text-base text-gray-700; }
.caption { @apply text-sm text-gray-600; }
```

### Spacing
```typescript
// Use design system spacing
const spacing = {
  xs: 'p-2',
  sm: 'p-4', 
  md: 'p-6',
  lg: 'p-8',
  xl: 'p-12'
};
```

## Component Lifecycle

1. **Design** - Create component design and API
2. **Implement** - Build component with TypeScript
3. **Test** - Write comprehensive tests
4. **Document** - Add usage examples and props
5. **Review** - Code review for standards compliance
6. **Integrate** - Add to component library exports

## Maintenance

### Regular Tasks
- Update dependencies
- Audit accessibility compliance
- Performance monitoring
- Design system alignment
- Documentation updates

### Version Control
- Use semantic versioning
- Document breaking changes
- Provide migration guides
- Maintain backwards compatibility when possible 