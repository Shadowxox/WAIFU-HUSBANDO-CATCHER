import datetime
import importlib
import time
import random
import re
import asyncio
from html import escape 
import asyncio
import random
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters
from shivu import app
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, db, LOGGER
from shivu.modules import ALL_MODULES
from keep_alive import keep_alive
keep_alive()


locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}


for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)


last_user = {}
warned_users = {}
def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)



async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id


    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:

        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 100)
        else:
            message_frequency = 50


        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:

                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:


                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}


        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1


        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)

            message_counts[chat_id] = 0

async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")  # Get current date

    all_characters = list(await collection.find({}).to_list(length=None))

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # Calculate today's message count
    if chat_id in message_counters:
        today_message_count = message_counters[chat_id].get(current_time, 0)
    else:
        today_message_count = 0

    # Check the total messages sent
    total_messages_sent = message_counts.get(chat_id, 0)

    # Determine if we should spawn a Halloween character
    spawn_halloween = 200 <= total_messages_sent <= 300 and random.random() < 0.1  # 10% chance

    rarities = {
        1: '⚪️ Common',
        2: '🟢 Medium',
        3: '🟣 Rare',
        4: '🟡 Legendary',
        5: '💮 Special edition',
        6: '🔮 Limited Edition',
        7: '🎐 Celestial',
        8: '🔞 Erotic',
        9: '🧬 X Verse',
        10: '🎃 Halloween Special',
        11: '💝 Valentine Special',
        12: '❄️ Winter Special',
        13: '🌤️ Summer Special',
        14: '💫 Angelic'
    }

    # Define spawn probabilities for each rarity
    spawn_counts = {
        '⚪️ Common': 5,
        '🟢 Medium': 6,
        '🟣 Rare': 15,
        '🟡 Legendary': 9,
        '💮 Special edition': 4,
        '🔮 Limited Edition': 1,
        '🎐 Celestial': 0,
        '🔞 Erotic': 0,
        '🧬 X Verse': 0,
        '🎃 Halloween Special': 0,
        '💝 Valentine Special': 0,
        '❄️ Winter Special': 1,
        '🌤️ Summer Special': 0,
        '💫 Angelic': 0
    }


    # Adjust spawn counts for Special Edition
    if today_message_count <= 4:  
        spawn_counts['💮 Special edition'] = 4
    else:
        spawn_counts['💮 Special edition'] = 2

    # Create a list of characters based on spawn counts
    characters_to_spawn = []
    for rarity, count in spawn_counts.items():
        characters_to_spawn.extend([c for c in all_characters if c.get('id') not in sent_characters[chat_id] and c.get('rarity') == rarity] * count)

    if not characters_to_spawn:
        characters_to_spawn = all_characters

    character = random.choice(characters_to_spawn)

    # Log if a Halloween character spawns
    if character.get('rarity') == '🎃 Halloween':
        await context.bot.send_message(chat_id=7378476666, text=f"A Halloween character has spawned! Character id: {character['id']}")

    rarity_name = rarities.get(character['rarity'], f'{character["rarity"]}')  

    sent_characters[chat_id].append(character.get('id'))
    last_characters[chat_id] = character

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    if character.get('img_url'):
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=character['img_url'],
            caption=f"🌟 A new {rarity_name} character has emerged! Quickly, head to /guess [Name] to reveal its name! 🌟",
            parse_mode='Markdown'
        )
    elif character.get('vid_url'):
        await context.bot.send_video(
            chat_id=chat_id,
            video=character['vid_url'],
            caption=f"🌟 A new {rarity_name} character has emerged! Quickly, head to /guess [Name] to reveal its name! 🌟",
            parse_mode='Markdown'
        )

