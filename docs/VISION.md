# VISION

## Tulevaisuuden visio
Visiona on, että voimme hakea useista eri tietolähteistä meille relevantit uutiset ja sisällöt. Tämän jälkeen AI-agentti kuratoi ja pisteyttää lähteet sen perusteella, kuinka relevantteja ne ovat käyttäjän taustaan, projekteihin, työhön ja kiinnostuksen kohteisiin nähden. Lopuksi esittelemme sisällöt helposti omaksuttavassa muodossa – esimerkiksi Redditin tai Jodelin kaltaisena virtana.

## Current State
InsightHubin nykyiset toiminnot:

- **Reddit-integraatio:**
    - Käyttäjä voi valita subreddit-kategorian ja aikavälin (viikko/kuukausi).
    - Sovellus hakee valitun määrän suosituimpia postauksia useista alikategorioista Redditin public API:n kautta.
    - Tulokset näytetään listana (otsikko, linkki, score).
    - Postaukset voidaan kopioida yhdellä napilla (URL-listana).

- **YouTube-integraatio:**
    - Käyttäjä voi syöttää kanavien nimet ja halutun videomäärän.
    - Sovellus hakee uusimmat videot jokaiselta kanavalta (otsikko, linkki, kanavan nimi).
    - Videot näytetään listana ja niiden URL:t voi kopioida yhdellä napilla.

- **UI ja käyttökokemus:**
    - Streamlit-pohjainen käyttöliittymä, jossa on selkeät syötekentät ja valinnat.
    - Käyttäjä voi helposti selata, valita ja kopioida Reddit- ja YouTube-linkkejä jatkokäyttöä varten.
    - Oletus-podcast-promptien valinta ja esikatselu.
    - Virheiden ja puuttuvien API-avainten käsittely sekä käyttäjäystävälliset varoitukset.

## Implementation Plan

### Phase 1: Core Reddit Integration
1. **Basic Streamlit Frontend** 
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




- **Highest Impact of the Week Podcast**: Create a podcast focusing on the top priority news sources only. This "Highest Impact of the Week" podcast will highlight the most significant and impactful information, providing users with a concise and valuable summary of the week's most important developments.
- **Text-to-Speech (TTS) Integration**: Add functionality to convert the generated summary/script into an actual audio file (podcast).
- **Mind Maps for Information Categories**: Implement the ability to create mind maps for each information category. This will help users visualize and organize content within specific areas of interest.
- **Mind Maps for Highest Impact Sources**: Create mind maps specifically for the curated highest impact of the week information sources. This will provide users with a visual representation of the most significant content, aiding in understanding and retention.
- **Dynamic Knowledge Profile**: Use an LLM to analyze the content the user consumes and interacts with (clicks, time spent, feedback on weekly suggestions). Map this to an internal graph of concepts relevant to their field (e.g., data engineering) to build a dynamic user knowledge profile for deeper personalization. (Supports **Contextualization/Elaboration**)
- **Hyper-Personalized Relevance**: Leverage the dynamic knowledge profile to tailor content recommendations and summaries, connecting new information to the user's existing knowledge base. (Supports **Contextualization/Elaboration**)