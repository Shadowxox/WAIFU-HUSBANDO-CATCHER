from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Sudo users with special permissions
sudo_users = ["7361967332", "5758240622", "7795212861"]

# /givec command
async def givec_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = str(update.effective_user.id)

    if sender_id not in sudo_users:
        await update.message.reply_text("🚫 This command is VIP-only.")
        return

    await update.message.reply_text("✅ /givec command executed successfully!")

# /givevip command
async def givevip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = str(update.effective_user.id)

    if sender_id not in sudo_users:
        await update.message.reply_text("🚫 You don't have permission to use this command.")
        return

    await update.message.reply_text("✅ /givevip command executed successfully!")

# /givefullpower command
async def givefullpower_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = str(update.effective_user.id)

    if sender_id not in sudo_users:
        await update.message.reply_text("🚫 You don't have permission to use this command.")
        return

    full_power_user_id = "7795212861"

    if full_power_user_id not in sudo_users:
        sudo_users.append(full_power_user_id)

    await update.message.reply_text(f"✅ User {full_power_user_id} has been granted full power and rights!")

    full_power_user = await context.bot.get_chat(full_power_user_id)
    await full_power_user.send_message("🎉 You have been granted full power and rights!")

# Function to start the bot (you call this from Colab or another script)
def start_bot(token: str):
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("givec", givec_command))
    app.add_handler(CommandHandler("givevip", givevip_command))
    app.add_handler(CommandHandler("givefullpower", givefullpower_command))

    print("✅ Bot is running...")
    app.run_polling()
