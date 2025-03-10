import openai
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask, request
import requests
import os

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Imposta la chiave API di OpenAI
openai.api_key = OPENAI_API_KEY

# Configura Flask
app = Flask(__name__)

# Configura il bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Funzione per gestire i messaggi del webhook
@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        
        # Gestisci l'aggiornamento in arrivo
        chat(update)
        
        return 'OK', 200
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500

# Funzione start
async def start(update: Update, context):
    await update.message.reply_text("Ciao! Sono un bot con intelligenza artificiale. Scrivimi qualcosa!")

# Funzione per rispondere con OpenAI (usando la nuova API)
async def chat(update: Update, context):
    user_text = update.message.text  # Il testo che l'utente invia al bot
    
    try:
        # Richiesta alla API di OpenAI con il modello ChatGPT
        response = openai.completions.create(
            model="gpt-3.5-turbo",  # Usa il modello GPT-3.5 turbo
            messages=[{"role": "user", "content": user_text}]  # Passa il messaggio dell'utente
        )
        
        # Ottieni la risposta dal modello
        reply_text = response['choices'][0]['message']['con
