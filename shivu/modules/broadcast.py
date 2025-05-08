from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from shivu import application, top_global_groups_collection, pm_users, is_sudo

async def broadcast(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not is_sudo(user_id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    message_to_broadcast = update.message.reply_to_message
    if message_to_broadcast is None:
        await update.message.reply_text("❗ Please reply to a message to broadcast.")
        return

    all_chats = await top_global_groups_collection.distinct("group_id")
    all_users = await pm_users.distinct("_id")

    targets = list(set(all_chats + all_users))
    failed_sends = 0

    for chat_id in targets:
        try:
            await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=message_to_broadcast.chat_id,
                message_id=message_to_broadcast.message_id
            )
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
            failed_sends += 1

    await update.message.reply_text(f"✅ Broadcast complete.\n❌ Failed to send to {failed_sends} users/chats.")

application.add_handler(CommandHandler("broadcast", broadcast, block=False))
