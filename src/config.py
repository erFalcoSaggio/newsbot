"""
Configurazione fonti RSS e parametri del bot — v2.
"""

# Fonti RSS — solo le migliori, niente fuffa
RSS_FEEDS = [
    # --- AI (fonti primarie, non aggregatori) ---
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "AI"},
    {"name": "Anthropic Blog", "url": "https://www.anthropic.com/rss.xml", "category": "AI"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "category": "AI"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "category": "AI"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "category": "AI"},

    # --- Tech ---
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "Tech"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "Tech"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "Tech"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage?points=100", "category": "Tech"},

    # --- Startup & VC ---
    {"name": "Y Combinator", "url": "https://www.ycombinator.com/blog/rss/", "category": "Startup"},
    {"name": "a16z", "url": "https://a16z.com/feed/", "category": "Startup"},
]

# Keyword ad alto segnale — se presenti, l'articolo è quasi sicuramente rilevante
HIGH_SIGNAL_KEYWORDS = [
    # AI core
    "artificial intelligence", "machine learning", "deep learning",
    "large language model", "llm", "gpt", "claude", "gemini", "llama",
    "openai", "anthropic", "deepmind", "mistral", "hugging face",
    "neural network", "transformer", "diffusion model", "agi",
    "ai agent", "ai safety", "rlhf", "fine-tuning", "open source ai",
    "text-to-image", "text-to-video", "multimodal",

    # Startup / funding
    "series a", "series b", "series c", "seed round", "funding round",
    "raised", "valuation", "unicorn", "ipo", "acquisition", "acqui-hire",
    "y combinator", "a16z", "sequoia", "benchmark",

    # Hardware / infra AI
    "nvidia", "gpu", "tpu", "semiconductor", "chip", "cuda",
    "data center", "inference", "training run",
]

# Keyword a basso segnale — da sole non bastano, servono in combinazione
LOW_SIGNAL_KEYWORDS = [
    "google", "apple", "microsoft", "meta", "amazon", "tesla",
    "startup", "developer", "api", "cloud", "saas", "robotics",
    "quantum", "open source", "automation", "copilot",
]

# Parole che indicano articoli di bassa qualità (listicle, opinioni vuote, ecc.)
NOISE_KEYWORDS = [
    "best apps", "tips and tricks", "how to watch", "deal alert",
    "sale today", "coupon", "giveaway", "unboxing", "review score",
    "top 10", "top 5", "gift guide", "black friday", "prime day",
    "daily crunch",  # TechCrunch newsletter recap, ridondante
]

# Articoli da includere nel digest
MAX_ARTICLES = 12

# Freschezza massima (ore)
MAX_AGE_HOURS = 26
