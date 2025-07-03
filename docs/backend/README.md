# Backend Documentation

This section contains documentation for the Python backend components of InsightHub.

## Core Components

### 🎯 AI Processing Pipeline (Task 31 ✅)
- **[AI_PIPELINE.md](./AI_PIPELINE.md)** - Complete orchestrator implementation
  - LangGraph StateGraph topology
  - Processing nodes (ContentFetcher, Summarizer, Embedding, ContentScorer, Storage)
  - ErrorHandlerNode with classification & recovery
  - Retry management & circuit breaker patterns
  - Optimization pipeline with metrics-driven tuning

### 🔧 Infrastructure & Monitoring
- **[LANGSMITH_INTEGRATION.md](./LANGSMITH_INTEGRATION.md)** - LangSmith monitoring setup
- **[LANGSMITH_OPERATIONS.md](./LANGSMITH_OPERATIONS.md)** - Operational dashboards & workflows
- **[SUPABASE_INTEGRATION.md](./SUPABASE_INTEGRATION.md)** - Database integration

### 📊 API & Reference
- **[API_REFERENCE.md](./API_REFERENCE.md)** - Backend API endpoints

## Architecture Overview

The backend follows a **LangGraph-based orchestration pattern** where content flows through specialized processing nodes:

```
START → ContentFetcher → Summarizer → Embedding → ContentScorer → Storage → END
                                     ↓ (on error)
                              ErrorHandlerNode
```

See **[AI_PIPELINE.md](./AI_PIPELINE.md)** for complete technical details. 