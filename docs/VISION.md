# VISION

## Current State
- **Reddit URL Fetcher**: The software currently fetches URLs from Reddit, likely based on specific criteria such as subreddit, post type, or keywords. This functionality is useful for aggregating content from Reddit for analysis, monitoring, or content curation.

## Implementation Plan

### Phase 1: Core Reddit Integration
1. **Basic Streamlit Frontend** ✅
   - Setup Streamlit app structure
   - Basic subreddit input and fetch functionality
   - Simple list view of results

2. **Enhanced Reddit Features** 🚀
   - Multiple view modes (List/Detailed)
   - Advanced filtering capabilities: (Supports **Selective Exposure**)
     - By subreddit
     - By score threshold
     - By post date range
   - Sorting options: (Supports **Selective Exposure**)
     - By score
     - By date
     - By relevance
   - Batch selection tools
   - Export functionality improvements

3. **Data Management** 📊
   - Session state management
   - Caching for performance
   - Error handling and user feedback
   - Export format standardization

### Phase 2: YouTube Integration
1.  **YouTube Data API Integration**
    *   Obtain YouTube Data API v3 key.
    *   Implement secure API key management (e.g., environment variables).
    *   Install Google API client library (`google-api-python-client`).
    *   Create `youtube_client.py` module.
    *   Implement function to fetch latest 'X' videos per channel ID:
        *   Authenticate using API key.
        *   Find channel's 'uploads' playlist ID.
        *   Query 'playlistItems' for latest videos.
        *   Extract title, URL, publication date.
        *   Include error handling.

2.  **UI Extensions**
    *   Add Streamlit input for YouTube channel IDs.
    *   Add Streamlit input for number of videos 'X'.
    *   Add "Fetch YouTube Videos" button.
    *   Display fetched videos (title, link, date).
    *   Implement checkbox selection for videos.
    *   Store selected video URLs in session state.

3.  **Combined Features**
    *   Modify selection/export logic to handle both Reddit and YouTube URLs.
    *   Ensure downstream processes handle combined list.
    *   Add UI feedback (loading indicators).
    *   Consider API result caching.

### Phase 3: Advanced Features
1. **Content Organization**
   - Tagging system (Supports **Chunking/Structuring**)
   - Custom categories (Supports **Chunking/Structuring**)
   - Smart collections
   - Search history (Supports **Spaced Repetition/Retrieval**)

2. **Analytics Dashboard**
   - Content source statistics
   - User interaction metrics
   - Trend visualization
   - Impact scoring

3. **Export and Integration**
   - Multiple export formats
   - NotebookLM integration
   - **Prompt Creator for NotebookLM/Summarization**: Develop a tool to generate customized prompts for LLMs based on selected subcategory sources. These prompts will define the structure (e.g., podcast script, bullet points), tone, and focus of the desired summary output from the selected content. (Supports **Active Processing**)
   - **NotebookLM Podcast Prompt Generator**: Build a Streamlit-based tool that enables users to generate concise, category/topic-specific AI prompts for NotebookLM Audio Overview. The user can select topic, tone, target audience, structure, and length preferences. The tool ensures the prompt stays within the 500 character limit and helps guide the AI podcast generation process based on selected Reddit/YouTube URLs. Enables highly personalized, high-quality AI podcasts directly from the aggregated content.
   - API endpoint for external tools
   - Backup/restore functionality

### Phase 4: AI Enhancement
1. **Content Processing**
   - **Content Extraction**: Implement logic to fetch core content from selected URLs (articles, potentially video transcripts).
   - LLM-based content summarization (using the Prompt Creator from Phase 3). (Supports **Active Processing**)
   - Automatic categorization (Supports **Chunking/Structuring**)
   - Relevance scoring (Supports **Selective Exposure**)
   - Topic extraction

2. **Smart Features**
   - Content recommendations
   - Similar content discovery
   - Trending topic detection
   - User preference learning

3. **Knowledge Management**
   - Mind map generation (Supports **Chunking/Structuring**)
   - Knowledge graph visualization
   - Learning path suggestions
   - Progress tracking

