import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.logger import get_logger
from src.bot.states import WAIT_APPROVAL, EDIT_TITLE, EDIT_DESCRIPTION, EDIT_TAGS
from src.bot.engine import engine

logger = get_logger("bot.approval")

async def send_approval_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends the generated metadata with inline keyboard for approval or edits."""
    assets = context.user_data['assets']
    meta = assets['metadata']
    
    text = (
        f"✅ <b>Video Generation Complete!</b>\n\n"
        f"Please review the YouTube metadata before I upload:\n\n"
        f"📌 <b>Title:</b> {meta.get('title', '')}\n\n"
        f"📝 <b>Description:</b>\n{meta.get('description', '')}\n\n"
        f"🏷️ <b>Tags:</b> {meta.get('tags', '')}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Approve & Upload", callback_data="approve")],
        [InlineKeyboardButton("✏️ Edit Title", callback_data="edit_title"),
         InlineKeyboardButton("✏️ Edit Description", callback_data="edit_desc")],
        [InlineKeyboardButton("✏️ Edit Tags", callback_data="edit_tags")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Handle both message replies (if coming from text edit) or callback query edits
    if update.callback_query:
        await update.callback_query.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
    return WAIT_APPROVAL

async def handle_approval_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles inline keyboard clicks."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    if choice == "approve":
        await query.edit_message_text("⏳ *Uploading to YouTube...*\n\nPlease wait.", parse_mode="Markdown")
        return await execute_upload(update, context)
        
    elif choice == "cancel":
        await query.edit_message_text("❌ *Upload Cancelled.*\n\nSend /start to begin a new generation.", parse_mode="Markdown")
        return ConversationHandler.END
        
    elif choice == "edit_title":
        await query.message.reply_text("Please reply with the new *Title*:", parse_mode="Markdown")
        return EDIT_TITLE
        
    elif choice == "edit_desc":
        await query.message.reply_text("Please reply with the new *Description*:", parse_mode="Markdown")
        return EDIT_DESCRIPTION
        
    elif choice == "edit_tags":
        await query.message.reply_text("Please reply with the new *Tags* (comma separated):", parse_mode="Markdown")
        return EDIT_TAGS

    return WAIT_APPROVAL

async def handle_edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['assets']['metadata']['title'] = update.message.text.strip()
    return await send_approval_message(update, context)

async def handle_edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['assets']['metadata']['description'] = update.message.text.strip()
    return await send_approval_message(update, context)

async def handle_edit_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['assets']['metadata']['tags'] = update.message.text.strip()
    return await send_approval_message(update, context)

async def execute_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Actually performs the YouTube upload and sends the success message."""
    assets = context.user_data['assets']
    query = update.callback_query
    
    try:
        youtube_url = engine.upload_to_youtube(assets['video_path'], assets['metadata'])
        
        response_text = (
            f"🎉 <b>Success! Your Short is live.</b>\n\n"
            f"<b>Title:</b> {assets['metadata'].get('title', '')}\n\n"
            f"📺 <b>YouTube URL:</b> {youtube_url}"
        )
        await query.message.reply_text(response_text, parse_mode="HTML")
        
        # Try to upload raw video to telegram, handling 50MB limit
        video_size_mb = os.path.getsize(assets['video_path']) / (1024 * 1024)
        if video_size_mb < 49.5:  # safe margin
            await query.message.reply_video(video=open(assets['video_path'], 'rb'), caption="Here is the raw video file.")
        else:
            await query.message.reply_text(f"<i>(Note: The raw video file is {video_size_mb:.1f}MB, which exceeds Telegram's 50MB bot upload limit, so it cannot be directly sent here. Your YouTube upload was successful though!)</i>", parse_mode="HTML")

    except Exception as e:
        logger.exception("Upload failed:")
        await query.message.reply_text(f"❌ <b>An error occurred during upload:</b>\n\n<code>{str(e)}</code>", parse_mode="HTML")

    return ConversationHandler.END