async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Ensure there's a last character for the current chat
    if chat_id not in last_characters:
        await update.message.reply_text("No character to guess at the moment. Please wait for one to spawn!")
        return

    if chat_id in first_correct_guesses:
        return

    # Prepare the guess
    guess = ' '.join(context.args).lower() if context.args else ''

    # Prevent certain characters in the guess
    if "()" in guess or "&" in guess.lower():
        await update.message.reply_text("Nahh, you can't use those types of words in your guess..❌️")
        return

    # Normalize and split the character's name for comparison
    name_parts = last_characters[chat_id]['name'].lower().split()

    # Check if the guess matches the character's name
    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id
        character = last_characters[chat_id]
        keyboard = [[InlineKeyboardButton(f"See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]

        await update.message.reply_text(
            f'<b><a href="tg://user?id={user_id}">{escape(update.effective_user.first_name)}</a></b> 🎊 You guessed the character!\n\n'
            f'🍁 Name: <b>{last_characters[chat_id]["name"]}</b>\n'
            f'⛩ Anime: <b>{last_characters[chat_id]["anime"]}</b>\n'
            f'🎐 Rarity: <b>{last_characters[chat_id]["rarity"]}</b>\n\n'
            f'This character is now in your harem! Use /mycollection to see your harem.',
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


        user = await user_collection.find_one({'id': user_id})
        if user:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})

            await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})

        elif hasattr(update.effective_user, 'username'):
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
            })


        group_user_total = await group_user_totals_collection.find_one({'user_id': user_id, 'group_id': chat_id})
        if group_user_total:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user_total.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user_total.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$set': update_fields})

            await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$inc': {'count': 1}})

        else:
            await group_user_totals_collection.insert_one({
                'user_id': user_id,
                'group_id': chat_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'count': 1,
            })

        group_info = await top_global_groups_collection.find_one({'group_id': chat_id})
        if group_info:
            update_fields = {}
            if update.effective_chat.title != group_info.get('group_name'):
                update_fields['group_name'] = update.effective_chat.title
            if update_fields:
                await top_global_groups_collection.update_one({'group_id': chat_id}, {'$set': update_fields})

            await top_global_groups_collection.update_one({'group_id': chat_id}, {'$inc': {'count': 1}})

        else:
            await top_global_groups_collection.insert_one({
                'group_id': chat_id,
                'group_name': update.effective_chat.title,
                'count': 1,
            })

    else:
        await update.message.reply_text('Oᴏᴘs! Cʜᴀᴍᴘ Yᴏᴜ Gᴜᴇssᴇᴅ Tʜᴇ Wʀᴏɴɢ Cʜᴀʀᴀᴄᴛᴇʀ Nᴀᴍᴇ... ❌️')


async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text('Aᴛᴛᴇɴᴛɪᴏɴ! Wᴇ Nᴇᴇᴅ Tʜᴇ Cʜᴀʀᴀᴄᴛᴇʀ ID Tᴏ Pʀᴏᴄᴇᴇᴅ. Cᴏᴜʟᴅ Yᴏᴜ Pʟᴇᴀsᴇ Pʀᴏᴠɪᴅᴇ Iᴛ? 🕵️‍♂️')
        return

    character_id = context.args[0]

    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text("Lᴏᴏᴋs Lɪᴋᴇ Yᴏᴜ Hᴀᴠᴇɴ'ᴛ Gᴜᴇssᴇᴅ Aɴʏ Cʜᴀʀᴀᴄᴛᴇʀs Yᴇᴛ! Lᴇᴛ's Dɪᴠᴇ Iɴ Aɴᴅ Sᴛᴀʀᴛ Gᴜᴇssɪɴɢ Sᴏᴍᴇ Fᴀɴᴛᴀsᴛɪᴄ Cʜᴀʀᴀᴄᴛᴇʀs Tᴏɢᴇᴛʜᴇʀ!🎉 ")
        return

    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This Character is Not In your collection')
        return

    user['favorites'] = [character_id]    
    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})
    await update.message.reply_text(f'Character {character["name"]} has been added to your favorite...')


def error_handler(update: Update, context: CallbackContext):
    """Log the error and handle it gracefully."""
    LOGGER.error("An error occurred: %s", context.error)


def main() -> None:
    """Run bot."""
    application.add_handler(CommandHandler(["guess"], guess, block=False))
    application.add_handler(CommandHandler("fav", fav, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    asyncio.create_task(application.run_polling(drop_pending_updates=True))
    application.add_error_handler(error_handler)


if __name__ == "__main__":
    shivuu.start()
    app.start()
    LOGGER.info("Bot started")
    main()
