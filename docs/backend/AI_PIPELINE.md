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
