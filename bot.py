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

# Imposta la chiave API di OpenAI
openai.api_key = OPENAI_API_KEY

# Configura Quart
app = Quart(__name__)

# Configura il bot di Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Crea l'applicazione globale per Telegram
application = None

async def create_application():
    """Funzione asincrona per creare l'applicazione Telegram"""
    global application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    logger.debug("Telegram Application initialized")

# Funzione per gestire i segnali
def handle_sigterm(signum, frame):
    logger.info("Received SIGTERM, shutting down gracefully...")
    # Eventuali operazioni di pulizia
    if application:
        logger.info("Shutting down the Telegram bot application.")
        application.stop()

# Associa il segnale SIGTERM al handler
signal.signal(signal.SIGTERM, handle_sigterm)

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = telegram.Update.de_json(await request.get_json(force=True), bot)
        logger.debug(f"Received update: {update}")  # Log dell'update ricevuto
        if application:
            await application.process_update(update)  # Aggiungi await per l'operazione asincrona
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500


# Funzione /start
async def start(update: Update, context):
    await update.message.reply_text("Ciao! Sono un bot con intelligenza artificiale. Scrivimi qualcosa!")

# Funzione per rispondere con OpenAI (ChatGPT)
# Funzione per rispondere con OpenAI (ChatGPT)
async def chat(update: Update, context):
    user_text = update.message.text
    try:
        logging.debug(f"User input: {user_text}")  # Log dell'input dell'utente

        # Log della richiesta a OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}]
        )

        logging.debug(f"OpenAI response: {response}")  # Log della risposta di OpenAI

        reply_text = response['choices'][0]['message']['content']
        logging.debug(f"Replying with: {reply_text}")  # Log del testo che il bot invia
        await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Errore con OpenAI: {str(e)}")  # Log dell'errore in caso di problemi con OpenAI
        await update.message.reply_text(f"Errore: {str(e)}")


# Funzione principale
def main():
    # Inizializza l'applicazione Telegram asincrona
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_application())  # Assicurati che l'applicazione sia completamente inizializzata

    # Aggiungi i gestori di comandi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Imposta il webhook
    bot.set_webhook(url="https://telegram-2m17.onrender.com/webhook")

    # Avvia il server Quart
    app.run(host="0.0.0.0", port=5000)

# Avvia il bot
if __name__ == "__main__":
    main()
