import openai
import os
import asyncio
import logging
import uvicorn
from quart import Quart, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

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

# Configura Quart (il server web)
app = Quart(__name__)

# Inizializza l'app Telegram
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# 🔹 Funzione /start
async def start(update: Update, context):
    await update.message.reply_text("Ciao! Sono un bot con intelligenza artificiale. Scrivimi qualcosa!")

# 🔹 Funzione per rispondere con OpenAI
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
        logger.error(f"Errore con OpenAI: {str(e)}")
        await update.message.reply_text(f"Errore: {str(e)}")

# 🔹 Webhook per Telegram
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update_json = await request.get_json()
        update = Update.de_json(update_json, application.bot)
        await application.process_update(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Errore nel webhook: {str(e)}")
        return 'Errore interno', 500

# 🔹 Homepage
@app.route("/", methods=["GET"])
async def home():
    return "Bot Telegram attivo! 🚀", 200

# 🔹 Funzione principale per inizializzare il bot
async def run_bot():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    webhook_url = "https://telegram-2m17.onrender.com/webhook"

    logger.info(f"Imposto webhook su {webhook_url}")

    await application.initialize()  # 🔥 Fix principale: inizializza prima l'app
    await application.bot.set_webhook(url=webhook_url)
    await application.start()

# 🔹 Avvia il server e il bot in parallelo
async def main():
    await run_bot()
    config = uvicorn.Config(app, host="0.0.0.0", port=5000, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())  # 🔥 Fix: usa asyncio.run() per garantire l'ordine corretto
