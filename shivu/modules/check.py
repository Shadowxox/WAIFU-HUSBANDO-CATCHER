import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode
from shivu import application, collection, user_collection

# /check command
async def check_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text("❌ Incorrect format. Use: /check character_id")
        return

    character_id = context.args[0]
    waifu = await collection.find_one({'id': character_id})

    if not waifu:
        await update.message.reply_text("❌ Character not found with that ID.")
        return

    caption = (
        f"🌸 Name: {waifu.get('name', 'Unknown')}\n"
        f"⭐ Rarity: {waifu.get('rarity', 'N/A')}\n"
        f"🎬 Anime: {waifu.get('anime', 'Unknown')}"
    )

    keyboard = [[InlineKeyboardButton("👤 Who Owns This?", callback_data=f"owns_{character_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_msg = await update.message.reply_photo(
        photo=waifu['img_url'],
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

    # Auto-delete waifu image message after 2 minutes
    await asyncio.sleep(120)
    try:
        await sent_msg.delete()
    except:
        pass

# Callback for who owns
async def who_owns(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("owns_"):
        character_id = query.data.split("_", 1)[1]
        cursor = user_collection.find({'collection': character_id})

        owners = []
        async for user in cursor:
            name = user.get("first_name", "Unknown")
            username = user.get("username")
            mention = f"@{username}" if username else name
            owners.append(mention)

        text = (
            f"👥 Owners of character ID `{character_id}`:\n\n" +
            ("\n".join(owners) if owners else "No one owns this character yet.")
        )

        owner_msg = await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

        # Auto-delete owner message after 2 minutes
        await asyncio.sleep(120)
        try:
            await owner_msg.delete()
        except:
            pass

# Register handlers
application.add_handler(CommandHandler("check", check_command))
application.add_handler(CallbackQueryHandler(who_owns, pattern=r"^owns_", block=False))
