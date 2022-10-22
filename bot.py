import os
import logging
from textwrap import dedent

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from constants import cities_en, cities_ru

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

load_dotenv()

def get_greeting_msg(lang, username):
    if lang == "ru":
        msg = f"""
            Привет, <b>{username}**</b>! Я помогу тебе найти обменники в Казахстане с наиболее выгодным курсом.
            Для начала тебе нужно выбрать город, в котором ты находишься.
        """
    else:
        msg = f"""
            Hello, <b>{username}</b>! I will help you to find exchange offices with the best exchange rate.
            First you need to choose the city where you are located.
        """
    return dedent(msg)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = update.effective_user.language_code
    suggested_language = "ru" if user_lang == "ru" else "en"

    context.user_data["language"] = suggested_language

    buttons = {
        "en": ["Choose a city", "Использовать русский язык"],
        "ru": ["Выбрать город", "Switch to English"]
    }

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(buttons[suggested_language][0], callback_data="choose_city"),
            InlineKeyboardButton(buttons[suggested_language][1], callback_data="change_language")
        ]]
    )

    await update.message.reply_text(get_greeting_msg(suggested_language, update.effective_user.first_name), parse_mode="HTML", reply_markup=keyboard)

async def choose_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data["language"]
    n_keyboard_cols = 3
    btns = []
    for i in range(len(cities_en)):
        col_index = i // n_keyboard_cols
        if i % n_keyboard_cols == 0:
            btns.append([])
        btns[col_index].append(InlineKeyboardButton(cities_en[i] if lang == "en" else cities_ru[i], callback_data=f"set_user_city_{cities_en[i].lower()}"))
    
    keyboard = InlineKeyboardMarkup(btns)
    
    text_msg = "Choose a city:" if lang == "en" else "Выбери город:"

    await context.bot.send_message(update.effective_chat.id, text_msg, reply_markup=keyboard)

async def set_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data["language"]
    city = update.callback_query.data.split("_")[-1]

    context.user_data["city"] = city

    text_msg = f"Settings were updated, {city.capitalize()} is your city now" if lang == "en" else f"Я обновил настройки, {city.capitalize()} установлен как ваш город"

    await context.bot.send_message(update.effective_chat.id, text_msg)

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_API_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_city, "choose_city"))
    app.add_handler(CallbackQueryHandler(set_user_city, r"^set_user_city_[a-z]+"))
    app.add_handler(CallbackQueryHandler(change_language, "change_language"))

    app.run_polling()