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
        pipeline = [
            {"$match": {"collection": character_id}},
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        owners_data = await user_collection.aggregate(pipeline).to_list(length=10)

        if not owners_data:
            msg = await query.message.reply_text("❌ No one owns this character yet.")
            await asyncio.sleep(120)
            return await msg.delete()

        lines = ["📝 *Users Who Have This Character:*"]
        for entry in owners_data:
            user = await context.bot.get_chat(entry["_id"])
            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"
            if user.username:
                name = f"@{user.username}"
            count = entry["count"]
            lines.append(f"👤 {name} (x{count})")

        lines.append("\n📊 *Top 10 Results Displayed!*")
        text = "\n".join(lines)

        sent = await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(120)
        try:
            await sent.delete()
        except:
            pass

# Register handlers
application.add_handler(CommandHandler("check", check_command))
application.add_handler(CallbackQueryHandler(who_owns, pattern=r"^owns_", block=False))
