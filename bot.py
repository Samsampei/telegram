from flask import Flask, request
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai
import requests
import os

# Crea l'app Flask
app = Flask(__name__)

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Crea il bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Gestione del webhook
@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        # Qui gestiamo l'update direttamente, senza fare uso di "application"
        handle_update(update)
        return 'OK', 200
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500

# Funzione che gestisce l'update (questa può essere personalizzata)
def handle_update(update):
    # Qui puoi gestire i vari tipi di messaggi ricevuti dal bot
    if update.message.text == "/start":
        start(update)
    elif update.message.text.startswith("/img"):
        generate_image(update)
    else:
        chat(update)

def start(update):
    update.message.reply_text("Ciao! Sono una ragazza virtuale. Scrivimi qualcosa!")

def chat(update):
    user_text = update.message.text
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]
    )

    reply_text = response["choices"][0]["message"]["content"]
    update.message.reply_text(reply_text)

def generate_image(update):
    user_prompt = "una bellissima ragazza virtuale, stile anime, sfondo futuristico"
    
    headers = {"Authorization": f"Token {REPLICATE_API_

