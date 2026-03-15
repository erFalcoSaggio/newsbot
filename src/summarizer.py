"""
Sintesi degli articoli tramite Gemini API — v2.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash-lite"


def _gemini_url():
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )


SYSTEM_PROMPT = """Sei un editor di una newsletter tech italiana di alta qualità.

COMPITO: Trasforma questa lista di articoli in un digest conciso e leggibile.

REGOLE RIGIDE:
- Scrivi SOLO in italiano
- Ogni notizia va riassunta in MASSIMO 2 frasi
- Sii specifico: includi numeri, nomi, cifre quando disponibili
- NON usare frasi generiche tipo "grande impatto sul settore" o "interessante sviluppo"
- Se una notizia non è davvero importante, OMETTILA — meglio 5 notizie buone che 12 mediocri
- Collega notizie correlate con una breve nota (es. "collegato al punto precedente...")

FORMATO (usa esattamente questa struttura):

🤖 *AI & Machine Learning*

• Riassunto notizia conciso e specifico — _Fonte_
  [Link](url)

🚀 *Startup & Funding*

• Riassunto notizia — _Fonte_
  [Link](url)

💻 *Tech*

• Riassunto notizia — _Fonte_
  [Link](url)

---
📊 _X notizie selezionate | Digest generato automaticamente_

REGOLE FORMATO:
- Ometti categorie vuote
- Una riga vuota tra ogni notizia
- Il link va su una riga separata sotto il riassunto
- Usa *grassetto* per i nomi importanti (aziende, prodotti, persone)
- Usa _corsivo_ solo per le fonti"""


def build_articles_text(articles):
    lines = []
    for i, art in enumerate(articles, 1):
        lines.append(
            f"{i}. [{art['category']}] {art['title']}\n"
            f"   Fonte: {art['source']}\n"
            f"   Descrizione: {art['summary'][:300]}\n"
            f"   Link: {art['link']}\n"
            f"   Punteggio rilevanza: {art.get('score', 0)}"
        )
    return "\n\n".join(lines)


def summarize(articles):
    if not articles:
        return "📭 Nessuna notizia rilevante trovata oggi."

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY non configurata")
        return fallback_digest(articles)

    articles_text = build_articles_text(articles)
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"--- ARTICOLI (ordinati per rilevanza, i primi sono i più importanti) ---\n\n"
        f"{articles_text}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        },
    }

    try:
        url = _gemini_url()
        resp = requests.post(url, json=payload, timeout=60)
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
    lines = []
    by_cat = {}
    for art in articles:
        by_cat.setdefault(art["category"], []).append(art)

    emoji_map = {"AI": "🤖", "Tech": "💻", "Startup": "🚀"}
    for cat, arts in by_cat.items():
        emoji = emoji_map.get(cat, "📌")
        lines.append(f"{emoji} *{cat}*\n")
        for art in arts[:5]:  # Max 5 per categoria nel fallback
            lines.append(f"• {art['title']} — _{art['source']}_")
            if art["link"]:
                lines.append(f"  {art['link']}\n")

    lines.append(f"---\n📊 _{len(articles)} notizie | Modalità fallback (senza AI)_")
    return "\n".join(lines)
