import pytest
from typing import Any

# Import the function to test (will fail until implemented)
from src.orchestrator.graph import create_orchestrator_graph

# LangGraph imports
from langgraph.graph import START, END

REQUIRED_NODES = {"content_fetcher", "summarizer", "embedding", "storage"}
REQUIRED_EDGES = [
    ("__start__", "content_fetcher"),
    ("content_fetcher", "summarizer"),
    ("summarizer", "embedding"),
    ("embedding", "storage"),
    ("storage", "__end__"),
]

def test_orchestrator_graph_structure():
    """Test that the orchestrator graph contains all required nodes and edges."""
    graph = create_orchestrator_graph()
    g = graph.get_graph()  # Get the underlying graph object

    # Check nodes
    node_names = set(g.nodes)
    for node in REQUIRED_NODES:
        assert node in node_names, f"Missing node: {node}"

    # Check edges - LangGraph edges are Edge objects with source and target attributes
    edge_names = set((edge.source, edge.target) for edge in g.edges)
    for src, dst in REQUIRED_EDGES:
        assert (src, dst) in edge_names, f"Missing edge: {src} -> {dst}"

    # Optionally: test end-to-end invocation with a mock state (skipped for now)
    # TODO: Add end-to-end test once implementation is ready 