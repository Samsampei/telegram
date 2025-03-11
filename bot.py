import openai
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from quart import Quart, request
import os
import asyncio
import logging
import signal
import uvicorn

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

# Inizializza il bot Telegram
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

        await application.process_update(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500

# Comando /start
async def start(update: Update, context):
    await update.message.reply_text("Ciao! Sono un bot con intelligenza artificiale. Scrivimi qualcosa!")

# Risponde con OpenAI
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

# Funzione principale
async def main():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    webhook_url = "https://telegram-2m17.onrender.com/webhook"
    await application.initialize()  # 👈 AGGIUNGI QUESTA RIGA!
    await application.start()
    await application.updater.start_polling()  # 👈 Usa Polling per test locale (evita webhook)
    await application.stop()
    logger.info(f"Webhook impostato su {webhook_url}")

    # Avvia Quart con Hypercorn
    config = uvicorn.Config(app, host="0.0.0.0", port=5000, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())  # Usa asyncio.run per avviare correttamente l'event loop
