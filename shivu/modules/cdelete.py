from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from shivu import application, sudo_users

VIP_SUDO = [7795212861]  # Special sudo user who can do everything


def is_vip_sudo(user_id: int) -> bool:
    return user_id in VIP_SUDO


async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_vip_sudo(user_id):
        await update.message.reply_text("❌ Only VIP sudo users can use this command.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to add them as sudo.")
        return

    target_id = update.message.reply_to_message.from_user.id
    if target_id in sudo_users:
        await update.message.reply_text("✅ User is already a sudo.")
        return

    sudo_users.append(target_id)
    await update.message.reply_text(f"✅ Added user {target_id} to sudo list.")


async def rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_vip_sudo(user_id):
        await update.message.reply_text("❌ Only VIP sudo users can use this command.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to remove them from sudo.")
        return

    target_id = update.message.reply_to_message.from_user.id
    if target_id not in sudo_users:
        await update.message.reply_text("❌ User is not in sudo list.")
        return

    sudo_users.remove(target_id)
    await update.message.reply_text(f"✅ Removed user {target_id} from sudo list.")


async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "**🔐 Current Sudo Users:**\n"
    for uid in sudo_users:
        try:
            user = await application.bot.get_chat(uid)
            mention = f"[{user.first_name}](tg://user?id={uid})"
        except Exception:
            mention = f"`{uid}`"
        text += f"• {mention}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


# Register handlers
application.add_handler(CommandHandler("addsudo", addsudo, block=False))
application.add_handler(CommandHandler("rmsudo", rmsudo, block=False))
application.add_handler(CommandHandler("listsudo", listsudo, block=False))
