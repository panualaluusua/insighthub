"""Utility functions for the application."""

from typing import List, Dict
import streamlit as st

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'selected_posts' not in st.session_state:
        st.session_state.selected_posts = set()
    if 'all_posts' not in st.session_state:
        st.session_state.all_posts = []
    if 'copied_text' not in st.session_state:
        st.session_state.copied_text = ""
    if 'youtube_videos' not in st.session_state:
        st.session_state.youtube_videos = []
    if 'youtube_copied_text' not in st.session_state:
        st.session_state.youtube_copied_text = ""
    if 'generated_ai_prompt' not in st.session_state:
        st.session_state.generated_ai_prompt = ""

def generate_podcast_prompt(
    category: str,
    tone: str,
    audience: str,
    structure: str,
    length: str,
    keywords: str
) -> str:
    """Generate a podcast prompt for NotebookLM.
    
    Args:
        category: Topic category
        tone: Tone of the podcast
        audience: Target audience
        structure: Structure of the podcast
        length: Desired length
        keywords: Optional keywords/focus
        
    Returns:
        Formatted podcast prompt
    """
    context_parts = []
    if category:
        context_parts.append(f"Aihe: {category}.")
    if tone:
        context_parts.append(f"Äänensävy: {tone}.")
    if audience:
        context_parts.append(f"Kohdeyleisö: {audience}.")
    if structure:
        context_parts.append(f"Rakenne: {structure}.")
    if length:
        context_parts.append(f"Pituus: {length}.")
    if keywords:
        focus_text = keywords.replace('"', "'").replace('\n', ' ').replace('\r', ' ').strip()[:100]
        context_parts.append(f"Fokus: {focus_text}.")
    
    context = " ".join(context_parts)
    final_prompt = f"Task: Luo podcast. {context} Output: Podcast-skripti. CRITICAL: Käytä VAIN annettuja lähde-URL:eja."
    
    # Truncate if too long
    if len(final_prompt) > 500:
        final_prompt = final_prompt[:497] + "..."
    
    return final_prompt
