# VISION

## Current State
- **Reddit URL Fetcher**: The software currently fetches URLs from Reddit, likely based on specific criteria such as subreddit, post type, or keywords. This functionality is useful for aggregating content from Reddit for analysis, monitoring, or content curation.

## Future Vision
- **Streamlit Frontend for Interactive Control**: Develop a web-based user interface using Streamlit. This frontend will allow users to:
    - Configure and trigger the fetching of top threads from specified subreddits within a defined time range.
    - Fetch the titles of the latest 'X' videos from specified YouTube channels.
    - Select specific Reddit threads and YouTube videos from the fetched lists.
    - Compile a unified list of selected URLs (from both Reddit and YouTube) for further processing (e.g., uploading to NotebookLM or other analysis).
- **YouTube Integration**: Expand the software to include YouTube as a source. This would involve fetching URLs for new videos from specific YouTubers or categories over a defined period. This feature would allow users to track video content trends, monitor specific channels, or gather data for content analysis.
- **User Preferences and Priority Matrix**: Enhance the software by allowing users to specify their interests and priorities. Implement a priority matrix to categorize content based on urgency and importance, tailored to user preferences. Consider using a large language model (LLM) for impact assessment to determine the relevance and potential impact of content based on user-defined criteria.
- **Seniority Levels**: Introduce categorization of content based on different seniority levels like beginner, medior, and senior. This will help tailor the relevance of news and information to the user's experience level, ensuring that the content is appropriately challenging and informative.
- **Weekly Implementation Suggestion**: Instead of a fixed 1-hour project, provide a weekly suggestion on how to implement the information gained. This could be a project, a new tool to explore, or a technique to try. The goal is to encourage users to apply the information in a practical context, fostering continuous learning and engagement.
- **AI Podcasts from Top Sources**: Currently, AI podcasts are built based on one subreddit. Expand this feature to create podcasts using the ranked top 50 information sources per category. This approach will provide a broader and more diverse range of content, enhancing the podcast's value and appeal to a wider audience.
- **Highest Impact of the Week Podcast**: Create a podcast focusing on the top priority news sources only. This "Highest Impact of the Week" podcast will highlight the most significant and impactful information, providing users with a concise and valuable summary of the week's most important developments.
- **Mind Maps for Information Categories**: Implement the ability to create mind maps for each information category. This will help users visualize and organize content within specific areas of interest.
- **Mind Maps for Highest Impact Sources**: Create mind maps specifically for the curated highest impact of the week information sources. This will provide users with a visual representation of the most significant content, aiding in understanding and retention.
- **Enhanced Mind Maps with LLMs**: Utilize powerful large language models (LLMs) to enhance mind maps by providing additional context and a broader perspective. This will allow users to gain a deeper understanding and see the bigger picture, beyond the restricted news sources in NotebookLM.
- **Dynamic Knowledge Profile**: Use an LLM to analyze the content the user consumes and interacts with (clicks, time spent, feedback on weekly suggestions). Map this to an internal graph of concepts relevant to their field (e.g., data engineering) to build a dynamic user knowledge profile for deeper personalization.
- **Knowledge Landscape Mind Maps**: Enhance mind maps to not only show connections within known topics but also to highlight adjacent, relevant topics the user hasn't engaged with yet. This helps mitigate the Dunning-Kruger effect by visualizing the broader knowledge landscape and revealing "unknown unknowns."
- **Narrative Framing**: Utilize LLMs to structure key insights and summaries within narrative formats. Frame information as stories (e.g., development journey of a tool, challenge overcome, future impact) to improve engagement and memorability over dry facts.
- **Hyper-Personalized Relevance**: Enhance content relevance by directly connecting information to the user's specific context using their dynamic knowledge profile. This includes:
    - Judicious use of the user's name in summaries or intros.
    - Creating analogies linking technical concepts to the user's stated hobbies or interests.
    - Explicitly framing insights around how they address the user's goals, problems, or knowledge gaps (the "What's In It For Me?").