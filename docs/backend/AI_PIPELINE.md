# AI Pipeline

This document describes the AI and LangChain-based data processing pipeline in InsightHub.

## Overview

The AI pipeline, located in the `src/orchestrator` directory, is responsible for taking the raw data fetched from Reddit and YouTube and transforming it into summarized, enriched content.

## Stages

1.  **Content Fetching:** Raw data is retrieved from the source APIs.

2.  **Transcription:** The `youtube_processor.py` (`src/youtube_processor.py`) now handles audio transcription for YouTube videos. It supports:
    -   **OpenAI Whisper API:** For high-quality and efficient transcriptions, with optional FFmpeg preprocessing to speed up audio and reduce costs.
    -   **Faster-Whisper (local):** As a fallback or for local processing.

3.  **Embedding:** The `embedding.py` node (`src/orchestrator/nodes/embedding.py`) uses `langchain_openai.OpenAIEmbeddings` to create vector embeddings of the content. This is a crucial step for any future semantic search or personalization features.

4.  **Summarization:** The `summarizer.py` node (`src/orchestrator/nodes/summarizer.py`) uses `langchain_openai.ChatOpenAI` to generate summaries of the content. The summarization prompts are dynamically created based on the content type and length.

## State Management

The `state.py` file (`src/orchestrator/state.py`) defines the state of the orchestration, including the `summarization_model` that is to be used.

## LangGraph **StateGraph** Architecture (Task 31.6)

> Introduced: July 2025 – implemented in `src/orchestrator/graph.py`

The InsightHub processing flow is orchestrated with **LangGraph's `StateGraph`** abstraction, giving us:

* **Declarative DAG** – nodes (callables) + edges define the complete workflow.
* **Automatic state propagation** – our `ContentState` (`TypedDict`) is passed and mutated immutably by each node.
* **Compile-time validation** – LangGraph checks node compatibility & edge correctness at graph compile time.

### Current Node Topology

```
START ─▶ content_fetcher ─▶ summarizer ─▶ embedding ─▶ scorer ─▶ storage ─▶ END
```

| Node | Module | Responsibility |
|------|--------|----------------|
| `content_fetcher` | `nodes.content_fetcher.ContentFetcherNode` | Routes fetching to YouTube/Reddit processors and populates raw/processed content & metadata. |
| `summarizer` | `nodes.summarizer.SummarizerNode` | Generates concise summary using DeepSeek V3 (LLM). |
| `embedding` | `nodes.embedding.EmbeddingNode` | Produces OpenAI vector embeddings for semantic search & ranking. |
| `scorer` | `nodes.content_scorer.ContentScorer` | Calculates multi-factor relevance score. |
| `storage` | `nodes.storage.StorageNode#store_content` | Persists final content to Supabase. |
| `error_handler` | `nodes.error_handler.ErrorHandlerNode` | Terminal node that converts uncaught exceptions into a **failed** `ContentState`, enriches it with `error_type`, `error_message`, timestamps, and decides (via `RetryManager`) if the orchestrator should attempt another retry. |

**Conditional Routing**

* `OrchestratorConfig.skip_embedding` (planned) can short-circuit the embedding node for specific workloads.
* Error edges will route to `error_handler` directly (planned for Task 32 when ranking branch is introduced).

### Extensibility Hooks

* **Ranking Branch:** a parallel branch placeholder after `embedding` can send content to a future RankingNode without blocking storage.
* **Optimization Pipeline:** when `ENABLE_OPTIMIZATIONS=true`, the high-level `Orchestrator` swaps execution to `OptimizedOrchestrator`, which still relies on the same `StateGraph` topology.

### Quick Start (Local Test)

```python
from src.orchestrator.graph import create_orchestrator_graph
from src.orchestrator.state import create_content_state

graph = create_orchestrator_graph()

state = create_content_state(
    source_type="youtube",
    source_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
)

result_state = graph.invoke(state)  # Executes full pipeline synchronously
print(result_state["summary"], result_state["embeddings"][:5])
```

### Testing & Validation

* **Unit tests:** `tests/test_orchestrator_graph.py` verifies node registration, edge ordering, START/END links & basic execution against mock nodes.
* **Integration tests:** forthcoming in Task 31.7 will execute the real graph with mocked external APIs to ensure end-to-end correctness.

### Error Handling & Recovery (NEW in Task 31.8)

Key behaviours:

* **Classification** – delegates to `ErrorClassifier` (network / timeout / transient / permanent / rate-limited / unknown).
* **State enrichment** – guarantees observability fields: `status`, `error_type`, `error_message`, `processed_at`, `retry_count`, `should_retry`.
* **Zero deps** – avoids heavy imports; safe to call from notebooks & ad-hoc scripts.

`Orchestrator._process_content_with_retry()` already routes failures through this node implicitly; future graph-level error edges can target `error_handler` directly (planned for Task 32 when ranking branch is introduced).

## Feedback-Driven User Profile Update Pipeline (Tasks #6 & #12)

The following real-time loop powers deep personalisation in InsightHub:

1. **Client-side feedback UI** – a single-click "Hide" menu asks the user *why* the item was hidden (Not relevant / Not now / Too superficial / Too advanced).
2. **`POST /api/v1/feedback`** – FastAPI endpoint validates UUIDs & enum, immediately queues the event and returns **202 Accepted**.
3. **Redis RQ queue** – lightweight, containerised in *docker-compose.yml*.
4. **`feedback_worker`** – background worker pops events, fetches the current `interest_vector` and content vector, then calls `UserProfileVectorManager.apply_feedback()`.
5. **Vector math** – `src/models/vector_math.py`
   * core formula  \(v_{new}=\operatorname{normalize}(v_{old}+w\,v_{content})\)
   * granular handlers for `TOO_SUPERFICIAL` / `TOO_ADVANCED` use projection to reduce only general or specific vector components.
6. **Persistence** – `src/storage/vector_store.py`
   * default `InMemoryVectorStore` for local dev
   * `SupabaseVectorStore` stub writes into `user_vectors` & `content_vectors` tables (pgvector, HNSW index).
7. **Supabase** – migrations created & pushed (`docs/backend/SUPABASE_PGVECTOR.md`).

All steps are **stateless** except the vector store, making the loop horizontally scalable. Detailed mathematical rationale lives in `docs/planning/KÄYTTÄJÄPROFIILI_JA_PALAUTEMEKANISMIN_TOTEUTUS.md`.

---
