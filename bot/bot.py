import os
import requests
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ========= ENV =========
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("API_BASE")
# =======================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Spotify Downloader Bot\n\n"
        "Spotify song link পাঠান 🎧"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "open.spotify.com/track" not in text:
        await update.message.reply_text("❌ শুধু Spotify track link দিন")
        return

    wait = await update.message.reply_text("⏳ গান প্রসেস হচ্ছে...")

    try:
        r = requests.get(
            f"{API_BASE}/sp/dl",
            params={"url": text},
            timeout=120
        )
        data = r.json()

        if not data.get("success"):
            await wait.edit_text("❌ গান ডাউনলোড করা গেল না")
            return

        await update.message.reply_audio(
            audio=data["download_url"]
        )
        await wait.delete()

    except Exception as e:
        await wait.edit_text("⚠️ Error হয়েছে, পরে চেষ্টা করুন")
        print(e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot started (Python 3.13 compatible)")
    app.run_polling()

if __name__ == "__main__":
    main()
