from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, waifu_collection
import re

WAIFU_CHANNEL_USERNAME = "database_shadowtestingbot"

def parse_caption(caption: str):
    try:
        name_match = re.search(r"Character Name:\s*(.+)", caption)
        anime_match = re.search(r"Anime Name:\s*(.+)", caption)
        rarity_match = re.search(r"Rarity:\s*(.+)", caption)
        id_match = re.search(r"ID:\s*(.+)", caption)

        if not (name_match and anime_match and rarity_match and id_match):
            return None

        return {
            "name": name_match.group(1).strip(),
            "anime": anime_match.group(1).strip(),
            "rarity": rarity_match.group(1).strip(),
            "id": id_match.group(1).strip()
        }
    except:
        return None

async def sync_waifus(update: Update, context: CallbackContext):
    await update.message.reply_text("🔄 Syncing waifus from channel...")

    count = 0
    try:
        async for message in context.bot.get_chat_history(WAIFU_CHANNEL_USERNAME, limit=0):
            if message.photo and message.caption:
                data = parse_caption(message.caption)
                if data:
                    waifu_doc = {
                        "id": data["id"],
                        "name": data["name"],
                        "anime": data["anime"],
                        "rarity": data["rarity"],
                        "img_url": message.photo[-1].file_id
                    }
                    await waifu_collection.update_one(
                        {"id": data["id"]},
                        {"$set": waifu_doc},
                        upsert=True
                    )
                    count += 1
        await update.message.reply_text(f"✅ Synced {count} waifus into the database.")
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to sync waifus.")
        print(f"[syncwaifus error] {e}")

application.add_handler(CommandHandler("syncwaifus", sync_waifus))
