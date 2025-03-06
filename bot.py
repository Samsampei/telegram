import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai
import requests
import os

# Configura i token
TELEGRAM_BOT_TOKEN = "INSERISCI_IL_TUO_TOKEN"
OPENAI_API_KEY = "INSERISCI_LA_TUA_API_KEY_OPENAI"
REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"
REPLICATE_API_TOKEN = "INSERISCI_IL_TUO_TOKEN_REPLICATE"

# Configura il bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def start(update, context):
    update.message.reply_text("Ciao! Sono una ragazza virtuale. Scrivimi qualcosa!")

def chat(update, context):
    user_text = update.message.text
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]
    )

    reply_text = response["choices"][0]["message"]["content"]
    update.message.reply_text(reply_text)

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

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))
    dp.add_handler(CommandHandler("img", generate_image))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
