import asyncio
import argparse
import sys
from src.providers.llm_gemini import GeminiProvider
from src.providers.tts_edge import EdgeTTSProvider
from src.providers.video_moviepy import MoviePyProvider
from src.providers.upload_youtube import YouTubeAPIProvider
from src.engine.orchestrator import ShortsGeneratorEngine
from src.utils.logger import get_logger

logger = get_logger("main")

def build_engine() -> ShortsGeneratorEngine:
    """Dependency Injection: Creates instances of all providers."""
    # Instantiating providers
    llm_provider = GeminiProvider()
    tts_provider = EdgeTTSProvider()
    video_provider = MoviePyProvider()
    
    # We load youtube API conditionally or handle its errors if secrets are missing
    youtube_provider = YouTubeAPIProvider()
    
    engine = ShortsGeneratorEngine(
        script_gen=llm_provider,
        voice_gen=tts_provider,
        video_gen=video_provider,
        metadata_gen=llm_provider,
        uploader=youtube_provider
    )
    return engine

async def main():
    parser = argparse.ArgumentParser(description="AI YouTube Shorts Generator")
    parser.add_argument("--image", type=str, required=False, help="Path to input image (CLI mode)")
    parser.add_argument("--context", type=str, required=False, help="Context/topic for the script (CLI mode)")
    parser.add_argument("--language", type=str, default="English", help="Language for the script and voice (default: English)")
    parser.add_argument("--upload", action="store_true", help="Auto-upload to YouTube")
    
    args = parser.parse_args()
    
    # If no CLI args are provided, launch the Telegram Bot
    if not args.image or not args.context:
        logger.info("No CLI arguments provided. Launching Telegram Bot...")
        from src.bot import start_bot
        start_bot()
        return
    
    # Otherwise run the CLI pipeline
    try:
        engine = build_engine()
        video_path, metadata = await engine.generate_short(
            image_path=args.image,
            context=args.context,
            auto_upload=args.upload,
            language=args.language
        )
        logger.info(f"\n[DONE] Successfully generated short at: {video_path}")
        logger.info("Title: " + metadata.get("title", ""))
        logger.info("Description: " + metadata.get("description", ""))
        logger.info("Tags: " + metadata.get("tags", ""))
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        # Launch Telegram Bot directly synchronously
        logger.info("No CLI arguments provided. Launching Telegram Bot...")
        from src.bot import start_bot
        start_bot()
    else:
        asyncio.run(main())
