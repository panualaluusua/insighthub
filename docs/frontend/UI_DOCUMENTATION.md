# 📚 UI Documentation Index

This index provides a central reference for all UI-related documentation, guidelines, and workflow rules for InsightHub Frontend.

---

## 🔗 Key UI Documentation

- [Component Guidelines](../../insighthub-frontend/COMPONENT_GUIDELINES.md) — Standards for building, testing, and documenting UI components
- [UI Development Workflow](../../.cursor/rules/ui/ui_development_workflow.mdc) — End-to-end UI workflow, including documentation requirements
- [Frontend Quality Assurance](QUALITY_ASSURANCE.md) — QA gates, testing, and accessibility
- [QA Processes](../../insighthub-frontend/QA_PROCESSES.md) — Full QA process, including UI testing

## 🎨 Design System & Patterns
- **Design Tokens:** Use TailwindCSS tokens and custom design system classes (see `tailwind.config.js`)
- **Typography, Colors, Spacing:** Follow patterns in [Component Guidelines](../../insighthub-frontend/COMPONENT_GUIDELINES.md)

## 🧑‍💻 How to Document UI Components

1. **Update or Create Documentation:**
   - For every new or changed UI component, update `COMPONENT_GUIDELINES.md` or create a new doc in `docs/frontend/`.
   - Include: props, usage examples, accessibility notes, and design system integration.

2. **Link Documentation to Task:**
   - Add a reference to the documentation in the relevant Taskmaster task (in `details`, `comments`, or a `docs` field).

3. **Add to This Index:**
   - Ensure your new/updated documentation is listed here for discoverability.

## 📝 Additional UI Docs & Rules
- [Svelte Component Patterns](../../.cursor/rules/svelte_component_ui.mdc)
- [UI Testing Standards](../../.cursor/rules/ui/testing_ui.mdc)
- [Performance UI Rules](../../.cursor/rules/performance_ui.mdc)
- [Accessibility UI Rules](../../.cursor/rules/accessibility_ui.mdc)
- [Tailwind Design UI](../../.cursor/rules/tailwind_design_ui.mdc)

---

**Always keep this index up to date when adding or changing UI documentation!** 