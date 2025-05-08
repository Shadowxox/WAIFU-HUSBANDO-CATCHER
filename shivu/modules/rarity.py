from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import collection, application
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def rarities(update: Update, context: CallbackContext):
    try:
        characters_cursor = collection.find({})  # Get the cursor for all characters

        rarity_counts = {
            "⚪️ Common": 0,
            "🟢 Medium": 0,
            "🟣 Rare": 0,
            "🟡 Legendary": 0,
            "💮 Special Edition": 0,
            "🔮 Limited Edition": 0,
            "🎐 Celestial": 0,
            "🔞 Erotic": 0,
            "🧬 X Verse": 0,
            "🎃 Halloween Special": 0,
            "💝 Valentine Special": 0,
            "❄️ Winter Special": 0,
            "🌤️ Summer Special": 0,
            "💫 Angelic": 0,
        }

        async for character in characters_cursor:  # Iterate over the cursor asynchronously
            rarity = character.get('rarity')
            if rarity in rarity_counts:
                rarity_counts[rarity] += 1
            else:
                logger.warning(f"Unknown rarity: '{rarity}'")

        rarity_message = "<b>Rarity Counts:</b>\n"
        for rarity, count in rarity_counts.items():
            rarity_message += f"{rarity}: {count}\n"

        await update.message.reply_text(rarity_message, parse_mode='HTML')

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        await update.message.reply_text(f"An error occurred: {str(e)}")

application.add_handler(CommandHandler("rarities", rarity))
