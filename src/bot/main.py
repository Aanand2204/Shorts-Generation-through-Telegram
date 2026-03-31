import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
)

from src.utils.logger import get_logger
from src.bot.states import (
    WAIT_IMAGE, WAIT_CONTEXT, WAIT_LANGUAGE,
    WAIT_APPROVAL, EDIT_TITLE, EDIT_DESCRIPTION, EDIT_TAGS
)
from src.bot.handlers.common import start, cancel
from src.bot.handlers.generation import handle_image, handle_context, handle_language
from src.bot.handlers.approval import (
    handle_approval_choice, handle_edit_title, handle_edit_description, handle_edit_tags
)

load_dotenv()

logger = get_logger("bot")

def start_bot():
    """Starts the bot polling loop."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables. Cannot start bot.")
        return
        
    application = Application.builder().token(token).build()

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAIT_IMAGE: [MessageHandler(filters.PHOTO | filters.TEXT, handle_image)],
            WAIT_CONTEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_context)],
            WAIT_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language)],
            WAIT_APPROVAL: [CallbackQueryHandler(handle_approval_choice)],
            EDIT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_title)],
            EDIT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_description)],
            EDIT_TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_tags)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot starting polling loop...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
