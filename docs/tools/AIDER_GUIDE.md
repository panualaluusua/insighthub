---
description: Complete guide to using Aider AI pair programming with TaskMaster and git worktree workflow
---

# Aider Usage Guide

**Aider is an AI pair programming tool that integrates seamlessly with our TaskMaster and git worktree development workflow.**

## What is Aider?

Aider is a command-line AI coding assistant that:
- **Edits files directly** based on natural language instructions
- **Understands your entire codebase** through repository mapping
- **Handles git operations** automatically with proper commit messages
- **Supports multiple AI models** (Claude, GPT-4, etc.)
- **Maintains conversation history** for context across sessions

---

## Integration with Our Workflow

### **Phase 1: Setup in Worktree**

After creating your worktree and identifying tasks with TaskMaster:

```bash
# Navigate to your feature worktree
cd ../feature-name-worktree

# Start aider session for a specific task
aider --message "Help me implement task 35.8: Add user authentication with JWT"
```

### **Phase 2: AI-Assisted Development Loop**

```bash
# Start interactive session with relevant files
aider src/auth.py src/middleware.py

# Or use one-shot commands
aider --message "Add password validation to the signup form" src/components/SignupForm.svelte

# For complex implementations, use interactive mode
aider
> Add JWT token validation middleware with refresh token support
> Make sure to handle edge cases and add proper error handling
```

### **Phase 3: TaskMaster Integration**

```bash
# Update task progress with findings
task-master update-subtask --id=35.8 --prompt="Implemented JWT auth with aider. Used bcrypt for hashing, added refresh token rotation."

# Mark task complete after aider implementation
task-master set-status --id=35.8 --status=done
```

---

## Essential Aider Commands

### **Starting Aider**

```bash
# Interactive mode with specific files
aider file1.py file2.js

# One-shot command
aider --message "Fix the validation bug in user registration" src/auth.py

# With specific model
aider --model claude-3-5-sonnet-20241022

# Read-only files for context
aider --read docs/API.md src/main.py
```

### **In-Session Commands**

```bash
# Add/remove files from editing scope
/add src/new-file.py
/drop src/old-file.py

# Add read-only files for context
/read docs/requirements.md

# Show current files in scope
/ls

# Commit current changes
/commit

# Clear conversation history
/clear

# Exit aider
/exit
```

---

## Configuration for Our Project

### **.aider.conf.yml Setup**

```yaml
# Model selection
model: claude-3-5-sonnet-20241022
weak-model: claude-3-5-haiku-20241022

# Git integration
auto-commits: true
dirty-commits: true
attribute-co-authored-by: true

# Code quality
auto-lint: true
lint-cmd:
  python: "ruff check --fix"
  javascript: "eslint --fix"
  typescript: "eslint --fix"

# Display preferences
pretty: true
dark-mode: true
stream: true
```

### **Environment Variables**

```bash
# Add to your .env file
ANTHROPIC_API_KEY=your_key_here
AIDER_MODEL=claude-3-5-sonnet-20241022
```

---

## Workflow Integration Patterns

### **🎯 Task-Driven Development**

```bash
# 1. Get task details from TaskMaster
task-master show 35.8

# 2. Start aider with task context
aider --message "Implement task 35.8: $(task-master show 35.8 --format=brief)"

# 3. Let aider analyze and plan
> Analyze the current auth system and propose JWT implementation approach

# 4. Implement step by step
> Start with the JWT utility functions
> Now add the middleware
> Update the login endpoint
```

### **🔍 Code Review & Refactoring**

```bash
# Review existing code before changes
aider --read src/auth.py
> Review this authentication code and suggest improvements

# Refactor with context
aider src/auth.py src/middleware.py
> Refactor this to use modern async/await patterns while maintaining backwards compatibility
```

### **🐛 Bug Fixing**

```bash
# Fix specific issues
aider tests/test_auth.py src/auth.py
> The login test is failing. Fix the issue and ensure all tests pass

# Debug with logs
aider --read logs/error.log src/problematic-file.py
> Based on this error log, fix the authentication issue
```

