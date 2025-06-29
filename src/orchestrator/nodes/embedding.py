"""EmbeddingNode implementation for LangGraph orchestrator.

This node uses OpenAI's text-embedding-ada-002 model to generate
vector embeddings for content. Since DeepSeek doesn't offer embedding models,
we use OpenAI which provides reliable embeddings at reasonable cost.
"""

import os
from typing import Optional, List
from datetime import datetime, timezone

from langchain_openai import OpenAIEmbeddings
from langsmith import traceable

from ..state import ContentState, update_state_status


class EmbeddingNode:
    """Node for generating vector embeddings using OpenAI API.
    
    This node takes content (preferring summary over raw content) and
    generates vector embeddings for similarity search and retrieval.
    """

    def __init__(
        self,
        model: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        max_tokens: int = 8191  # Max tokens for ada-002
    ):
        """Initialize the EmbeddingNode.
        
        Args:
            model: OpenAI embedding model to use
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if None)
            max_tokens: Maximum tokens to process (truncate if needed)
        """
        self.model = model
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.max_tokens = max_tokens
        
        # Store initialization parameters for lazy loading
        self._embeddings_kwargs = {
            "model": self.model,
            "api_key": self.api_key
        }
        self._embeddings = None

    @property
    def embeddings(self):
        """Lazy-load the embeddings to avoid API key validation during initialization."""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(**self._embeddings_kwargs)
        return self._embeddings

    @traceable(name="embedding_generator")
    def __call__(self, state: ContentState) -> ContentState:
        """Generate embeddings for the content in state.
        
        Args:
            state: ContentState containing summary or raw_content
            
        Returns:
            Updated ContentState with embeddings and updated status
        """
        try:
            # Get content to embed (prefer summary over raw content)
            content = state.get("summary") or state.get("raw_content", "")
            
            if not content or not content.strip():
                return update_state_status(
                    state,
                    status="error",
                    current_node="embedding",
                    error_message="No content available for embedding (content is empty or missing)"
                )
            
            # Truncate content if it's too long
            truncated_content = self._truncate_content(content)
            
            # Generate embeddings using OpenAI
            embedding_vector = self.embeddings.embed_query(truncated_content)
            
            # Update state with embeddings
            updated_state = state.copy()
            updated_state["embeddings"] = embedding_vector
            updated_state["status"] = "embedded"
            updated_state["current_node"] = "embedding"
            updated_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            return updated_state
            
        except Exception as e:
            return update_state_status(
                state,
                status="error",
                current_node="embedding",
                error_message=f"Embedding generation failed: {str(e)}"
            )

    def _truncate_content(self, content: str) -> str:
        """Truncate content to stay within token limits.
        
        Args:
            content: Content to potentially truncate
            
        Returns:
            Truncated content if necessary
        """
        # Rough estimate: 4 characters per token for English text
        estimated_tokens = len(content) // 4
        
        if estimated_tokens <= self.max_tokens:
            return content
        
        # Truncate to approximate token limit
        max_chars = self.max_tokens * 4
        truncated = content[:max_chars]
        
        # Try to truncate at a sentence boundary
        last_period = truncated.rfind('.')
        if last_period > max_chars * 0.8:  # Only if we don't lose too much content
            truncated = truncated[:last_period + 1]
        
        return truncated

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for this model.
        
        Returns:
            Embedding dimension (1536 for ada-002)
        """
        model_dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
        return model_dimensions.get(self.model, 1536) 