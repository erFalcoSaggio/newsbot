"""
Sintesi degli articoli tramite Gemini API (free tier).
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

SYSTEM_PROMPT = """Sei un giornalista tech italiano esperto di AI, startup e tecnologia.

Ti verrà fornita una lista di articoli con titolo, fonte e breve descrizione.
Il tuo compito è creare un DIGEST GIORNALIERO in italiano, seguendo queste regole:

1. Raggruppa le notizie per tema (AI, Startup/Funding, Tech)
2. Per ogni notizia scrivi 1-2 frasi di riassunto chiare e informative
3. Usa un tono professionale ma accessibile
4. Evidenzia perché la notizia è rilevante
5. Se ci sono connessioni tra notizie diverse, segnalale

FORMATO OUTPUT:

🤖 *AI & Machine Learning*
- [riassunto notizia] — _fonte_

🚀 *Startup & Funding*
- [riassunto notizia] — _fonte_

💻 *Tech*
- [riassunto notizia] — _fonte_

Se una categoria non ha notizie, omettila.
Alla fine aggiungi una riga con il conteggio totale delle notizie.
Usa il formato Markdown compatibile con Telegram."""


def build_articles_text(articles):
    lines = []
    for i, art in enumerate(articles, 1):
        lines.append(
            f"{i}. [{art['category']}] {art['title']}\n"
            f"   Fonte: {art['source']}\n"
            f"   Descrizione: {art['summary'][:300]}\n"
            f"   Link: {art['link']}"
        )
    return "\n\n".join(lines)


def summarize(articles):
    if not articles:
        return "📭 Nessuna notizia rilevante trovata oggi."

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY non configurata")
        return fallback_digest(articles)

    articles_text = build_articles_text(articles)
    prompt = f"{SYSTEM_PROMPT}\n\n--- ARTICOLI DI OGGI ---\n\n{articles_text}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
    }

    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        logger.info("Digest generato con successo tramite Gemini")
        return text
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore chiamata Gemini: {e}")
        return fallback_digest(articles)
    except (KeyError, IndexError) as e:
        logger.error(f"Errore parsing risposta Gemini: {e}")
        return fallback_digest(articles)


def fallback_digest(articles):
    logger.warning("Usando fallback digest (senza LLM)")
    lines = ["📰 *Daily Tech Digest* (modalità fallback)\n"]
    by_cat = {}
    for art in articles:
        by_cat.setdefault(art["category"], []).append(art)

    emoji_map = {"AI": "🤖", "Tech": "💻", "Startup": "🚀"}
    for cat, arts in by_cat.items():
        emoji = emoji_map.get(cat, "📌")
        lines.append(f"\n{emoji} *{cat}*")
        for art in arts:
            lines.append(f"• {art['title']} — _{art['source']}_")
            if art["link"]:
                lines.append(f"  🔗 {art['link']}")

    lines.append(f"\n📊 Totale: {len(articles)} notizie")
    return "\n".join(lines)
