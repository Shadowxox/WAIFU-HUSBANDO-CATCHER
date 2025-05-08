from telegram import Update, Chat
from telegram.ext import CallbackContext, CommandHandler
from shivu import application, top_global_groups_collection, pm_users, OWNER_ID, sudo_users

async def broadcast(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Check permission
    if user_id != OWNER_ID and user_id not in sudo_users:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    # Require reply to message
    if not update.message.reply_to_message:
        await update.message.reply_text("ℹ️ Please reply to a message to broadcast.")
        return

    message_to_broadcast = update.message.reply_to_message
    all_chats = await top_global_groups_collection.distinct("group_id")
    all_users = await pm_users.distinct("_id")
    all_ids = list(set(all_chats + all_users))

    sent_count = 0
    failed_count = 0
    pinned_count = 0
    not_pinned_count = 0
    group_info = []

    for chat_id in all_ids:
        try:
            sent_msg = await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=message_to_broadcast.chat_id,
                message_id=message_to_broadcast.message_id
            )
            sent_count += 1

            # Try to pin if it's a group
            if chat_id < 0:
                try:
                    await context.bot.pin_chat_message(chat_id, sent_msg.message_id)
                    pinned_count += 1
                except:
                    not_pinned_count += 1

                # Try to get group info
                try:
                    chat = await context.bot.get_chat(chat_id)
                    title = chat.title or "No Title"
                    link = f"https://t.me/{chat.username}" if chat.username else "Private Group"
                    group_info.append(f"{title} - {link}")
                except:
                    group_info.append(f"{chat_id} - Unknown Group")

        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
            failed_count += 1

    # Report to OWNER_ID
    report = (
        f"📢 Broadcast Report:\n\n"
        f"✅ Sent: {sent_count}\n"
        f"❌ Failed: {failed_count}\n"
        f"📌 Pinned: {pinned_count}\n"
        f"🚫 Pin Failed: {not_pinned_count}\n\n"
        f"🗂️ Group List:\n" + "\n".join(group_info[:50])  # Limit output size
    )

    await context.bot.send_message(chat_id=OWNER_ID, text=report)

# Register the handler
application.add_handler(CommandHandler("broadcast", broadcast, block=False))