### Technical Requirements
1. **Frontend**
   - Streamlit for main interface
   - Plotly for visualizations
   - Custom CSS for styling
   - Responsive design

2. **Backend**
   - FastAPI for API endpoints
   - Redis for caching
   - SQLAlchemy for data persistence
   - Background job processing

3. **Infrastructure**
   - Docker containerization
   - GitHub Actions CI/CD
   - Monitoring and logging
   - Security best practices

### Quality Assurance
1. **Testing Strategy**
   - Unit tests for core functionality
   - Integration tests for API
   - End-to-end testing
   - Performance benchmarking

2. **Documentation**
   - API documentation
   - User guides
   - Development setup guide
   - Contribution guidelines

## Future Vision
- **Streamlit Frontend for Interactive Control**: Develop a web-based user interface using Streamlit. This frontend will allow users to:
    - Configure and trigger the fetching of content from various sources (Reddit, YouTube, RSS, websites, etc.).
    - Review, filter, sort, and select specific content items for summarization.
    - Define summarization parameters using the Prompt Creator.
    - View and export the generated summary.
    - Compile a unified list of selected URLs for further processing.
- **Expanded Source Integration**: Add support for more content sources like RSS feeds, specific websites, Twitter lists, Hacker News, etc.
- **YouTube Integration**: Expand the software to include YouTube as a source. This would involve fetching URLs for new videos from specific YouTubers or categories over a defined period. This feature would allow users to track video content trends, monitor specific channels, or gather data for content analysis.
- **User Preferences and Priority Matrix**: Enhance the software by allowing users to specify their interests and priorities. Implement a priority matrix to categorize content based on urgency and importance, tailored to user preferences. Consider using a large language model (LLM) for impact assessment to determine the relevance and potential impact of content based on user-defined criteria.
- **Seniority Levels**: Introduce categorization of content based on different seniority levels like beginner, medior, and senior. This will help tailor the relevance of news and information to the user's experience level, ensuring that the content is appropriately challenging and informative.
- **Weekly Implementation Suggestion**: Instead of a fixed 1-hour project, provide a weekly suggestion on how to implement the information gained. This could be a project, a new tool to explore, or a technique to try. The goal is to encourage users to apply the information in a practical context, fostering continuous learning and engagement.
- **AI Podcasts from Top Sources**: Currently, AI podcasts are built based on one subreddit. Expand this feature to create podcasts using the ranked top 50 information sources per category. This approach will provide a broader and more diverse range of content, enhancing the podcast's value and appeal to a wider audience.
- **Highest Impact of the Week Podcast**: Create a podcast focusing on the top priority news sources only. This "Highest Impact of the Week" podcast will highlight the most significant and impactful information, providing users with a concise and valuable summary of the week's most important developments.
- **Text-to-Speech (TTS) Integration**: Add functionality to convert the generated summary/script into an actual audio file (podcast).
- **Mind Maps for Information Categories**: Implement the ability to create mind maps for each information category. This will help users visualize and organize content within specific areas of interest.
- **Mind Maps for Highest Impact Sources**: Create mind maps specifically for the curated highest impact of the week information sources. This will provide users with a visual representation of the most significant content, aiding in understanding and retention.
- **Enhanced Mind Maps with LLMs**: Utilize powerful large language models (LLMs) to enhance mind maps by providing additional context and a broader perspective. This will allow users to gain a deeper understanding and see the bigger picture, beyond the restricted news sources in NotebookLM.
- **Dynamic Knowledge Profile**: Use an LLM to analyze the content the user consumes and interacts with (clicks, time spent, feedback on weekly suggestions). Map this to an internal graph of concepts relevant to their field (e.g., data engineering) to build a dynamic user knowledge profile for deeper personalization. (Supports **Contextualization/Elaboration**)
- **Hyper-Personalized Relevance**: Leverage the dynamic knowledge profile to tailor content recommendations and summaries, connecting new information to the user's existing knowledge base. (Supports **Contextualization/Elaboration**)