# Actionable Code Quality Checklist

This document provides a checklist for ensuring high code quality across the InsightHub project. Use it during development and code reviews to promote clean, maintainable, and robust code.

---

## Readability & Consistency

- [ ] **Naming Conventions:**
    - **Review Question:** Are variables, functions, classes, and file names clear, descriptive, and consistent?
    - **Action (Code Review):** Check that Python files and variables use `snake_case`, while TypeScript/Svelte variables and functions use `camelCase`. Component files should be `PascalCase.svelte`.
- [ ] **Code Formatting:**
    - **Action:** Before committing, run the project formatters: `black` for Python and `prettier` for Svelte/TypeScript.
    - **Review Question:** Does all code adhere to the automated formatting rules? Are there any manual formatting overrides that hinder readability?
- [ ] **Comments & Documentation:**
    - **Review Question:** Is complex or non-obvious logic explained with comments that clarify *why* something is done, not *what* it does?
    - **Action (Code Review):** Identify "magic numbers" or hardcoded strings that should be constants with descriptive names.
- [ ] **Type Safety:**
    - **Action:** Run `npx svelte-check` in the frontend directory and `mypy .` in the backend directory.
    - **Review Question:** Are there any type errors? Is the `any` type used excessively where a more specific type could be defined?

---

## Maintainability & Architecture

- [ ] **DRY (Don't Repeat Yourself) Principle:**
    - **Review Question:** Is there duplicated code that could be refactored into a reusable function, component, or utility?
- [ ] **Single Responsibility Principle (SRP):**
    - **Review Question:** Does each function, component, or class have one clear responsibility? Or is it trying to do too many things at once?
    - **Example:** A Svelte component should primarily handle UI and user interactions, while complex business logic should be in a separate utility or service.
- [ ] **Modularity & Cohesion:**
    - **Review Question:** Are related functions and data grouped logically into modules or services?
    - **Action (Code Review):** Check for large, monolithic files that could be broken down into smaller, more focused modules.
- [ ] **Configuration Management:**
    - **Review Question:** Are configuration values (e.g., API URLs, thresholds) hardcoded?
    - **Action:** Ensure all configuration is loaded from environment variables (`$env/static/private` in SvelteKit) or a dedicated config file.

---

## Testing

- [ ] **Test Coverage & Quality:**
    - **Review Question:** Do new features have corresponding tests (unit, integration)? Is critical logic covered?
    - **Action:** Run tests and check the coverage report. Is the coverage percentage reasonable for the changes made?
- [ ] **Test Readability & Independence:**
    - **Review Question:** Are the tests easy to understand? Do they clearly state what they are testing?
    - **Review Question:** Are tests independent and free of side effects? Can they be run in any order?
- [ ] **Testing the "What," Not the "How":**
    - **Review Question:** Do tests verify the public API or user-facing behavior of a function/component, rather than its internal implementation details? This makes them less brittle to refactoring.

---

## Best Practices & Error Handling

- [ ] **Linter Adherence:**
    - **Action:** Run `ruff check .` for Python and `eslint .` for TypeScript/Svelte.
    - **Review Question:** Are all linter warnings and errors addressed?
- [ ] **Error Handling:**
    - **Review Question (Backend):** Are potential errors (e.g., database failures, invalid input) caught gracefully? Does the API return clear, standardized error responses instead of crashing or leaking stack traces?
    - **Review Question (Frontend):** Is data fetched from the backend or user input validated? Is feedback shown to the user if an operation fails?
- [ ] **Avoiding Anti-Patterns:**
    - **Review Question (Svelte):** Are we mutating props directly? Are we creating memory leaks by failing to unsubscribe from stores or event listeners in `onDestroy`?
    - **Review Question (Python):** Are we using mutable default arguments in functions? Are we handling lists and dictionaries in a thread-safe manner if necessary?
- [ ] **Security Implications:**
    - **Action (Code Review):** Cross-reference changes with the `SECURITY_CHECKLIST.md`.
    - **Review Question:** Does this change introduce any potential security risks, such as exposing sensitive data or creating a new attack vector? (e.g., using `{@html ...}` in Svelte with un-sanitized data). 