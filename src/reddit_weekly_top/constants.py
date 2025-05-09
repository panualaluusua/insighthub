"""Constants and configurations for the application."""

# Category Definitions
SUBREDDIT_CATEGORIES = {
    "AI Coding": [
        "ChatGPTCoding", "ClaudeAI", "cursor", "LLMDevs", "LocalLLaMA", "MLEngineering", "ollama", "AI_Agents"
    ],
    "AI Tools and Workflows": [
        "n8n", "databricks", "LangChain", "mcp", "notebooklm"
    ],
    "Career & Entrepreneurship": [
        "consulting", "ExperiencedDevs", "DataEngineering", "microsaas", "SideProject", "IndieHackers"
    ],
    "Productivity": [
        "productivity", "automation", "LifeProTips", "digitalminimalism", "DIY", "dataisbeautiful", "analytics", "longevity", "instant_regret", "instantkarma"
    ],
    "Cycling / Outdoors": [
        "bicycletouring", "bicycling", "BicyclingCirclejerk", "bikepacking", "cycling", 
        "gravelcycling", "Justridingalong", "mountainbiking", "MTB", "randonneuring", 
        "trailrunning", "Ultralight", "Velo", "xcmtb", "xcountryskiing", "Zwift", 
        "bouldering", "HikerTrashMemes", "running", "RunningCirclejerk", "EarthPorn", 
        "landscaping"
    ],
    "Finance / Economics": [
        "Economics", "eupersonalfinance", "finance", "FinOps", "MiddleClassFinance", 
        "Omatalous", "wallstreetbets"
    ],
    "Gaming": [
        "Amd", "aoe4", "eu4", "XboxGamePass"
    ],
    "News / World": [
        "announcements", "europe", "worldnews", "UkraineWarVideoReport", "UkrainianConflict"
    ],
    "Finland Specific": [
        "arkisuomi", "Oulu", "Suomi"
    ],
    "Miscellaneous / Humor / Life": [
        "automation", "CameraObscura", "consulting", "daddit", "darknetdiaries", 
        "digitalminimalism", "DIY", "greentext", "instant_regret", "instantkarma", 
        "KidsAreFuckingStupid", "LifeProTips", "longevity", "MapPorn", "mildlyinteresting", 
        "notebooklm", "productivity", "Showerthoughts", "starterpacks", "tragedeigh", 
        "trashy", "Udemy", "WatchPeopleDieInside", "Whatcouldgowrong"
    ]
}

# Add an "All" category that includes all unique subreddits from other categories
all_subs = set()
for subs in SUBREDDIT_CATEGORIES.values():
    all_subs.update(subs)
SUBREDDIT_CATEGORIES["All"] = sorted(list(all_subs))

# Podcast/AI prompt presets
DEFAULT_PODCAST_PROMPTS = [
    # 1. Provided by user
    """Data Engineer's Deep Dive After Dark (18+)
Reference talked Reddit topics
FOCUS: AI in data eng, dev tools, AI coding, real-world apps, top comments, \"Fuck It, Make It a Product\"-segment, Perkele Power Move-segment: Best AI Hack, Create business ideas,
STYLE: Raw, unhinged, hilarious, Terry Crews vibe. No corporate BS, no censorship—just pure, no-filter tech talk. Swearing encouraged (esp. fuck/shit), Chaotic Tangent Binge.
RULES: No repetition, no fluff, no \"exactly.\"
LENGTH: 30–60 min.""",

    # 2. Inspired by podcast_prompt.md and popular tech podcasts
    """AI News Weekly Roundup
Summarize and discuss this week's most upvoted AI, ML, and data engineering Reddit posts.
FOCUS: Break down trends, highlight top discussions, and share actionable insights for practitioners.
STYLE: Conversational, insightful, and fast-paced. Mix expert commentary with humor.
LENGTH: 20–30 min.""",

    # 3. Classic “Joe Rogan Style” deep dive
    """Joe Rogan Style Deep Dive
Imitate Joe Rogan’s podcast style: long-form, unscripted, curious, and open-minded.
FOCUS: Explore the most controversial or thought-provoking Reddit topics in tech and AI.
STYLE: Relaxed, tangential, and personal stories encouraged. Let the conversation flow naturally.
LENGTH: 60–90 min.""",

    # 4. Beginner-friendly explainer
    """Beginner’s Guide to Data Engineering
Explain the week’s top Reddit posts as if to a beginner or new grad.
FOCUS: Define terms, break down jargon, and give real-world analogies.
STYLE: Simple, friendly, and supportive. Avoid technical jargon unless explained.
LENGTH: 15–20 min.""",

    # 5. “Productivity Power Hour”
    """Productivity Power Hour
Highlight the best dev tools, workflow hacks, and AI-powered productivity tips from Reddit and YouTube.
FOCUS: Actionable advice, tool recommendations, and time-saving strategies.
STYLE: Energetic, motivational, and practical.
LENGTH: 10–15 min.""",

    # --- Category-specific, insight-driven prompts ---
    """AI Coding Weekly Synthesis
Synthesize the most innovative coding techniques, code snippets, and workflow hacks from this week’s top posts in AI coding subreddits (e.g., ChatGPTCoding, ClaudeAI, cursor, LLMDevs). Focus on practical implementations, clever prompt engineering, and real-world debugging stories. Highlight at least one breakthrough or controversial thread and explain its significance for working AI developers.
""",

    """AI Tools & Workflows Deep Dive
Curate and analyze the most impactful tools, libraries, and workflow automations discussed in the AI tools and workflows subreddits (e.g., n8n, databricks, LangChain, mcp, notebooklm). Explain how these tools are changing day-to-day AI work. Compare community opinions, share actionable setup tips, and spotlight a tool or workflow that could save listeners hours this month.
""",

    """Career & Entrepreneurship Power Moves
Extract the top insights, career moves, and entrepreneurial lessons from the week’s most upvoted posts in consulting, ExperiencedDevs, DataEngineering, microsaas, SideProject, and IndieHackers. Focus on actionable career advice, startup pitfalls, and real user stories. Include a ‘Power Move of the Week’—the most creative or bold career/entrepreneurial action found in the threads.
""",

    """Productivity & Life Hacks Roundup
Distill the most effective productivity strategies, automation tips, and life hacks from this week’s trending posts in productivity, automation, LifeProTips, digitalminimalism, and related subreddits. Highlight new tools, routines, or mindsets that listeners can implement immediately. End with a rapid-fire segment of the three most upvoted unconventional productivity hacks.
""",
]

