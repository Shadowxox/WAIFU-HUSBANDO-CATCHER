from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from shivu import application, waifu_collection

ITEMS_PER_PAGE = 10

async def sips(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide an anime name.\nExample: `/sips Naruto`", parse_mode="Markdown")
        return

    anime = " ".join(context.args)
    characters = await waifu_collection.find({'anime': {'$regex': f"^{anime}$", '$options': 'i'}}).to_list(None)

    if not characters:
        await update.message.reply_text(f"No characters found for anime: {anime}")
        return

    await send_sips_page(update, context, characters, anime, 0)

async def send_sips_page(update_or_query, context, characters, anime, page):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    sliced = characters[start:end]

    text = f"🍿 Waifus from *{anime}* (Page {page + 1}):\n\n"
    for waifu in sliced:
        text += (
            f"🔹 *Name:* {waifu['name']}\n"
            f"🆔 ID: `{waifu['id']}`\n"
            f"💠 Rarity: {waifu['rarity']}\n\n"
        )

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"sips_prev_{anime}_{page - 1}"))
    if end < len(characters):
        buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"sips_next_{anime}_{page + 1}"))

    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update_or_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def sips_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    action, anime, page = query.data.split("_", 2)
    page = int(page)
    characters = await waifu_collection.find({'anime': {'$regex': f"^{anime}$", '$options': 'i'}}).to_list(None)
    await send_sips_page(query, context, characters, anime, page)

application.add_handler(CommandHandler("sips", sips))
application.add_handler(CallbackQueryHandler(sips_callback, pattern=r"^sips_(next|prev)_"))
