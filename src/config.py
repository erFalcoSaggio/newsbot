"""
Configurazione fonti RSS e parametri del bot.
"""

RSS_FEEDS = [
    # --- AI & Machine Learning ---
    {"name": "MIT Technology Review - AI", "url": "https://www.technologyreview.com/feed/", "category": "AI"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "AI"},
    {"name": "Anthropic Blog", "url": "https://www.anthropic.com/rss.xml", "category": "AI"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "category": "AI"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "category": "AI"},

    # --- Tech ---
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "Tech"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "Tech"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "Tech"},
    {"name": "Hacker News (Top)", "url": "https://hnrss.org/frontpage", "category": "Tech"},

    # --- Startup & VC ---
    {"name": "Y Combinator Blog", "url": "https://www.ycombinator.com/blog/rss/", "category": "Startup"},
    {"name": "a16z Blog", "url": "https://a16z.com/feed/", "category": "Startup"},
]

RELEVANCE_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "gpt", "claude", "gemini", "openai", "anthropic", "google ai",
    "neural", "transformer", "diffusion", "autonomous",
    "startup", "funding", "seed", "series a", "series b", "vc",
    "venture capital", "acquisition", "ipo", "valuation",
    "open source", "developer", "api", "cloud", "saas",
    "robotics", "quantum", "chip", "semiconductor", "nvidia", "apple",
    "microsoft", "meta", "google", "amazon",
]

MAX_ARTICLES = 15
MAX_AGE_HOURS = 28
