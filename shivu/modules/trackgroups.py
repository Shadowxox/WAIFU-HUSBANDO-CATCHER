from telegram import ChatInviteLink
from telegram.constants import ChatMemberStatus

async def list_groups(update: Update, context: CallbackContext):
    group_ids = await top_global_groups_collection.distinct("group_id")

    if not group_ids:
        await update.message.reply_text("❌ No group IDs found in the database.")
        return

    results = []
    for gid in group_ids:
        try:
            chat = await context.bot.get_chat(gid)
            name = chat.title or "Unnamed"
            link = "❌ No invite link"

            # Try to get an invite link (if the bot is admin with invite rights)
            try:
                admins = await context.bot.get_chat_administrators(gid)
                bot_admin = next((a for a in admins if a.user.id == context.bot.id), None)

                if bot_admin and bot_admin.can_invite_users:
                    invite_links = await context.bot.export_chat_invite_link(gid)
                    link = invite_links if invite_links else link
            except Exception as e:
                print(f"Couldn't get invite link for {gid}: {e}")

            results.append(f"📌 {name}\n🆔 `{gid}`\n🔗 {link}")

        except Exception as e:
            print(f"Skipping {gid}: {e}")

    message = "\n\n".join(results)
    await update.message.reply_text(message[:4096], parse_mode="Markdown")
