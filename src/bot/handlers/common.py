from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.states import WAIT_IMAGE

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user for an image."""
    await update.message.reply_text(
        "Welcome to the AI YouTube Shorts Generator! 🎬\n\n"
        "Let's create a new short. Please send me an *image* to get started.",
        parse_mode="Markdown"
    )
    return WAIT_IMAGE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Generation cancelled. Send /start to begin again.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
