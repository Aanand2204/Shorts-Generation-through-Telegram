# AI-Powered YouTube Shorts Generator (Telegram Bot & CLI)

A highly modular, extensible AI-powered application that generates and automatically uploads YouTube Shorts from user-provided images and context. It features a fully interactive Telegram Bot interface as well as a powerful CLI.

## 🚀 Features

- **Telegram Bot Interface**: An interactive, easy-to-use Telegram bot that guides you through uploading an image, providing context, and selecting a language. It features dynamic progress updates and a built-in pre-publish review step with inline keyboards for editing metadata.
- **LLM Scripting**: Uses Google GenAI (Gemini) to generate dynamic, vertical video scripts perfectly timed for 15-60 second Shorts.
- **Voice Synthesis**: High-quality text-to-speech using Microsoft Edge TTS natively.
- **Dynamic Video Compositing**: Automatic kinetic zoom/pan effects on static images using MoviePy.
- **Auto Subtitles**: OpenAI Whisper-powered word-level timing for large, engaging, TikTok/Shorts-style captions.
- **YouTube API Integration**: One-click OAuth uploads for seamless Shorts publishing directly from the bot or CLI.

## 🏗️ Architecture

The system is built on a robust, decoupled architecture using **Dependency Injection (DI)** with abstract base classes (`src/core/interfaces.py`). Every provider (LLM, TTS, Video editing, YouTube Upload) is completely modular and replaceable without touching the core orchestration logic. The Telegram bot interface (`src/bot`) acts as a conversational frontend to the underlying video generation engine.

## 🛠️ Setup Instructions

### 1. Install System Requirements
Ensure you have `ffmpeg` installed for MoviePy and Whisper text-level transcriptions:
- **Windows**: Use winget or chocolatey (`winget install ffmpeg`) or download from https://www.gyan.dev/ffmpeg/builds/
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 2. Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv teleenv

# Activate on Windows: 
.\teleenv\Scripts\activate

# Activate on Mac/Linux: 
source teleenv/bin/activate
```
Install Python requirements:
```bash
pip install -r requirements.txt
```

### 3. API Keys & Configuration
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Ensure you fill in your `.env` variables:
- `GEMINI_API_KEY`: Your API key from Google AI Studio.
- `TELEGRAM_BOT_TOKEN`: The token for your Telegram Bot (obtained from BotFather).

*(Optional)* If you plan to use the auto-upload feature to publish to YouTube, you must download your OAuth `client_secrets.json` from the Google Cloud Console and place it in the `credentials/` folder.

## 💻 Running the Application

### Method A: Telegram Bot Interface (Recommended)
Launch the bot directly using `main.py` with no arguments.
```bash
python main.py
```
Once running, simply message your bot on Telegram `/start` to begin the interactive generation process!

### Method B: Command Line Interface (CLI)
You can completely bypass the bot and generate shorts directly from your terminal:
```bash
python main.py --image "sample.jpg" --context "A motivational story about perseverance" --language "English"
```

To automatically upload to YouTube via the CLI (requires `credentials/client_secrets.json`):
```bash
python main.py --image "sample.jpg" --context "A motivational story about perseverance" --upload
```