### **📚 Documentation Generation**

```bash
# Generate documentation
aider --message "Create comprehensive API documentation for the auth module" src/auth.py
> Include examples, error codes, and response formats
```

---

## Best Practices

### **✅ DO**

- **Start with clear, specific requests**: "Add JWT authentication with refresh tokens"
- **Include relevant files in scope**: Add both implementation and test files
- **Use TaskMaster task descriptions**: Copy task details into aider prompts
- **Commit frequently**: Let aider auto-commit or use `/commit` regularly
- **Review changes**: Always check aider's proposed changes before accepting

### **❌ DON'T**

- **Make vague requests**: "Make the code better" 
- **Include too many unrelated files**: Keep scope focused
- **Skip testing**: Always include test files when implementing features
- **Ignore linting**: Fix any linting issues aider introduces
- **Bypass TaskMaster**: Always update task status after aider sessions

---

## Advanced Usage

### **Multi-File Refactoring**

```bash
# Large-scale changes across multiple files
aider src/**/*.py
> Migrate from SQLAlchemy 1.4 to 2.0 across all models
> Update imports, query syntax, and relationship definitions
```

### **Test-Driven Development**

```bash
# Start with tests
aider tests/test_new_feature.py
> Write comprehensive tests for JWT refresh token functionality

# Then implement
aider tests/test_new_feature.py src/auth.py
> Implement the JWT refresh token feature to make these tests pass
```

### **Complex Integrations**

```bash
# Multiple technology stack changes
aider --read docs/ARCHITECTURE.md src/backend/ src/frontend/
> Integrate the new authentication system with both Python backend and Svelte frontend
> Ensure proper error handling and user experience
```

---

## Troubleshooting

### **Common Issues**

| Issue | Solution |
|-------|----------|
| Aider modifies wrong files | Use `/drop filename` to remove from scope |
| Changes break tests | Include test files in scope: `aider src/file.py tests/test_file.py` |
| Model limits exceeded | Use `--weak-model` for simple tasks |
| Git conflicts | Let aider handle commits or use `/commit` manually |

### **Performance Optimization**

```bash
# For large repos, limit scope
aider --subtree-only src/specific-module/

# Use cheaper models for simple tasks
aider --weak-model gpt-4o-mini --message "Fix typo in comment"

# Cache prompts for repeated operations
aider --cache-prompts
```

---

## Integration with Development Tools

### **With TaskMaster Research**

```bash
# Research before implementation
task-master research --query="JWT best practices 2024" --save-to=35.8

# Use research in aider
aider --read .taskmaster/docs/research/latest.md src/auth.py
> Implement JWT authentication using the researched best practices
```

### **With Git Worktrees**

```bash
# In feature worktree
cd ../auth-feature-worktree
aider src/auth.py
> Implement the authentication feature

# Auto-commits will be in the feature branch
# Merge back to main when complete
```

### **With Testing Pipeline**

```bash
# Implement with immediate testing
aider src/auth.py tests/test_auth.py
> Add password reset functionality with comprehensive tests
> Ensure all edge cases are covered
```

---

## See Also

- [Development Workflow](../general/dev_workflow.md) - Git worktree and TaskMaster integration
- [TaskMaster Guide](../tools/taskmaster.md) - Task management workflow
- [Testing Strategy](../testing/TESTING_STRATEGY.md) - Quality assurance processes

---

## Quick Reference

```bash
# Essential commands
aider file.py                    # Edit specific file
aider --message "task" file.py   # One-shot edit
aider --read doc.md file.py      # Include context
aider --model claude-3-5-sonnet  # Specify model

# In-session
/add file.py     # Add file to scope
/read file.md    # Add read-only context  
/commit          # Commit changes
/clear           # Clear history
/exit            # Exit aider
```

**Remember: Aider works best when you're specific about what you want and include relevant context files.** 