# Actionable Performance Audit Checklist

This document provides a hands-on checklist for auditing and optimizing the performance of the InsightHub project. Use it regularly to ensure a fast and responsive user experience.

---

## Frontend (SvelteKit/TypeScript)

- [ ] **Lighthouse Score:**
    - **Action:** Run a Lighthouse audit in Chrome DevTools on key pages (homepage, dashboard).
    - **Review Question:** Are the Performance, Accessibility, Best Practices, and SEO scores all above 90? What specific, low-hanging fruit does the report suggest?
- [ ] **Bundle Size & Composition:**
    - **Action:** Run `npm run build` and then `npx vite-bundle-visualizer` to analyze the final bundle composition.
    - **Review Question:** Are there any unexpectedly large libraries in our bundle? Can we replace heavy libraries (like `moment.js`) with smaller alternatives (like `date-fns`)?
- [ ] **Image & Asset Optimization:**
    - **Review Question:** Are all images served in modern formats (like WebP) and appropriately sized for their containers?
    - **Action:** Use the `<enhanced:img>` component for static images to automate optimization. For dynamic images, ensure they are compressed before upload.
- [ ] **Component Loading Strategy:**
    - **Review Question:** Are we loading large, non-critical components (e.g., complex charts, modals) immediately?
    - **Action (Code Review):** Use Svelte's `{#await import('./MyComponent.svelte')}` syntax to lazy-load components that are not visible on initial page load.
- [ ] **CSS Performance:**
    - **Review Question:** Is our critical CSS inlined for the fastest initial render? (SvelteKit often handles this well).
    - **Action (Code Review):** Are we using complex, deeply nested CSS selectors? Simplify selectors to improve style computation speed.

---

## Backend (Python/FastAPI)

- [ ] **API Response Time:**
    - **Action:** Use a tool like Postman or `curl` with timing flags to measure the response time of critical API endpoints.
    - **Review Question:** Are any endpoints consistently taking longer than 500ms to respond? Can the logic be optimized?
- [ ] **Database Query Performance (Supabase):**
    - **Action:** Use `EXPLAIN ANALYZE` on slow queries directly in the Supabase SQL Editor to understand their execution plan.
    - **Review Question:** Are we missing indexes on columns used in `WHERE`, `JOIN`, or `ORDER BY` clauses?
    - **Review Question (N+1 Problem):** In loops that fetch data, are we making one query per item instead of a single batch query? (e.g., fetching 10 posts and then making 10 separate queries for each post's author). Consolidate these into a single `JOIN` query.
- [ ] **Caching Strategy:**
    - **Review Question:** Are there API endpoints that return static or infrequently changing data?
    - **Action:** Implement a caching layer (e.g., Redis) for these endpoints to serve responses from memory, avoiding repeated computation or database hits.
- [ ] **Load Function Optimization (SvelteKit `+page.server.ts`):**
    - **Review Question:** Is our `load` function waiting for multiple, independent data fetches sequentially?
    - **Action (Code Review):** Run independent promises in parallel using `Promise.all()` to reduce the total wait time.
    - **Action (Code Review):** For non-essential data, stream promises directly to the client instead of `await`ing them in the `load` function. This allows the page to render faster while the less critical data loads in the background.

---

## Infrastructure & Network

- [ ] **Time to First Byte (TTFB):**
    - **Action:** Use a tool like WebPageTest or GTmetrix to measure TTFB from different locations.
    - **Review Question:** Is the TTFB consistently under 600ms? If not, investigate server-side processing or database bottlenecks.
- [ ] **Content Delivery Network (CDN):**
    - **Review Question:** Are our static assets (JS, CSS, images) being served via a CDN? (Supabase handles this for storage, but verify for other assets).
- [ ] **HTTP/2 or HTTP/3:**
    - **Action:** Check the "Protocol" column in the Chrome DevTools Network tab to ensure assets are served over `h2` or `h3`.

---

## CI/CD (GitHub Actions)

- [ ] **Workflow & Test Duration:**
    - **Action:** Review the "Actions" tab in GitHub. Are our CI/CD pipelines taking an excessively long time to complete?
    - **Review Question:** Can we run tests in parallel or optimize slow build steps to get faster feedback? 