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
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN non è definito!")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY non è definito!")

# Imposta la chiave API di OpenAI
openai.api_key = OPENAI_API_KEY

# Configura Quart
app = Quart(__name__)

# Configura il bot di Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Crea l'applicazione globale per Telegram
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
logger.debug("Telegram Application initialized")

# Funzione per gestire i segnali
def handle_sigterm(signum, frame):
    logger.info("Received SIGTERM, shutting down gracefully...")
    if application:
        logger.info("Shutting down the Telegram bot application.")
        application.stop()

signal.signal(signal.SIGTERM, handle_sigterm)

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = telegram.Update.de_json(await request.get_json(force=True), bot)
        logger.debug(f"Received update: {update}")
        await application.process_update(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500

# Funzione /start
async def start(update: Update, context):
    await update.message.reply_text("Ciao! Sono un bot con intelligenza artificiale. Scrivimi qualcosa!")

# Funzione per rispondere con OpenAI (ChatGPT)
async def chat(update: Update, context):
    user_text = update.message.text
    try:
        logger.debug(f"User input: {user_text}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}]
        )
        reply_text = response['choices'][0]['message']['content']
        logger.debug(f"Replying with: {reply_text}")
        await update.message.reply_text(reply_text)
    except Exception as e:
        logger.error(f"Errore con OpenAI: {str(e)}")
        await update.message.reply_text("Errore nel generare la risposta, riprova più tardi.")

# Aggiungi i gestori di comandi
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

async def start_bot():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    bot.set_webhook(url="https://telegram-2m17.onrender.com/webhook")
    logger.info("Bot avviato e webhook impostato.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    app.run(host="0.0.0.0", port=5000)
