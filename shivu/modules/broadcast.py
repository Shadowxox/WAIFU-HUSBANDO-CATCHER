from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from shivu import application, sudo_users, pm_users as pm_collection, group_users as group_collection

pending_broadcasts = {}

async def broadcast_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in sudo_users:
        return await update.message.reply_text("🚫 You're not authorized to use this command.")

    reply: Message = update.message.reply_to_message
    text = " ".join(context.args) if context.args else None

    if not reply and not text:
        return await update.message.reply_text("Reply to a message or use /broadcast <text>.")

    pending_broadcasts[user_id] = {
        "text": text,
        "reply": reply
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data="confirm_broadcast"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")]
    ])

    preview = text if text else "[Media reply]"
    await update.message.reply_text(
        f"⚠️ Are you sure you want to broadcast this?\n\n{preview}",
        reply_markup=keyboard
    )

async def broadcast_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in sudo_users:
        return await query.edit_message_text("🚫 Not authorized.")

    if query.data == "cancel_broadcast":
        pending_broadcasts.pop(user_id, None)
        return await query.edit_message_text("❌ Broadcast cancelled.")

    data = pending_broadcasts.get(user_id)
    if not data:
        return await query.edit_message_text("⚠️ Nothing to broadcast.")

    await query.edit_message_text("📢 Broadcasting...")

    total_success = 0
    total_failed = 0
    total_pinned = 0

    # Send to private users
    async for user in pm_collection.find():
        try:
            if data["reply"]:
                await data["reply"].copy(user["_id"])
            else:
                await context.bot.send_message(chat_id=user["_id"], text=data["text"])
            total_success += 1
        except Exception:
            total_failed += 1

    # Send to groups
    async for group in group_collection.find():
        group_id = group["_id"]
        gc_name = group.get("title", "Unknown Group")
        gc_success = 0
        gc_failed = 0
        gc_pinned = 0

        try:
            if data["reply"]:
                sent_msg = await data["reply"].copy(group_id)
            else:
                sent_msg = await context.bot.send_message(chat_id=group_id, text=data["text"])
            gc_success += 1
            total_success += 1

            try:
                await context.bot.pin_chat_message(group_id, sent_msg.message_id, disable_notification=True)
                gc_pinned += 1
                total_pinned += 1
            except:
                pass

        except Exception:
            gc_failed += 1
            total_failed += 1

        # Report per group
        report = f"""📊 <b>Broadcast Report</b>
<b>GC Name:</b> {gc_name}
<b>Success:</b> ✅ {gc_success}
<b>Pinned:</b> 📌 {gc_pinned}
<b>Unsuccess:</b> ❌ {gc_failed}
"""
        for owner_id in sudo_users:
            try:
                await context.bot.send_message(chat_id=owner_id, text=report, parse_mode="HTML")
            except:
                pass

    # Final Summary
    summary = f"""✅ <b>Broadcast Finished</b>
<b>Total Sent:</b> {total_success}
<b>Total Pinned:</b> {total_pinned}
<b>Failed:</b> {total_failed}
"""
    for owner_id in sudo_users:
        try:
            await context.bot.send_message(chat_id=owner_id, text=summary, parse_mode="HTML")
        except:
            pass

    pending_broadcasts.pop(user_id, None)

# Register handlers
application.add_handler(CommandHandler("broadcast", broadcast_command, block=False))
application.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^(confirm_broadcast|cancel_broadcast)$", block=False))
