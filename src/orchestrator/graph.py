"""Orchestrator graph construction for InsightHub using LangGraph."""

from langgraph.graph import StateGraph, START, END
from src.orchestrator.state import ContentState
from src.orchestrator.nodes.content_fetcher import ContentFetcherNode
from src.orchestrator.nodes.summarizer import SummarizerNode
from src.orchestrator.nodes.embedding import EmbeddingNode
from src.orchestrator.nodes.content_scorer import ContentScorer
from src.orchestrator.nodes.storage import StorageNode
from src.orchestrator.nodes.error_handler import ErrorHandlerNode
from typing import Any

def create_orchestrator_graph() -> Any:
    """
    Construct and compile the orchestrator StateGraph for content processing.

    The graph routes ContentState through the following nodes:
      START -> content_fetcher -> summarizer -> embedding -> scorer -> storage -> END

    Returns:
        Compiled LangGraph graph object ready for invocation.
    """
    # Instantiate the graph with the ContentState schema
    builder = StateGraph(ContentState)

    # Add nodes (all must be callables)
    builder.add_node("content_fetcher", ContentFetcherNode())
    builder.add_node("summarizer", SummarizerNode())
    builder.add_node("embedding", EmbeddingNode())
    builder.add_node("scorer", ContentScorer())
    builder.add_node("storage", lambda state: StorageNode().store_content(state))
    builder.add_node("error_handler", ErrorHandlerNode())

    # Add edges for sequential processing
    builder.add_edge(START, "content_fetcher")
    builder.add_edge("content_fetcher", "summarizer")
    builder.add_edge("summarizer", "embedding")
    builder.add_edge("embedding", "scorer")
    builder.add_edge("scorer", "storage")
    builder.add_edge("storage", END)

    # Compile and return the graph
    return builder.compile() 