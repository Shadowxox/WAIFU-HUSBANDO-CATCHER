from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from shivu import application, top_global_groups_collection, pm_users, OWNER_ID, sudo_users

# Make sure OWNER_ID is in sudo_users
if OWNER_ID not in sudo_users:
    sudo_users.append(OWNER_ID)

# Cache to hold pending broadcast requests
broadcast_cache = {}

async def boardcast(update: Update, context: CallbackContext) -> None:
    sender_id = str(update.effective_user.id)

    if sender_id not in sudo_users:
        await update.message.reply_text("🚫 You don't have permission to use this command.")
        return

    # Handle message input
    if update.message.reply_to_message:
        message = update.message.reply_to_message
        broadcast_cache[sender_id] = {'type': 'forward', 'chat_id': message.chat_id, 'msg_id': message.message_id}
    elif context.args:
        broadcast_cache[sender_id] = {'type': 'text', 'text': " ".join(context.args)}
    else:
        await update.message.reply_text("⚠️ Please reply to a message or provide text to broadcast.")
        return

    # Ask for confirmation
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm", callback_data="confirm_broadcast")]])
    await update.message.reply_text("⚠️ Are you sure you want to send this broadcast to all users?", reply_markup=keyboard)

async def confirm_broadcast_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    sender_id = str(query.from_user.id)

    if sender_id not in broadcast_cache:
        await query.edit_message_text("❌ No pending broadcast found.")
        return

    data = broadcast_cache.pop(sender_id)
    all_chats = await top_global_groups_collection.distinct("group_id")
    all_users = await pm_users.distinct("_id")
    all_targets = list(set(all_chats + all_users))

    failed_sends = 0
    pin_success = 0
    pin_fail = 0

    for chat_id in all_targets:
        try:
            if data['type'] == 'forward':
                sent_msg = await context.bot.forward_message(
                    chat_id=chat_id,
                    from_chat_id=data['chat_id'],
                    message_id=data['msg_id']
                )
            else:
                sent_msg = await context.bot.send_message(chat_id=chat_id, text=data['text'])

            # Try to pin
            try:
                await context.bot.pin_chat_message(chat_id=chat_id, message_id=sent_msg.message_id, disable_notification=True)
                pin_success += 1
            except Exception:
                pin_fail += 1

        except Exception:
            failed_sends += 1

    summary = (
        f"📢 Broadcast Completed\n"
        f"📬 Total Targets: {len(all_targets)}\n"
        f"❌ Failed Sends: {failed_sends}\n"
        f"📌 Pinned: {pin_success}\n"
        f"🚫 Pin Failures: {pin_fail}"
    )

    # Edit confirmation message
    await query.edit_message_text("✅ Broadcast sent.")

    # Send detailed report to OWNER
    await context.bot.send_message(chat_id=OWNER_ID, text=summary)

# Handlers
application.add_handler(CommandHandler("boardcast", boardcast, block=False))
application.add_handler(CallbackQueryHandler(confirm_broadcast_callback, pattern="^confirm_broadcast$"))
