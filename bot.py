import openai
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask, request
import requests
import os
import asyncio  # Per la gestione asincrona

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
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

@app.route('/test', methods=['GET'])
def test():
    return "Server Flask attivo e funzionante!", 200

# Funzione asincrona per processare gli update
async def process_update_async(update):
    # Assicurati che l'applicazione sia inizializzata
    if not application.running:
        await application.initialize()  
    await application.process_update(update)

# Funzione per gestire i messaggi del webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        asyncio.run(process_update_async(update))  # Esegui l'aggiornamento asincrono
        return 'OK', 200
    except Exception as e:
        app.logger.error(f"Errore durante il processamento del webhook: {str(e)}")
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Imposta il webhook
    bot.set_webhook(url="https://telegram-2m17.onrender.com/webhook")

    # Avvia il server Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Avvia il bot
if __name__ == "__main__":
    main()
