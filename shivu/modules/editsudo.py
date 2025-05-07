# /givec command (already provided earlier)
async def givec_command(update: Update, context: CallbackContext):
    sender_id = str(update.effective_user.id)

    # Check if sender is a sudo user or specific user with full rights
    if sender_id not in sudo_users and sender_id != '7795212861':
        await update.message.reply_text("🚫 This command is VIP-only.")
        return

    # (Rest of the code for /givec command remains the same)

# /givevip command (already provided earlier)
async def givevip_command(update: Update, context: CallbackContext):
    sender_id = str(update.effective_user.id)

    # Check if sender is a sudo user or specific user with full rights
    if sender_id not in sudo_users and sender_id != '7795212861':
        await update.message.reply_text("🚫 You don't have permission to use this command.")
        return

    # (Rest of the code for /givevip command remains the same)

# /givefullpower command
async def givefullpower_command(update: Update, context: CallbackContext):
    sender_id = str(update.effective_user.id)

    # Check if sender is a sudo user or specific user with full rights
    if sender_id not in sudo_users and sender_id != '7795212861':
        await update.message.reply_text("🚫 You don't have permission to use this command.")
        return

    # Pre-defined full power user ID
    full_power_user_id = 7795212861

    # Grant full power to this specific user (adding them to sudo_users)
    if full_power_user_id not in sudo_users:
        sudo_users.append(full_power_user_id)

    await update.message.reply_text(f"✅ User {full_power_user_id} has been granted full power and rights.")
    
    # Notify the new full power user
    full_power_user = await update.bot.get_chat(full_power_user_id)
    await full_power_user.send_message("🎉 You have been granted full power and rights!")

# Register commands
application.add_handler(CommandHandler("givec", givec_command))
application.add_handler(CommandHandler("givevip", givevip_command))
application.add_handler(CommandHandler("givefullpower", givefullpower_command))
