import os
import logging

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from constants import cities, currency_names, currencies
from exchange_offices import get_offices_info, find_best_offices
from helpers import get_offices_info_msg
from geocode import geocode
from translation import translate as _

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

if os.path.exists(".env"):
    load_dotenv()


async def greet_user(update, context):
    lang = context.user_data.get("language", "en")
    button_keys = ["choose_city", "switch_language_foreign"]

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(_(button_keys[0], lang), callback_data="choose_city"),
            InlineKeyboardButton(_(button_keys[1], lang), callback_data="change_language")
        ]]
    )
    greeting_msg = f"{_('hi', lang)}, <b>{update.effective_user.first_name}!</b> {_('greeting', lang)}"

    if update.message is not None:
        await update.message.reply_text(greeting_msg, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(greeting_msg, parse_mode="HTML", reply_markup=keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = update.effective_user.language_code
    
    await context.bot.set_my_commands([
        BotCommand("find_best_offices", _("find_best_offices", "en")),
        BotCommand("settings", _("show_settings", "en")),
        BotCommand("edit_city", _("edit_city", "en")),
        BotCommand("switch_language", _("switch_language", "en")),
        BotCommand("help", _("help", "en"))
    ])
    await context.bot.set_my_commands([
        BotCommand("find_best_offices", _("find_best_offices", "ru")),
        BotCommand("settings", _("show_settings", "ru")),
        BotCommand("edit_city", _("edit_city", "ru")),
        BotCommand("switch_language", _("switch_language", "ru")),
        BotCommand("help", _("help", "ru"))
    ], language_code="ru")

    suggested_language = "ru" if user_lang == "ru" else "en"

    context.user_data["language"] = suggested_language
    await greet_user(update, context)

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("city", "Unset")
    lang = context.user_data.get("language", "Unset")

    msg = f"<b>{_('city', lang)}</b>: {city.capitalize()}" + "\n"
    msg += f"<b>{_('language', lang)}</b>: {_('current_language', lang)}"

    await update.message.reply_text(msg, parse_mode="HTML")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(_("help_text", lang))

async def choose_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    n_keyboard_cols = 3
    btns = []
    for i in range(len(cities)):
        col_index = i // n_keyboard_cols
        if i % n_keyboard_cols == 0:
            btns.append([])
        btns[col_index].append(InlineKeyboardButton(_(cities[i], lang) , callback_data=f"set_user_city_{cities[i]}"))
    
    keyboard = InlineKeyboardMarkup(btns)
    
    text_msg = _("choose_city_imperative", lang) + ":"

    if update.callback_query is not None:
        await update.callback_query.answer()
    await context.bot.send_message(update.effective_chat.id, text_msg, reply_markup=keyboard)

async def set_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    city = update.callback_query.data.split("_")[-1]

    context.user_data["city"] = city
    text_msg = f"{_('settings_updated', lang)}, {city.capitalize()} {_('city_was_set', lang)}"
    
    await update.callback_query.answer()
    await context.bot.send_message(update.effective_chat.id, text_msg)

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    curr_lang = context.user_data["language"]
    new_lang = "ru" if curr_lang == "en" else "en"
    context.user_data["language"] = new_lang

    if update.callback_query is not None:
        await update.callback_query.answer()
        await greet_user(update, context)
    else:
        await context.bot.send_message(update.effective_chat.id, _("language_changed", new_lang))

async def find_offices_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    currency_names_locale = [_(c, lang) for c in currency_names]

    context.user_data["transaction"] = {
        "sale_currency": None,
        "purchase_currency": None,
        "sale_amount": None,
        "currency_names_locale": currency_names_locale
    }

    keyboard = ReplyKeyboardMarkup([currency_names_locale], one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(_("enter_sale_currency", lang) + ":", reply_markup=keyboard)

async def find_offices_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sale_currency_name = context.user_data["transaction"]["sale_currency"]
    purchase_currency_name = context.user_data["transaction"]["purchase_currency"]
    sale_amount = context.user_data["transaction"]["sale_amount"]
    currency_names_locale = context.user_data["transaction"]["currency_names_locale"]

    if sale_currency_name is None:
        lang = context.user_data.get("language", "en")
        new_sale_currency = update.message.text

        if new_sale_currency not in currency_names_locale:
            keyboard = ReplyKeyboardMarkup([currency_names_locale], one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(_("wrong_currency", lang) + ". " + _("enter_sale_currency", lang) + ":", reply_markup=keyboard)

            return

        context.user_data["transaction"]["sale_currency"] = new_sale_currency

        currencies_to_show = [c for c in currency_names_locale if c != new_sale_currency]

        keyboard = ReplyKeyboardMarkup([currencies_to_show], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(_("enter_purchase_currency", lang) + ":", reply_markup=keyboard)
    elif purchase_currency_name is None:
        lang = context.user_data.get("language", "en")
        new_purchase_currency = update.message.text

        if new_purchase_currency not in currency_names_locale:
            currencies_to_show = [c for c in currency_names_locale if c != sale_currency_name]
            keyboard = ReplyKeyboardMarkup([currencies_to_show], one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(_("wrong_currency", lang) + ". " + _("enter_purchase_currency", lang) + ":", reply_markup=keyboard)

            return

        context.user_data["transaction"]["purchase_currency"] = new_purchase_currency

        await update.message.reply_text(_("enter_sale_amount", lang) + ":")
        
    elif sale_amount is None:
        lang = context.user_data.get("language", "en")
        try:
            sale_amount = float(update.message.text)
        except ValueError:
            await update.message.reply_text(_("need_number", lang))
            return

        wait_msg = await update.message.reply_text(_("wait", lang) + " ...")

        sale_currency = currencies[currency_names_locale.index(sale_currency_name)]
        purchase_currency = currencies[currency_names_locale.index(purchase_currency_name)]
        
        del context.user_data["transaction"]
        
        city = context.user_data["city"]
        all_offices = get_offices_info(city)
        best_offices, purchase_amount = find_best_offices(all_offices, sale_currency, purchase_currency, sale_amount)
        
        offices_info_for_display = []
        for best_office in best_offices:
            office = {}
            office["name"] = best_office["name"]
            coords = geocode(f"Kazakhstan, {city}, {best_office['address']}")
            if coords is not None:
                link_url = f"https://www.google.com/maps/dir//{coords[0]},{coords[1]}/"
                office["location"] = link_url
            else:
                office["location"] = best_office["address"]
            
            offices_info_for_display.append(office)
        
        msg = get_offices_info_msg(offices_info_for_display, purchase_amount, purchase_currency, lang)
        
        await context.bot.edit_message_text(text=msg, chat_id=update.effective_chat.id, message_id=wait_msg.id, parse_mode="HTML")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "transaction" in context.user_data:
        await find_offices_message_handler(update, context)
    else:
        lang = context.user_data.get("language", "en")
        await update.message.reply_text(_("cant_understand", lang))

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_API_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settings", show_settings))
    app.add_handler(CommandHandler("find_best_offices", find_offices_command_handler))
    app.add_handler(CommandHandler("edit_city", choose_city))
    app.add_handler(CommandHandler("switch_language", change_language))
    app.add_handler(CommandHandler("help", help))

    app.add_handler(CallbackQueryHandler(choose_city, "choose_city"))
    app.add_handler(CallbackQueryHandler(set_user_city, r"^set_user_city_[a-z]+"))
    app.add_handler(CallbackQueryHandler(change_language, "change_language"))
    app.add_handler(MessageHandler(filters=filters.TEXT, callback=message_handler))

    app.run_polling()