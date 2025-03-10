import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai
import os
import requests

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Configura la chiave API di OpenAI
openai.api_key = OPENAI_API_KEY

# Crea il bot Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Funzione di chat aggiornata per la versione >= 1.0.0
def chat(update, context):
    user_text = update.message.text

    # Usa la nuova interfaccia di OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]  # Messaggio del cliente
    )

    reply_text = response['choices'][0]['message']['content']
    update.message.reply_text(reply_text)

def start(update, context):
    update.message.reply_text("Ciao! Sono una ragazza virtuale. Scrivimi qualcosa!")

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
    # Crea l'applicazione Telegram
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Aggiungi i gestori
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))  # Gestisci i messaggi di testo con la funzione chat
    application.add_handler(CommandHandler("img", generate_image))

    # Avvia il polling
    application.run_polling()

if __name__ == "__main__":
    main()
