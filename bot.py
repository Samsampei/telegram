import openai
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask, request
import os
import asyncio

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Imposta la chiave API di OpenAI
openai.api_key = OPENAI_API_KEY

# Configura Flask
app = Flask(__name__)

# Configura il bot di Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Crea l'applicazione globale per Telegram
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()  # Assicurati di inizializzare correttamente

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        print("Received update:", update)  # Debugging
        await application.process_update(update)  # Aggiungi await per l'operazione asincrona
        return 'OK', 200
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500


# Funzione /start
async def start(update: Update, context):
    await update.message.reply_text("Ciao! Sono un bot con intelligenza artificiale. Scrivimi qualcosa!")

# Funzione per rispondere con OpenAI (ChatGPT)
async def chat(update: Update, context):
    user_text = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}]
        )
        reply_text = response['choices'][0]['message']['content']
        await update.message.reply_text(reply_text)
    except Exception as e:
        await update.message.reply_text(f"Errore: {str(e)}")

# Funzione principale
def main():
    # Aggiungi i gestori di comandi
    application.add_handler(CommandHandler("start", start))
