import edge_tts
from src.core.interfaces import IVoiceGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)

LANGUAGE_VOICES = {
    "English": "en-US-ChristopherNeural",
    "Spanish": "es-ES-AlvaroNeural",
    "French": "fr-FR-HenriNeural",
    "German": "de-DE-KillianNeural",
    "Hindi": "hi-IN-MadhurNeural",
    "Italian": "it-IT-DiegoNeural",
    "Portuguese": "pt-BR-AntonioNeural",
    "Japanese": "ja-JP-KeitaNeural",
    "Korean": "ko-KR-InJoonNeural",
    "Russian": "ru-RU-DmitryNeural",
    "Arabic": "ar-AE-HamdanNeural",
    "Chinese": "zh-CN-YunxiNeural"
}

class EdgeTTSProvider(IVoiceGenerator):
    def __init__(self, default_voice: str = "en-US-ChristopherNeural"):
        self.default_voice = default_voice

    async def generate_voice(self, script: str, output_path: str, language: str = "English") -> str:
        voice = LANGUAGE_VOICES.get(language.capitalize(), self.default_voice)
        logger.info(f"Generating voice using Edge TTS ({voice}) for language {language}...")
        communicate = edge_tts.Communicate(script, voice)
        
        words = []
        with open(output_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # Convert 100-nanosecond ticks to seconds
                    start = chunk["offset"] / 10000000.0
                    duration = chunk["duration"] / 10000000.0
                    words.append({
                        "text": chunk["text"],
                        "start": start,
                        "end": start + duration
                    })
                    
        import json
        json_path = output_path.replace(".wav", ".json")
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(words, file)
            
        logger.info(f"Voice saved to {output_path} and timestamps to {json_path}")
        return output_path
