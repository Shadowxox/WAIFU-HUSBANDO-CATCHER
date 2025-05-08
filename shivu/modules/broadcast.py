from telegram import Update, Message, Chat
from telegram.ext import CommandHandler, ContextTypes
from shivu import application, pm_users, group_users, OWNER_ID

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("You are not authorized.")

    if update.message.reply_to_message:
        to_broadcast = update.message.reply_to_message
    elif context.args:
        text = " ".join(context.args)
        to_broadcast = await update.message.reply_text(text)
    else:
        return await update.message.reply_text("Reply to a message or use:\n`/broadcast your message`", parse_mode="Markdown")

    success = 0
    failed = 0
    pinned = 0
    group_names = []

    # Send to PM users
    async for user in pm_users.find({}):
        try:
            await to_broadcast.copy(chat_id=user["_id"])
            success += 1
        except:
            failed += 1

    # Send to groups & try pin
    async for group in group_users.find({}):
        group_id = group["_id"]
        group_name = group.get("title", "Unknown")
        try:
            msg = await to_broadcast.copy(chat_id=group_id)
            try:
                await context.bot.pin_chat_message(chat_id=group_id, message_id=msg.message_id)
                pinned += 1
            except:
                pass
            group_names.append(group_name)
            success += 1
        except:
            failed += 1

    # Report to owner
    report = (
        f"📢 Broadcast Report:\n"
        f"Group Names: {', '.join(group_names) or 'None'}\n"
        f"Success: {success}\n"
        f"Pined: {pinned}\n"
        f"Unsuccess: {failed}"
    )
    try:
        await context.bot.send_message(chat_id=OWNER_ID, text=report)
    except:
        pass

    await update.message.reply_text("✅ Broadcast sent. Report delivered to owner.")

# Add handler
application.add_handler(CommandHandler("broadcast", broadcast, block=False))
