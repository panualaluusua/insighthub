### Reflection on: Transitioning from n8n to LangChain

**1. What was accomplished:**
The project officially pivoted from a low-code n8n workflow to a code-first Python application built on LangChain. All n8n-related files were archived, and a new, detailed development plan was created in Taskmaster to guide the migration.

**2. What went well (with the n8n approach)?**
- **Rapid Prototyping:** n8n was excellent for quickly building a visual prototype of the InsightHub workflow. It helped validate the core logic (fetch -> process -> store) without getting bogged down in boilerplate code.
- **Visual Clarity:** The flowchart UI made it easy to understand the high-level data flow at a glance.

**3. What didn't go well (the pain points that triggered the change)?**
- **Code Integration was Awkward:** Writing custom logic required embedding JavaScript in small "Code" nodes, which was difficult to debug, version control, and test. Simple regex errors caused the entire workflow to fail with cryptic messages.
- **Lack of Control:** We hit the ceiling of the platform's abstractions. We couldn't easily implement complex state management, branching logic, or custom error handling without fighting the UI.
- **Poor Developer Experience:** The workflow was not developer-centric. It lacked features we take for granted: robust version control (editing a JSON file by hand is not a solution), automated testing, dependency management, and a proper debugging environment.
- **Scalability Concerns:** The visual model, while simple at first, would become unwieldy and difficult to manage as the project's complexity grew.

**4. What was learned?**
- **Low-code is for prototyping, not for production applications.** It's a powerful tool for initial exploration but becomes a liability for complex, long-term projects that require robustness and maintainability.
- **The right tool for the job matters.** For a project that is inherently about complex data processing and custom logic, a code-first framework is the appropriate choice.
- **Developer experience is critical.** A framework should empower developers, not constrain them. The friction of working against n8n's limitations was a clear sign that a change was needed.

**5. How will this impact future work?**
- **Foundation for a Robust Application:** By moving to LangChain/LangGraph, we can now build a scalable, testable, and maintainable application.
- **Increased Velocity:** While the initial setup is more involved, development speed will increase significantly once the core components are in place, as we can leverage the full power of Python and its ecosystem.
- **Clear Path Forward:** The new task plan provides a clear, actionable roadmap for building the application, ensuring we build it correctly from the ground up. The decision is now documented for any future team members. 