import os
import uuid
import asyncio

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.logger import get_logger
from src.bot.states import WAIT_IMAGE, WAIT_CONTEXT, WAIT_LANGUAGE
from src.bot.engine import engine
from src.bot.handlers.approval import send_approval_message

logger = get_logger("bot.generation")

# Ensure directories exist
os.makedirs("output/uploads", exist_ok=True)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for context."""
    user = update.message.from_user
    
    # Check if a photo was actually sent
    if not update.message.photo:
         await update.message.reply_text("Please send an image (as a photo, not as a document file).")
         return WAIT_IMAGE
        
    photo_file = await update.message.photo[-1].get_file()
    
    task_id = str(uuid.uuid4())
    ext = ".jpg"
    image_path = os.path.join("output", "uploads", f"{task_id}{ext}")
    
    # Download the photo
    await photo_file.download_to_drive(custom_path=image_path)
    
    context.user_data['image_path'] = image_path
    logger.info(f"Photo downloaded for user {user.username} to {image_path}")

    await update.message.reply_text(
        "Great! Now, please reply with the *context* or topic for the script (e.g., 'Motivational success quotes', 'Horror story about the deep ocean').",
        parse_mode="Markdown"
    )
    return WAIT_CONTEXT

async def handle_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the context and asks for language."""
    context.user_data['script_context'] = update.message.text
    
    # Provide a simple keyboard for common languages
    reply_keyboard = [["English", "Spanish", "Hindi"]]
    
    await update.message.reply_text(
        "Awesome! Finally, tell me what *language* I should use for the voiceover and script (e.g., English, Hindi, Spanish).",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Language?"
        ),
    )
    return WAIT_LANGUAGE

async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the language and begins the generation process."""
    language = update.message.text.strip()
    
    image_path = context.user_data.get('image_path')
    script_context = context.user_data.get('script_context')
    
    # Acknowledge and remove keyboard
    await update.message.reply_text("Got it!", reply_markup=ReplyKeyboardRemove())
    status_message = await update.message.reply_text(
        "Perfect! I am starting the generation process. This may take a few minutes..."
    )
    
    # We define a progress hook to update the telegram message
    def ui_progress_hook(progress_value, msg):
        async def edit_msg():
            try:
                bar_length = 10
                filled = int(bar_length * progress_value)
                bar = "█" * filled + "░" * (bar_length - filled)
                percentage = int(progress_value * 100)
                
                text = f"⚙️ *Generating Short...*\n\n{msg}\n\nProgress: [{bar}] {percentage}%"
                await status_message.edit_text(text, parse_mode="Markdown")
            except Exception:
                pass
                
        asyncio.create_task(edit_msg())

    try:
        # Run generation pipeline
        assets = await engine.generate_assets(
            image_path=image_path,
            context=script_context,
            language=language,
            ui_progress_hook=ui_progress_hook
        )
        
        context.user_data['assets'] = assets
        
        # Cleanup the progress message
        try:
            await status_message.delete()
        except:
            pass
            
        return await send_approval_message(update, context)

    except Exception as e:
        logger.exception("Pipeline failed:")
        await update.message.reply_text(f"❌ *An error occurred during generation:*\n\n`{str(e)}`", parse_mode="Markdown")
        return ConversationHandler.END
