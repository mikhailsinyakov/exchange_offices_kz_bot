import os
import logging
from textwrap import dedent

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from constants import cities_en, cities_ru
from exchange_offices import get_offices_info, find_best_offices
from geocode import geocode

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

load_dotenv()

def get_greeting_msg(lang, username):
    if lang == "ru":
        msg = f"""
            Привет, <b>{username}</b>! Я помогу тебе найти обменники в Казахстане с наиболее выгодным курсом.
            Для начала тебе нужно выбрать город, в котором ты находишься.
        """
    else:
        msg = f"""
            Hello, <b>{username}</b>! I will help you to find exchange offices with the best exchange rate.
            First you need to choose the city where you are located.
        """
    return dedent(msg)

async def greet_user(update, context):
    lang = context.user_data["language"]
    buttons = {
        "en": ["Choose a city", "Использовать русский язык"],
        "ru": ["Выбрать город", "Switch to English"]
    }

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(buttons[lang][0], callback_data="choose_city"),
            InlineKeyboardButton(buttons[lang][1], callback_data="change_language")
        ]]
    )
    if update.message is not None:
        await update.message.reply_text(get_greeting_msg(lang, update.effective_user.first_name), parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(get_greeting_msg(lang, update.effective_user.first_name), parse_mode="HTML", reply_markup=keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = update.effective_user.language_code
    await context.bot.set_my_commands([
        BotCommand("settings", "Show current settings"),
        BotCommand("find_best_offices", "Find offices with best currency rates")
    ])
    await context.bot.set_my_commands([
        BotCommand("settings", "Показать текущие настройки"),
        BotCommand("find_best_offices", "Найти обменники с лучшими курсами валют")
    ], language_code="ru")

    suggested_language = "ru" if user_lang == "ru" else "en"

    context.user_data["language"] = suggested_language
    await greet_user(update, context)

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("city", "Unset")
    lang = context.user_data.get("language", "Unset")

    msg = f"<b>{'City' if lang == 'en' else 'Город'}</b>: {city.capitalize()}\n"
    msg += "<b>Language</b>: English" if lang == "en" else "<b>Язык</b>: Русский"

    await update.message.reply_text(msg, parse_mode="HTML")

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

    await update.callback_query.answer()
    await context.bot.send_message(update.effective_chat.id, text_msg, reply_markup=keyboard)

async def set_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data["language"]
    city = update.callback_query.data.split("_")[-1]

    context.user_data["city"] = city

    text_msg = f"Settings were updated, {city.capitalize()} is your city now" if lang == "en" else f"Я обновил настройки, {city.capitalize()} установлен как ваш город"

    await update.callback_query.answer()
    await context.bot.send_message(update.effective_chat.id, text_msg)

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    curr_lang = context.user_data["language"]
    context.user_data["language"] = "ru" if curr_lang == "en" else "en"

    await update.callback_query.answer()
    await greet_user(update, context)

async def find_offices_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["transaction"] = {
        "sale_currency": None,
        "purchase_currency": None,
        "sale_amount": None
    }

    lang = context.user_data["language"]
    msg = {
        "en": "Enter a sale currency:",
        "ru": "Введите валюту продажи:"
    }
    keyboard = ReplyKeyboardMarkup([["USD", "EUR", "RUB", "KZT"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(msg[lang], reply_markup=keyboard)

async def find_offices_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "transaction" in context.user_data:
        if context.user_data["transaction"]["sale_currency"] is None:
            sale_currency = update.message.text
            context.user_data["transaction"]["sale_currency"] = sale_currency

            lang = context.user_data["language"]
            msg = {
                "en": "Enter a purchase currency:",
                "ru": "Введите валюту покупки:"
            }
            currencies = [c for c in ["USD", "EUR", "RUB", "KZT"] if c != sale_currency]
            keyboard = ReplyKeyboardMarkup([currencies], one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(msg[lang], reply_markup=keyboard)
        elif context.user_data["transaction"]["purchase_currency"] is None:
            purchase_currency = update.message.text
            context.user_data["transaction"]["purchase_currency"] = purchase_currency

            lang = context.user_data["language"]
            msg = {
                "en": "Enter a sale amount:",
                "ru": "Введите сумму продажи:"
            }
            await update.message.reply_text(msg[lang])
        elif context.user_data["transaction"]["sale_amount"] is None:
            sale_currency = context.user_data["transaction"]["sale_currency"]
            purchase_currency = context.user_data["transaction"]["purchase_currency"]
            sale_amount = float(update.message.text)
            del context.user_data["transaction"]
            
            city = context.user_data["city"]
            offices = get_offices_info(city)
            best_offices, purchase_amount = find_best_offices(offices, sale_currency, purchase_currency, sale_amount)
            
            lang = context.user_data["language"]

            purchase_amount_str = {
                "en": f"Your purchase amount is {purchase_amount:.2f}{purchase_currency}",
                "ru": f"Сумма покупки: {purchase_amount:.2f}{purchase_currency}"
            }

            offices_list_str = {
                "en": "List of offices:\n",
                "ru": "Список обменников:\n"
            }

            for office in best_offices:
                offices_list_str["en"] += f"<b>{office['name']}</b> "
                offices_list_str["ru"] += f"<b>{office['name']}</b> "

                coords = geocode(f"Kazakhstan, {city}, {office['address']}")
                if coords is not None:
                    link_url = f"https://www.google.com/maps/dir//{coords[0]},{coords[1]}/"
                    offices_list_str["en"] += f"<a href='{link_url}'>On map</a>" + "\n"
                    offices_list_str["ru"] += f"<a href='{link_url}'>На карте</a>" + "\n"
                else:
                    offices_list_str["en"] += f"<i>{office['address']}</i>" + "\n"
                    offices_list_str["ru"] += f"<i>{office['address']}</i>" + "\n"

            msg = {
                "en": purchase_amount_str["en"] + "\n" + offices_list_str["en"],
                "ru": purchase_amount_str["ru"] + "\n" + offices_list_str["ru"]
            }
            await update.message.reply_text(msg[lang], parse_mode="HTML")



if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_API_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settings", show_settings))
    app.add_handler(CommandHandler("find_best_offices", find_offices_command_handler))

    app.add_handler(CallbackQueryHandler(choose_city, "choose_city"))
    app.add_handler(CallbackQueryHandler(set_user_city, r"^set_user_city_[a-z]+"))
    app.add_handler(CallbackQueryHandler(change_language, "change_language"))
    app.add_handler(MessageHandler(filters=filters.TEXT, callback=find_offices_message_handler))

    app.run_polling()