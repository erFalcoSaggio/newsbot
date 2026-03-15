"""
NewsBot — Entry point.
"""

import sys
import os
import logging
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from collector import collect_all
from summarizer import summarize
from telegram_bot import send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("newsbot")


def main():
    today = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    logger.info(f"=== NewsBot Digest — {today} ===")

    logger.info("Step 1: Raccolta articoli da RSS...")
    articles = collect_all()

    if not articles:
        logger.warning("Nessun articolo trovato oggi")
        send_message(f"📭 *Digest {today}*\n\nNessuna notizia rilevante trovata oggi.")
        return

    logger.info(f"Step 2: Generazione digest ({len(articles)} articoli)...")
    digest = summarize(articles)

    header = f"📰 *Daily Tech Digest — {today}*\n\n"
    full_message = header + digest

    logger.info("Step 3: Invio su Telegram...")
    success = send_message(full_message)

    if success:
        logger.info("✅ Digest inviato con successo!")
    else:
        logger.error("❌ Errore nell'invio del digest")
        sys.exit(1)


if __name__ == "__main__":
    main()
