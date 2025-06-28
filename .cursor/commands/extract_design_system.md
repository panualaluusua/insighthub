# Extract Design System

Analyze the provided UI image/URL and extract comprehensive design system details.

## Analysis Process

1. **Color Palette Extraction**
   - Primary colors (main brand colors)
   - Secondary colors (accent and supporting colors)
   - Neutral colors (grays, whites, blacks)
   - State colors (success, warning, error, info)
   - Note color hex codes and usage patterns

2. **Typography Analysis**
   - Font families used (primary and fallback fonts)
   - Font sizes and scale relationships
   - Font weights and their usage hierarchy
   - Line heights and letter spacing
   - Text color combinations

3. **Spacing System**
   - Consistent spacing units (4px, 8px, 16px, etc.)
   - Margin and padding patterns
   - Component spacing relationships
   - Layout grid systems
   - Vertical rhythm patterns

4. **Component Patterns**
   - Button styles and variations
   - Card layouts and content structure
   - Form input designs and states
   - Navigation patterns
   - Icon usage and style

5. **Layout Structure**
   - Grid systems (12-column, flexbox, etc.)
   - Container widths and breakpoints
   - Positioning patterns
   - Responsive behavior
   - Layout hierarchy

## Output Format

Generate a JSON file named `design-system.json` with the following structure:

```json
{
  "colors": {
    "primary": {
      "main": "#3B82F6",
      "light": "#60A5FA",
      "dark": "#1E40AF"
    },
    "secondary": {
      "main": "#10B981",
      "light": "#34D399",
      "dark": "#047857"
    },
    "neutral": {
      "50": "#F9FAFB",
      "100": "#F3F4F6",
      "500": "#6B7280",
      "900": "#111827"
    },
    "semantic": {
      "success": "#059669",
      "warning": "#D97706",
      "error": "#DC2626",
      "info": "#0284C7"
    }
  },
  "typography": {
    "fontFamily": {
      "primary": "Inter, sans-serif",
      "secondary": "system-ui, sans-serif"
    },
    "fontSize": {
      "xs": "0.75rem",
      "sm": "0.875rem",
      "base": "1rem",
      "lg": "1.125rem",
      "xl": "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem",
      "4xl": "2.25rem"
    },
    "fontWeight": {
      "normal": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700
    },
    "lineHeight": {
      "tight": 1.25,
      "normal": 1.5,
      "relaxed": 1.75
    }
  },
  "spacing": {
    "unit": "4px",
    "scale": [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96],
    "component": {
      "xs": "8px",
      "sm": "12px",
      "md": "16px",
      "lg": "24px",
      "xl": "32px"
    }
  },
  "components": {
    "button": {
      "borderRadius": "6px",
      "padding": {
        "sm": "8px 16px",
        "md": "12px 24px",
        "lg": "16px 32px"
      },
      "fontSize": {
        "sm": "0.875rem",
        "md": "1rem",
        "lg": "1.125rem"
      }
    },
    "card": {
      "borderRadius": "8px",
      "padding": "24px",
      "shadow": "0 1px 3px rgba(0, 0, 0, 0.1)",
      "border": "1px solid #E5E7EB"
    },
    "input": {
      "borderRadius": "6px",
      "padding": "12px 16px",
      "border": "1px solid #D1D5DB",
      "focusBorder": "2px solid #3B82F6"
    }
  },
  "layout": {
    "container": {
      "maxWidth": "1200px",
      "padding": "24px"
    },
    "grid": {
      "columns": 12,
      "gutter": "24px"
    },
    "breakpoints": {
      "sm": "640px",
      "md": "768px",
      "lg": "1024px",
      "xl": "1280px"
    }
  }
}
```

## Additional Analysis Notes

- Identify any unique design patterns or custom components
- Note accessibility considerations (contrast ratios, touch targets)
- Document responsive behavior patterns
- Highlight any animation or transition patterns
- Include recommendations for SvelteKit + TailwindCSS implementation

## Usage

This extracted design system should be used as the foundation for all subsequent UI generation tasks. The JSON file will serve as the single source of truth for design decisions and ensure consistency across all generated components. 