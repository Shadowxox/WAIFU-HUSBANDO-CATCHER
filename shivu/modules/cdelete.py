from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, sudo_users, user_collection


async def cdelete(update: Update, context: CallbackContext) -> None:
    sender_id = update.effective_user.id

    # 🔒 Sudo check
    if sender_id not in sudo_users:
        return await update.message.reply_text("🚫 You are not authorized to use this command.")

    # ✅ Input via /cdelete waifu_id quantity [username_or_id]
    if len(context.args) < 2:
        return await update.message.reply_text("❌ Usage: /cdelete <waifu_id> <quantity> [username or user_id] or reply to user.")

    waifu_id = context.args[0]
    try:
        quantity = int(context.args[1])
        if quantity < 1:
            raise ValueError
    except ValueError:
        return await update.message.reply_text("❌ Quantity must be a positive number.")

    # 🎯 Determine target user
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif len(context.args) >= 3:
        try:
            target_input = context.args[2]
            if target_input.startswith("@"):
                user_data = await user_collection.find_one({"username": target_input[1:]})
            else:
                user_data = await user_collection.find_one({"id": int(target_input)})
            if not user_data:
                return await update.message.reply_text("❌ User not found.")
            target_id = user_data["id"]
        except Exception:
            return await update.message.reply_text("❌ Could not resolve user.")
    else:
        return await update.message.reply_text("❌ Please reply to a user or provide username/user_id.")

    # 🔍 Load user and delete
    user = await user_collection.find_one({"id": target_id})
    if not user or "characters" not in user:
        return await update.message.reply_text("❌ User has no characters.")

    chars = user["characters"]
    new_chars = []
    deleted = 0

    for char in chars:
        if char["id"] == waifu_id and deleted < quantity:
            deleted += 1
            continue
        new_chars.append(char)

    if deleted == 0:
        return await update.message.reply_text("❌ Waifu not found or nothing to delete.")

    await user_collection.update_one({"id": target_id}, {"$set": {"characters": new_chars}})
    await update.message.reply_text(
        f"✅ Deleted `{deleted}` waifu(s)` with ID `{waifu_id}` from user `{target_id}`.",
        parse_mode="Markdown"
    )

# Register
application.add_handler(CommandHandler("cdelete", cdelete, block=False))
