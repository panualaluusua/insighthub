# Actionable Cost Audit Checklist

This document provides a hands-on checklist for auditing and optimizing the costs associated with the InsightHub project. Use it periodically to identify potential savings.

---

## Cloud Infrastructure (Supabase)

- [ ] **Database Compute & Usage:**
    - **Action:** Go to `Dashboard > Reports > Database` and check the CPU, Memory, and I/O usage patterns over the last month.
    - **Review Question:** Is our current compute add-on appropriate for our traffic? Are we consistently below 50% CPU usage? Could we downgrade to a smaller instance without impacting performance?
    - **Review Question:** Are there any unused development/staging database instances that can be paused or deleted?
- [ ] **Storage Optimization:**
    - **Action:** Review Supabase Storage buckets. Are there large, old, or unreferenced files that can be deleted?
    - **Action:** Implement a lifecycle policy for storage buckets to automatically move old or infrequently accessed files to cheaper storage tiers (if available) or delete them.
- [ ] **Database & Table Structure:**
    - **Action:** Run `ANALYZE` on your tables. Check for unused indexes that consume storage and slow down writes.
    - **Review Question:** Are we using data types that are larger than necessary (e.g., `text` for a field that will only ever hold 10 characters)?
- [ ] **Network Egress:**
    - **Review Question:** Are we making large data transfers out of Supabase? Could any data processing be moved into a database function or an Edge Function to reduce egress costs?

---

## AI/LLM Usage

- [ ] **Model Selection:**
    - **Review Question:** Are we using the most cost-effective model for each specific task? For simple classification or summarization, could we use a smaller, cheaper model instead of a large one? (e.g., using `deepseek/deepseek-chat` instead of `deepseek/deepseek-r1` for simple tasks).
- [ ] **Prompt & Completion Optimization:**
    - **Review Question:** Are our prompts as concise as possible? Are we minimizing the number of tokens sent in each API request?
    - **Action:** Set a `max_tokens` limit on completions to prevent unexpectedly long and expensive responses from the LLM.
- [ ] **API Call Caching:**
    - **Action (Code Review):** Identify LLM API calls that are likely to be repeated with the same input. Implement a caching layer (e.g., using Redis or a simple database table) to store and reuse results, avoiding redundant API calls.
- [ ] **Usage Monitoring:**
    - **Action:** Implement logging to track the number of tokens used per API call and attribute costs to specific features or users.

---

## CI/CD (GitHub Actions)

- [ ] **Runner Optimization:**
    - **Review Question:** Are our CI jobs using larger-than-necessary GitHub-hosted runners? Could we switch to smaller runners for simple linting or testing jobs?
- [ ] **Workflow Efficiency:**
    - **Action:** Review the runtime of your most frequent workflows. Are there slow steps that could be parallelized or optimized?
    - **Action:** Implement caching for dependencies (`npm`, `pip`, `poetry`) to significantly speed up job setup times and reduce runner minutes.
- [ ] **Trigger Conditions:**
    - **Review Question:** Are workflows being triggered unnecessarily? For example, does a documentation change need to trigger a full backend deployment pipeline? Refine `on:` triggers and `paths` filters.

---

## Data Processing & External APIs

- [ ] **Third-Party API Usage:**
    - **Action (Code Review):** Are we making redundant calls to external APIs? Can results be cached?
    - **Review Question:** Are we subscribed to the optimal pricing tier for our usage volume on third-party services?
- [ ] **Data Transfer:**
    - **Review Question:** Are we efficiently batching data sent to external services?

---

## General Architecture & Review Process

- [ ] **Regular Audits:**
    - **Action:** Schedule a recurring calendar event (e.g., quarterly) for the team to run through this entire checklist.
- [ ] **Cost-Benefit Analysis:**
    - **Review Question:** For each third-party service or managed tool we use, is the cost justified by the time and effort it saves our team? Could we replace it with a cheaper or open-source alternative? 