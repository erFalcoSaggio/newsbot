"""
Invio del digest giornaliero su Telegram.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_message(text, parse_mode="Markdown"):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID non configurati")
        return False

    chunks = split_message(text, max_len=4000)
    success = True

    for i, chunk in enumerate(chunks):
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }
        try:
            resp = requests.post(
                f"{TELEGRAM_API}/sendMessage",
                json=payload,
                timeout=15
            )
            if resp.status_code == 400 and "parse" in resp.text.lower():
                logger.warning("Markdown non valido, invio senza formattazione")
                payload["parse_mode"] = ""
                resp = requests.post(
                    f"{TELEGRAM_API}/sendMessage",
                    json=payload,
                    timeout=15
                )
            resp.raise_for_status()
            logger.info(f"Messaggio {i+1}/{len(chunks)} inviato")
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore invio Telegram (chunk {i+1}): {e}")
            success = False

    return success


def split_message(text, max_len=4000):
    if len(text) <= max_len:
        return [text]
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len:
            if current:
                chunks.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks
