from telegram import Update, Chat, ChatInviteLink
from telegram.ext import CallbackContext, CommandHandler
from shivu import application, top_global_groups_collection, pm_users, OWNER_ID, SUDOERS

async def broadcast(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id != OWNER_ID and user_id not in SUDOERS:
        await update.message.reply_text("You're not allowed to use this command.")
        return

    reply_msg = update.message.reply_to_message
    if not reply_msg:
        await update.message.reply_text("Please reply to a message to broadcast.")
        return

    group_ids = await top_global_groups_collection.distinct("group_id")
    user_ids = await pm_users.distinct("_id")
    all_chats = list(set(group_ids + user_ids))

    sent = 0
    failed = 0
    pinned = 0
    pin_failed = 0
    group_report = []

    for chat_id in all_chats:
        try:
            sent_msg = await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=reply_msg.chat_id,
                message_id=reply_msg.message_id
            )
            sent += 1

            chat = await context.bot.get_chat(chat_id)
            if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
                try:
                    await context.bot.pin_chat_message(chat_id=chat_id, message_id=sent_msg.message_id)
                    pinned += 1

                    try:
                        invite_link = chat.username and f"https://t.me/{chat.username}" or "Private group"
                        group_report.append(f"✅ {chat.title or chat_id} - {invite_link}")
                    except:
                        group_report.append(f"✅ {chat.title or chat_id} - [Invite link error]")
                except:
                    pin_failed += 1
                    group_report.append(f"⚠️ {chat.title or chat_id} - Failed to pin")

        except Exception as e:
            failed += 1
            print(f"Failed to send to {chat_id}: {e}")

    report = (
        f"📣 Broadcast Report:\n"
        f"👥 Total chats/users: {len(all_chats)}\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}\n"
        f"📌 Pinned: {pinned}\n"
        f"⚠️ Pin Failed: {pin_failed}\n\n"
        f"📋 Group Results:\n" + "\n".join(group_report[:50])  # Limit to 50 lines for length
    )

    await context.bot.send_message(chat_id=OWNER_ID, text=report)

application.add_handler(CommandHandler("broadcast", broadcast, block=False))
