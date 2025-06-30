---
description: Multi-agent development workflow using Git worktrees and Taskmaster for isolated feature development
globs: **/*
alwaysApply: true
---

# Multi-Agent Git Worktree Development Workflow

**This rule defines the standard process for multi-agent development using Git worktrees and Taskmaster.**

## Key Principles
- **Always use Git worktrees for feature development - main repository stays on main branch**
- **Work directly in master tag context - avoid complex tag operations that risk data loss**
- **Create worktree first, then identify and work on specific tasks/subtasks**
- **Keep task management simple and safe**

### DO / DON'T Examples
```bash
# ✅ DO: Create worktree first, then work on specific task in master context
git worktree add -b feat/new-login ../login-feature main
cd ../login-feature
task-master show 35.8  # Work directly on the task

# ❌ DON'T: Use complex tag moving operations that risk data loss
# ❌ DON'T: Create new tags or copy tags for simple feature work

# ✅ DO: Work directly on subtasks in master tag
task-master set-status --id=35.8 --status=in-progress
task-master update-subtask --id=35.8 --prompt="Starting implementation..."

# ❌ DON'T: Move tasks between tags unless absolutely necessary
```

---

## See also
- @taskmaster.mdc
- @self_improve.mdc
- @tdd_testing.mdc
- @type_schema_style.mdc
- @anti_patterns.mdc
- @immutability_functional.mdc
- @python_development.mdc

---

## Standard Operating Procedure

**Follow this simplified three-phase process for all feature development.**

### **Phase 1: Create Worktree & Identify Work**

- **Survey for Work**: From the main repository directory, list available tasks
  ```bash
  task-master list
  task-master next
  ```

- **Create Worktree & Branch**: Create an isolated environment for development
  ```bash
  git worktree add -b feat/feature-name ../feature-name-worktree main
  ```

- **Initialize Development Context**: Move into the new worktree (stay in master tag)
  ```bash
  cd ../feature-name-worktree
  ```

- **Identify Specific Task**: Choose the specific task/subtask to work on
  ```bash
  task-master show <task-id>  # e.g., task-master show 35.8
  ```

### **Phase 2: The Development Loop**

**This iterative loop occurs entirely within the feature's dedicated worktree, working in master tag:**

- **Start Task**: Set the task/subtask status to in-progress
  ```bash
  task-master set-status --id=<task-id> --status=in-progress
  ```

- **Log Implementation Plan**: Use `task-master update-subtask` to document approach
- **Implement Code**: Follow TDD principles during development
- **Log Progress**: Use `task-master update-subtask` to record findings and decisions
- **Mark Complete**: Use `task-master set-status --id=<task-id> --status=done`
- **Commit Work**: `git commit -m "feat: complete task/subtask X"`
- **Continue**: Work on related subtasks or identify next task

### **Phase 3: Integrate & Finalize**

- **Return to Main Repository**: Navigate back to the main directory
- **Merge Feature**: Integrate the completed feature branch
  ```bash
  git checkout main
  git merge feat/feature-name
  ```

- **Cleanup Git**: Remove the feature's worktree and branch
  ```bash
  git worktree remove ../feature-name-worktree
  git branch -d feat/feature-name
  ```

- **Verify Task Status**: Ensure completed tasks are marked as done in master tag
  ```bash
  task-master list --status=done
  ```

---

## **Taskmaster Integration Guidelines**

### **Primary Interaction Methods**

- **MCP Server (Recommended for AI Agents)**: Use MCP tools for better performance and structured data exchange
  - Refer to @mcp.mdc for MCP architecture details
  - See @taskmaster.mdc for comprehensive tool reference
  - Restart MCP server if core logic changes

- **CLI (For Users & Fallback)**: Use `task-master` command for direct terminal interaction
  - Install globally: `npm install -g task-master-ai`
  - Use locally: `npx task-master-ai ...`

### **Safe Task Management Practices**

- **Work in Master Tag**: Avoid creating or switching tags for simple feature work
- **Use Simple Operations**: Prefer `show`, `set-status`, `update-subtask` over complex operations
- **Avoid Tag Operations**: Only use tags for major branching strategies, not routine feature work
- **Backup Before Complex Operations**: Always backup tasks.json before any bulk operations

### **Task Management Best Practices**

- **Complexity Analysis**: Use `analyze_project_complexity --research` for comprehensive analysis
- **Task Breakdown**: Use `expand_task` with complexity reports or `--num` for specific subtask count
- **Implementation Drift**: Use `update` or `update_task` when approach changes significantly
- **Status Management**: Use 'pending', 'done', 'deferred', or custom statuses
- **Dependencies**: Use `add_dependency` and `remove_dependency` to manage task relationships

### **Task Structure Fields**

- **id**: Unique identifier (e.g., `1`, `1.1`)
- **title**: Brief, descriptive title
- **description**: Concise summary of task scope
- **status**: Current state (`pending`, `done`, `deferred`)
- **dependencies**: IDs of prerequisite tasks with status indicators
- **priority**: Importance level (`high`, `medium`, `low`)
- **details**: In-depth implementation instructions
- **testStrategy**: Verification approach
- **subtasks**: List of smaller, specific tasks

### **Iterative Subtask Implementation Process**

1. **Understand Goal**: Use `task-master show <subtaskId>` for detailed requirements
2. **Plan Implementation**: Explore codebase and identify specific changes needed
3. **Log the Plan**: Use `update_subtask` with complete findings and approach
4. **Verify Planning**: Confirm plan was logged successfully
5. **Begin Implementation**: Set status to `in-progress` and start coding
6. **Log Progress**: Regularly append findings, successes, and failures
7. **Update Rules**: Create/update rules based on new patterns discovered
8. **📚 Document Architecture**: Create comprehensive documentation in `docs/` folder
9. **Mark Complete**: Set status to `done` after verification
10. **Commit Changes**: Stage and commit with comprehensive message
11. **Proceed**: Identify next subtask using `task-master next`

---

## **📚 Documentation Requirements**

### **Critical Documentation Principle**
**ALL significant architectural changes, QA processes, testing strategies, and implementation patterns MUST be documented in the `docs/` folder immediately upon completion.**

### **Documentation Standards**
- **Location**: Use `docs/` folder with appropriate subdirectories (`docs/frontend/`, `docs/backend/`, `docs/testing/`)
- **Format**: Markdown files with clear structure, examples, and cross-references
- **Timing**: Document DURING implementation, not as an afterthought
- **Content**: Include architecture diagrams, implementation details, troubleshooting guides, and team guidelines

### **Documentation Triggers**
- **New QA Infrastructure**: Document in `docs/frontend/QUALITY_ASSURANCE.md`
- **Testing Strategies**: Document in `docs/testing/`
- **API Changes**: Document in `docs/backend/`
- **Architecture Updates**: Update `docs/ARCHITECTURE.md`
- **Workflow Changes**: Update this rule and related documentation

### **DO / DON'T Examples**
```bash
# ✅ DO: Create documentation immediately after implementation
task-master update-subtask --id=35.7 --prompt="QA infrastructure complete"
# Create docs/frontend/QUALITY_ASSURANCE.md with full implementation details

# ❌ DON'T: Mark task complete without documentation
task-master set-status --id=35.7 --status=done
# Without creating proper documentation in docs/ folder
```

---

## **⚠️ CRITICAL: Avoid Data Loss**

### **Tag System Safety**
- **NEVER use `copy_tag` or complex tag operations for routine feature work**
- **NEVER create new tags unless working on major architectural changes**
- **NEVER move tasks between tags unless absolutely necessary**
- **ALWAYS work in master tag context for normal feature development**

### **Safe Operations Only**
```bash
# ✅ SAFE: Work directly on tasks in master context
task-master show 35.8
task-master set-status --id=35.8 --status=in-progress
task-master update-subtask --id=35.8 --prompt="Progress update"

# ❌ DANGEROUS: Tag operations that risk data loss
# task-master add-tag feat-something
# task-master copy-tag master feat-something
# task-master move --from=master.5 --to=feat-something.1
```

---

## Maintenance Notes
- **Review and update this workflow after major releases, process changes, or when new patterns emerge**
- **Cross-reference new or updated rules as needed**
- **Encourage all contributors to suggest workflow improvements**
- **Update task management practices as Taskmaster features evolve**
- **📚 Maintain documentation in `docs/` folder for all workflow changes**
- **⚠️ ALWAYS prioritize data safety over complex workflows**