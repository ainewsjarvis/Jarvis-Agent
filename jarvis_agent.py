import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# 1. Google API-nøkkel
GEMINI_API_KEY = "AIzaSyCXf10TO_1BzsyROPR_ulpg_qYEqPTnmAU"

# 2. Din Telegram Token
TELEGRAM_TOKEN = "8963063213:AAGiX2gq3fgDwf7_bPXO7SoZVzmKqM9qS-o"

client = genai.Client(api_key=GEMINI_API_KEY)
MODELL = "gemini-1.5-flash"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def haandter_melding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bruker_tekst = update.message.text
    print(f"Mottatt fra mobil: {bruker_tekst}")

    try:
        response = client.models.generate_content(
            model=MODELL,
            contents=bruker_tekst
        )
        svar = response.text
    except Exception as e:
        svar = f"Feil ved oppkobling: {e}"

    await update.message.reply_text(svar)

if __name__ == '__main__':
    print("--- 🤖 JARVIS TELEGRAM-BOT ER STARTET OG LYTTER PÅ MOBILEN ---")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), haandter_melding))
    app.run_polling()
