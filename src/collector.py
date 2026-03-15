"""
Raccolta articoli da feed RSS con filtraggio per rilevanza e freschezza.
"""

import feedparser
from datetime import datetime, timezone, timedelta
from time import mktime
import re
import logging

from config import RSS_FEEDS, RELEVANCE_KEYWORDS, MAX_ARTICLES, MAX_AGE_HOURS

logger = logging.getLogger(__name__)


def parse_published_date(entry):
    for date_field in ["published_parsed", "updated_parsed"]:
        parsed = getattr(entry, date_field, None) or entry.get(date_field)
        if parsed:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except (ValueError, OverflowError):
                continue
    return None


def is_recent(pub_date, max_hours):
    if not pub_date:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_hours)
    return pub_date >= cutoff


def is_relevant(title, summary, keywords):
    if not keywords:
        return True
    text = f"{title} {summary}".lower()
    return any(kw.lower() in text for kw in keywords)


def clean_html(text):
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500]


def fetch_feed(feed_info):
    articles = []
    try:
        feed = feedparser.parse(feed_info["url"])
        if feed.bozo and not feed.entries:
            logger.warning(f"Feed non valido: {feed_info['name']}")
            return []

        for entry in feed.entries:
            pub_date = parse_published_date(entry)
            if not is_recent(pub_date, MAX_AGE_HOURS):
                continue

            title = entry.get("title", "").strip()
            summary = clean_html(entry.get("summary", ""))
            link = entry.get("link", "")

            if not title:
                continue
            if not is_relevant(title, summary, RELEVANCE_KEYWORDS):
                continue

            articles.append({
                "title": title,
                "summary": summary,
                "link": link,
                "source": feed_info["name"],
                "category": feed_info["category"],
                "published": pub_date.isoformat() if pub_date else None,
            })
    except Exception as e:
        logger.error(f"Errore nel fetch di {feed_info['name']}: {e}")
    return articles


def collect_all():
    all_articles = []
    for feed_info in RSS_FEEDS:
        logger.info(f"Fetching: {feed_info['name']}...")
        articles = fetch_feed(feed_info)
        all_articles.extend(articles)
        logger.info(f"  → {len(articles)} articoli trovati")

    seen_titles = set()
    unique = []
    for art in all_articles:
        normalized = art["title"].lower().strip()
        if normalized not in seen_titles:
            seen_titles.add(normalized)
            unique.append(art)

    unique.sort(key=lambda x: x["published"] or "0000", reverse=True)
    result = unique[:MAX_ARTICLES]
    logger.info(f"Totale: {len(all_articles)}, unici: {len(unique)}, selezionati: {len(result)}")
    return result
