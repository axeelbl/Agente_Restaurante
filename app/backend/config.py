# Variables globales, carga de .env, constantes

import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LEADS_FILE = BASE_DIR / "leads.csv"

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM = os.getenv("SENDGRID_FROM")
SENDGRID_TO = os.getenv("SENDGRID_TO")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM = os.getenv("RESEND_FROM") or os.getenv("SENDGRID_FROM")
RESEND_TO = os.getenv("RESEND_TO") or os.getenv("SENDGRID_TO")
LEADS_FILE = "leads.csv"
