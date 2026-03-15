"""
Raccolta articoli con sistema di scoring per rilevanza — v2.
"""

import feedparser
from datetime import datetime, timezone, timedelta
from time import mktime
import re
import logging

from config import (
    RSS_FEEDS, HIGH_SIGNAL_KEYWORDS, LOW_SIGNAL_KEYWORDS,
    NOISE_KEYWORDS, MAX_ARTICLES, MAX_AGE_HOURS
)

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


def clean_html(text):
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500]


def compute_relevance_score(title, summary):
    """
    Calcola un punteggio di rilevanza per l'articolo.
    >= 3: molto rilevante (keyword ad alto segnale)
    1-2: probabilmente rilevante (keyword a basso segnale)
    0: non rilevante
    -10: rumore (da escludere)
    """
    text = f"{title} {summary}".lower()

    # Prima controlla se è rumore
    for noise in NOISE_KEYWORDS:
        if noise.lower() in text:
            return -10

    score = 0

    # Keyword ad alto segnale: +3 ciascuna (max contate una volta)
    for kw in HIGH_SIGNAL_KEYWORDS:
        if kw.lower() in text:
            score += 3

    # Keyword a basso segnale: +1 ciascuna
    for kw in LOW_SIGNAL_KEYWORDS:
        if kw.lower() in text:
            score += 1

    # Bonus per titoli corti e incisivi (tipici di breaking news)
    if len(title.split()) <= 12:
        score += 1

    return score


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

            score = compute_relevance_score(title, summary)

            # Scarta rumore e articoli non rilevanti
            if score < 1:
                continue

            articles.append({
                "title": title,
                "summary": summary,
                "link": link,
                "source": feed_info["name"],
                "category": feed_info["category"],
                "published": pub_date.isoformat() if pub_date else None,
                "score": score,
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
        logger.info(f"  → {len(articles)} articoli rilevanti")

    # Deduplica per titolo normalizzato
    seen = set()
    unique = []
    for art in all_articles:
        key = art["title"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(art)

    # Ordina per score (più rilevanti prima), poi per data
    unique.sort(key=lambda x: (x["score"], x["published"] or "0000"), reverse=True)

    result = unique[:MAX_ARTICLES]
    logger.info(
        f"Totale: {len(all_articles)}, unici: {len(unique)}, "
        f"selezionati: {len(result)}, "
        f"score range: {result[-1]['score'] if result else 0}-{result[0]['score'] if result else 0}"
    )
    return result
