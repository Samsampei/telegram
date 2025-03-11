import openai
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from quart import Quart, request
import os
import asyncio
import logging
import signal

# Configura il logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Il token TELEGRAM_BOT_TOKEN non è stato trovato!")
if not OPENAI_API_KEY:
    raise ValueError("Il token OPENAI_API_KEY non è stato trovato!")

openai.api_key = OPENAI_API_KEY

# Configura Quart
app = Quart(__name__)

# 🔥 **Inizializza l'applicazione una volta sola**
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

@app.route("/", methods=["GET"])
async def home():
    return "Bot Telegram attivo! 🚀", 200

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Gestisce gli aggiornamenti di Telegram"""
    try:
        update_json = await request.get_json()
        update = Update.de_json(update_json, application.bot)
        logger.debug(f"Received update: {update}")

        # ❌ **Non chiamiamo più initialize() qui!**
        await application.process_update(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500

# Funzione /start
async def start(update: Update, context):
    await update.message.reply_text("Ciao! Sono un bot con intelligenza artificiale. Scrivimi qualcosa!")

# Funzione per rispondere con OpenAI
async def chat(update: Update, context):
    user_text = update.message.text
    try:
        logging.debug(f"User input: {user_text}")  
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}]
        )
        reply_text = response['choices'][0]['message']['content']
        await update.message.reply_text(reply_text)
    except Exception as e:
        logging.error(f"Errore con OpenAI: {str(e)}")  
        await update.message.reply_text(f"Errore: {str(e)}")

# Gestore dei segnali per Render
def shutdown_handler(signum, frame):
    logger.info("Spegnimento in corso...")
    asyncio.create_task(application.shutdown())

signal.signal(signal.SIGTERM, shutdown_handler)

# Funzione principale
async def main():
    """Configura l'applicazione e avvia Quart"""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    # Imposta il webhook
    webhook_url = "https://telegram-2m17.onrender.com/webhook"
    await application.initialize()
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook impostato su {webhook_url}")

# 🔥 **Avvia `main()` senza bloccare il loop**
asyncio.create_task(main())

# Avvia Quart (Render lo tiene attivo)
app.run(host="0.0.0.0", port=5000)

import uvicorn

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())  # Assicura che il bot venga avviato correttamente

    # Avvia il server web
    uvicorn.run(app, host="0.0.0.0", port=5000)

