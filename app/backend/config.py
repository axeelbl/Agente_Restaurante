# Variables globales, carga de .env, constantes

import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # llega a Agente_Peluquero_CV
LEADS_FILE = BASE_DIR / "leads.csv"

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM = os.getenv("SENDGRID_FROM")
SENDGRID_TO = os.getenv("SENDGRID_TO")
LEADS_FILE = "leads.csv"
