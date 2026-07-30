import logging
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai
from google.genai.errors import APIError

# 1. API-nøkler
GEMINI_API_KEY = "AIzaSyCXf10TO_1BzsyROPR_ulpg_qYEqPTnmAU"
TELEGRAM_TOKEN = "8963063213:AAGiX2gq3fgDwf7_bPXO7SoZVzmKqM9qS-o"

client = genai.Client(api_key=GEMINI_API_KEY)
MODELL = "gemini-2.5-flash"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Enkel web-server for at Render Free Web Service skal holde seg fornøyd
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Jarvis is alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def haandter_melding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bruker_tekst = update.message.text
    print(f"Mottatt fra mobil: {bruker_tekst}")

    for forsoek in range(3):
        try:
            response = client.models.generate_content(
                model=MODELL,
                contents=bruker_tekst
            )
            svar = response.text
            break
        except APIError as e:
            if "429" in str(e):
                await asyncio.sleep(5)
                svar = "Beklager, Google bremsede forespørselen litt. Prøv igjen om noen sekunder!"
            else:
                svar = f"API-feil: {e}"
                break
        except Exception as e:
            svar = f"Feil ved oppkobling: {e}"
            break

    await update.message.reply_text(svar)

if __name__ == '__main__':
    # Start webserver i egen tråd for Render
    threading.Thread(target=run_health_check_server, daemon=True).start()

    print("--- 🤖 JARVIS TELEGRAM-BOT ER STARTET OG LYTTER PÅ MOBILEN ---")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), haandter_melding))
    app.run_polling()
