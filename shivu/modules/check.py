from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from telegram.constants import ParseMode
from shivu import application, collection

# /check <character_id> command
async def check_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text(
            "❌ Incorrect format. Please use: /check character_id"
        )
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

    await update.message.reply_photo(
        photo=waifu['img_url'],
        caption=caption,
        parse_mode=ParseMode.MARKDOWN
    )

# Register the command
application.add_handler(CommandHandler("check", check_command))
