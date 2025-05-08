from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from shivu import application, user_collection

RARITY_EMOJIS = {
    "⚪️ Common": "⚪️",
    "🟣 Rare": "🟣",
    "🟡 Legendary": "🟡",
    "🟢 Medium": "🟢",
    "💮 Special Edition": "💮",
    "🔮 Limited Edition": "🔮",
    "🎐 Celestial": "🎐",
    "🔞 Erotic": "🔞",
    "💝 Valentine Special": "💝",
    "🧬 X Verse": "🧬",
    "🎃 Halloween Special": "🎃",
    "❄️ Winter Special": "❄️",
    "🌤️ Summer Special": "🌤️",
    "💫 Angelic": "💫",
    "All": "📦"
}

def get_rarity_keyboard(user_id):
    buttons = []
    row = []
    for rarity, emoji in RARITY_EMOJIS.items():
        row.append(InlineKeyboardButton(emoji, callback_data=f"cmode:{user_id}:{rarity}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

async def cmode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    keyboard = get_rarity_keyboard(user.id)
    await update.message.reply_text(
        "🎴 Select a rarity to filter your harem:", reply_markup=keyboard
    )

async def cmode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    caller_id = query.from_user.id

    try:
        _, user_id_str, rarity = query.data.split(":", maxsplit=2)
        owner_id = int(user_id_str)
    except:
        await query.answer("❌ Invalid selection.", show_alert=True)
        return

    if caller_id != owner_id:
        await query.answer("❌ This isn’t your harem menu.", show_alert=True)
        return

    await query.answer()  # safe to proceed now

    user_data = await user_collection.find_one({"id": owner_id})
    if not user_data or "characters" not in user_data:
        await query.edit_message_text("❌ No characters found.")
        return

    characters = user_data["characters"]
    if rarity != "All":
        characters = [c for c in characters if c.get("rarity") == rarity]

    if not characters:
        await query.edit_message_text(f"No characters found with rarity: {rarity}")
        return

    names = [c.get("name", "???") for c in characters]
    preview = ", ".join([f"<code>{n}</code>" for n in names[:15]])
    if len(names) > 15:
        preview += f"... and {len(names) - 15} more."

    await query.edit_message_text(
        f"🎴 <b>{rarity}</b> characters in harem:\n\n{preview}",
        parse_mode="HTML"
    )

application.add_handler(CommandHandler("cmode", cmode, block=False))
application.add_handler(CallbackQueryHandler(cmode_callback, pattern="^cmode:"))
