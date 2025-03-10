import os
import telegram
import openai
import requests
from flask import Flask, request
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Configura Flask
app = Flask(__name__)

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Configura il bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Funzioni di gestione dei comandi
async def start(update, context):
    await update.message.reply_text("Ciao! Sono una ragazza virtuale. Scrivimi qualcosa!")

async def chat(update, context):
    user_text = update.message.text
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]
    )

    reply_text = response["choices"][0]["message"]["content"]
    await update.message.reply_text(reply_text)

async def generate_image(update, context):
    user_prompt = "una bellissima ragazza virtuale, stile anime, sfondo futuristico"
    
    headers = {"Authorization": f"Token {REPLICATE_API_TOKEN}"}
    data = {"version": "latest", "input": {"prompt": user_prompt}}

    response = requests.post(REPLICATE_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        image_url = response.json().get("output", [""])[0]
        await update.message.reply_photo(photo=image_url)
    else:
        await update.message.reply_text("Errore nella generazione dell'immagine.")

# Configura l'Application di telegram.ext
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
application.add_handler(CommandHandler("img", generate_image))

# Endpoint per Telegram Webhook
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = telegram.Update.de_json(request.get_json(), bot)
    await application.process_update(update)
    return "OK", 200

# Imposta il webhook all'avvio del server
@app.route("/")
def set_webhook():
    webhook_url = f"https://telegram-2m17.onrender.com/{TELEGRAM_BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to {webhook_url}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
