import os, requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("API_BASE")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Spotify Downloader Bot\n\n"
        "Spotify song link পাঠান"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "spotify.com/track" not in url:
        await update.message.reply_text("❌ Spotify track link দিন")
        return

    msg = await update.message.reply_text("⏳ Processing...")

    try:
        r = requests.get(f"{API_BASE}/sp/dl", params={"url": url}, timeout=120).json()
        if not r.get("success"):
            await msg.edit_text("❌ Failed")
            return

        await update.message.reply_audio(audio=r["download_url"])
        await msg.delete()

    except:
        await msg.edit_text("⚠️ Error")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()
