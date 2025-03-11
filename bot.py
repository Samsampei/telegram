import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Imposta il logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Token del bot Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN", "INSERISCI_IL_TUO_TOKEN")

# URL pubblico di Render per i Webhook (modificalo con il tuo)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://il-tuo-dominio.render.com")

# Crea l'applicazione Flask per gestire il webhook
app = Flask(__name__)

# Inizializza il bot Telegram
application = Application.builder().token(TOKEN).build()

# Comando di start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Ciao! Sono il tuo bot su Render! 🚀")

# Handler per i messaggi di testo
async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

# Aggiungi gli handler al bot
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Route per il webhook di Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    asyncio.run(application.process_update(update))
    return "OK", 200

# Funzione per avviare il webhook
async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL + f"/{TOKEN}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
