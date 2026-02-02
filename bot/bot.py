import os
import threading
import logging
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("API_BASE")
# =======================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------- Dummy HTTP Server (Render health check) ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()
# ------------------------------------------------------------


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Spotify Downloader Bot\n\n"
        "Spotify song link পাঠান 🎧"
    )


# Handle Spotify links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "open.spotify.com/track" not in text:
        await update.message.reply_text("❌ শুধু Spotify track link দিন")
        return

    wait_msg = await update.message.reply_text("⏳ গান প্রসেস হচ্ছে...")

    try:
        r = requests.get(
            f"{API_BASE}/sp/dl",
            params={"url": text},
            timeout=120
        )

        data = r.json()

        if not data.get("success"):
            await wait_msg.edit_text("❌ গান ডাউনলোড করা গেল না")
            return

        await update.message.reply_audio(
            audio=data["download_url"]
        )

        await wait_msg.delete()

    except Exception as e:
        logging.error(e)
        await wait_msg.edit_text("⚠️ Error হয়েছে, পরে চেষ্টা করুন")


def main():
    # Start dummy HTTP server for Render
    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot started (Render Free compatible)")
    app.run_polling()


if __name__ == "__main__":
    main()
