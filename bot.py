import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask, request
import openai
import os
import requests

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Usa la chiave API di OpenAI
openai.api_key = OPENAI_API_KEY

# Configura Flask
app = Flask(__name__)

# Configura il bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Funzione per gestire il webhook
@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        
        # Gestisci l'aggiornamento in arrivo
        handle_message(update)
        
        return 'OK', 200
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500

def start(update, context):
    update.message.reply_text("Ciao! Sono una ragazza virtuale. Scrivimi qualcosa!")

def handle_message(update):
    user_text = update.message.text

    # Chiamata all'API OpenAI per generare una risposta
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=user_text,
        max_tokens=150  # Puoi regolare il numero di token se necessario
    )

    # Estrai il testo dalla risposta
    reply_text = response['choices'][0]['text'].strip()  # Ottieni la risposta dal modello
    update.message.reply_text(reply_text)  # Invia la risposta all'utente

def generate_image(update, context):
    user_prompt = "una bellissima ragazza virtuale, stile anime, sfondo futuristico"
    
    headers = {"Authorization": f"Token {REPLICATE_API_TOKEN}"}
    data = {
        "version": "latest",
        "input": {"prompt": user_prompt}
    }

    response = requests.post(REPLICATE_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        image_url = response.json().get("output", [""])[0]
        update.message.reply_photo(photo=image_url)
    else:
        update.message.reply_text("Errore nella generazione dell'immagine.")

# Imposta il webhook
bot.set_webhook(url="https://telegram-2m17.onrender.com/" + TELEGRAM_BOT_TOKEN)

# Avvia Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Esegui il server Flask
