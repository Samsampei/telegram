import openai
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask, request
import requests
import os

# Configura i token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_URL = os.getenv("REPLICATE_API_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Imposta la chiave API di OpenAI
openai.api_key = OPENAI_API_KEY

# Configura Flask
app = Flask(__name__)

# Configura il bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Funzione per gestire i messaggi del webhook
@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        
        # Gestisci l'aggiornamento in arrivo
        # Utilizza il dispatcher per passare l'aggiornamento al bot
        application.update_queue.put(update)
        
        return 'OK', 200
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return 'Internal Server Error', 500

# Funzione start
async def start(update: Update, context):
    await update.message.reply_text("Ciao! Sono un bot con intelligenza artificiale. Scrivimi qualcosa!")

# Funzione per rispondere con OpenAI (usando la nuova API)
async def chat(update: Update, context):
    user_text = update.message.text  # Il testo che l'utente invia al bot
    
    try:
        # Richiesta alla API di OpenAI con il modello ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Usa il modello GPT-3.5 turbo
            messages=[{"role": "user", "content": user_text}]  # Passa il messaggio dell'utente
        )
        
        # Ottieni la risposta dal modello
        reply_text = response['choices'][0]['message']['content']
        
        # Rispondi all'utente
        await update.message.reply_text(reply_text)
    except Exception as e:
        # Gestione degli errori
        await update.message.reply_text(f"Errore: {str(e)}")

# Funzione per generare l'immagine tramite Replicate
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
    global application  # Rendi `application` una variabile globale

    # Crea l'applicazione per Telegram
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Aggiungi i gestori
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    application.add_handler(CommandHandler("img", generate_image))

    # Esegui il webhook
    bot.set_webhook(url="https://<il_tuo_dominio>/" + TELEGRAM_BOT_TOKEN)

    # Esegui il server Flask per il webhook
    app.run(host="0.0.0.0", port=5000)  # Esegui il server Flask


if __name__ == "__main__":
    main()
