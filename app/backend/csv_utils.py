import csv
import os
from datetime import datetime

from .config import LEADS_FILE


def _safe_csv_cell(value) -> str:
    text = str(value or "")
    return "'" + text if text.startswith(("=", "+", "-", "@", "\t", "\r")) else text


def save_lead(user_message, bot_message, meta):
    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_exists = os.path.isfile(LEADS_FILE)
    with open(LEADS_FILE, "a", newline="", encoding="utf-8") as file_handle:
        writer = csv.writer(file_handle)
        if not file_exists:
            writer.writerow([
                "timestamp", "ip", "user_agent", "language", "referer",
                "response_time", "user_message", "bot_message",
            ])
        writer.writerow([
            datetime.now().isoformat(),
            meta.get("ip", ""),
            meta.get("user_agent", ""),
            meta.get("language", ""),
            meta.get("referer", ""),
            meta.get("response_time", ""),
            _safe_csv_cell(user_message),
            _safe_csv_cell(bot_message),
        ])


def get_last_modified():
    if os.path.exists(LEADS_FILE):
        return os.path.getmtime(LEADS_FILE)
    return 0
