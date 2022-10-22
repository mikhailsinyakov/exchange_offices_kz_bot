import os
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello, {update.effective_user.first_name}!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_API_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()