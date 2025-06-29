"""SummarizerNode implementation for LangGraph orchestrator.

This node uses DeepSeek API via LangChain to generate content summaries.
DeepSeek offers excellent value at $0.27 input / $1.10 output per 1M tokens
with 50% discount during off-peak hours.
"""

import os
from typing import Optional
from datetime import datetime, timezone

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langsmith import traceable

from ..state import ContentState, update_state_status


class SummarizerNode:
    """Node for generating content summaries using DeepSeek API.
    
    This node takes raw content or processed content and generates
    concise, informative summaries using DeepSeek's chat model.
    """

    def __init__(
        self,
        model: str = "deepseek-chat",
        api_key: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.3
    ):
        """Initialize the SummarizerNode.
        
        Args:
            model: DeepSeek model to use (deepseek-chat or deepseek-reasoner)
            api_key: DeepSeek API key (uses DEEPSEEK_API_KEY env var if None)
            max_tokens: Maximum tokens to generate (uses model default if None)
            temperature: Sampling temperature for generation
        """
        self.model = model
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Store initialization parameters for lazy loading
        self._llm_kwargs = {
            "model": self.model,
            "base_url": "https://api.deepseek.com/v1",
            "api_key": self.api_key,
            "temperature": self.temperature
        }
        
        if self.max_tokens:
            self._llm_kwargs["max_tokens"] = self.max_tokens
            
        self._llm = None

    @property
    def llm(self):
        """Lazy-load the LLM to avoid API key validation during initialization."""
        if self._llm is None:
            self._llm = ChatOpenAI(**self._llm_kwargs)
        return self._llm

    @traceable(name="content_summarizer")
    def __call__(self, state: ContentState) -> ContentState:
        """Generate summary for the content in state.
        
        Args:
            state: ContentState containing raw_content or processed_content
            
        Returns:
            Updated ContentState with summary and updated status
        """
        try:
            # Get content to summarize (prefer processed over raw)
            content = state.get("processed_content") or state.get("raw_content", "")
            
            if not content or not content.strip():
                return update_state_status(
                    state,
                    status="error",
                    current_node="summarizer",
                    error_message="No content available for summarization (content is empty)"
                )
            
            # Create appropriate prompt based on source type and content length
            prompt = self._create_summary_prompt(state, content)
            
            # Generate summary using DeepSeek
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            
            # Update state with summary
            updated_state = state.copy()
            updated_state["summary"] = response.content
            updated_state["status"] = "summarized"
            updated_state["current_node"] = "summarizer"
            updated_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            return updated_state
            
        except Exception as e:
            return update_state_status(
                state,
                status="error",
                current_node="summarizer",
                error_message=f"Summarization failed: {str(e)}"
            )

    def _create_summary_prompt(self, state: ContentState, content: str) -> str:
        """Create an appropriate summarization prompt based on content type and length.
        
        Args:
            state: ContentState for context
            content: Content to summarize
            
        Returns:
            Formatted prompt string
        """
        source_type = state.get("source_type", "unknown")
        content_length = len(content)
        
        # Base instructions
        base_instruction = (
            "Generate a concise, informative summary of the following content. "
            "Focus on key points, main ideas, and actionable insights. "
        )
        
        # Adjust instructions based on source type
        if source_type == "youtube":
            base_instruction += (
                "This is a YouTube video transcript. Identify the main topic, "
                "key learnings, and any recommendations or conclusions. "
            )
        elif source_type == "reddit":
            base_instruction += (
                "This is Reddit content. Capture the main discussion points, "
                "popular opinions, and key insights from the community. "
            )
        
        # Adjust summary length based on content length
        if content_length > 10000:
            length_instruction = "Provide a comprehensive summary in 3-4 paragraphs."
        elif content_length > 5000:
            length_instruction = "Provide a detailed summary in 2-3 paragraphs."
        elif content_length > 1000:
            length_instruction = "Provide a concise summary in 1-2 paragraphs."
        else:
            length_instruction = "Provide a brief summary in 1 paragraph."
        
        # Combine instructions with content
        full_prompt = f"""
{base_instruction}
{length_instruction}

Content to summarize:
{content}

Summary:"""
        
        return full_prompt 