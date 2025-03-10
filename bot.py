import os
import openai
import requests
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Crea il bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Inizializza Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Il bot è attivo!"

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
async def webhook():
    """Riceve gli aggiornamenti di Telegram e li inoltra all'application."""
    update = Update.de_json(request.get_json(force=True), bot)
    await application.update_queue.p
