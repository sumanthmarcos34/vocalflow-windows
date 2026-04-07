# VocalFlow for Windows

A Windows clone of [VocalFlow](https://github.com/Vocallabsai/vocalflow) - an AI-powered voice-to-text dictation app built with Python and PyQt6.

## Features

- **Hold-to-Record**: Press a configurable hotkey to start/stop dictation
- **Real-time Transcription**: Deepgram ASR provides live speech-to-text streaming
- **Post-processing**: Groq API refines transcripts for better accuracy
- **Text Injection**: Automatically type transcribed text into any active application
- **System Tray UI**: Lightweight PyQt6 interface with transcript display
- **Balance Tracking** (Extra Feature): Display Deepgram and Groq API balance/usage

## Extra Features (Beyond Original)

- **Deepgram Balance Display**: Shows your Deepgram account balance in the UI
- **Groq Usage Display**: Tracks Groq API token usage and estimated costs
- **Auto-refresh**: Balances update automatically every 5 minutes

## Project Structure

```
vocalflow-windows/
├── README.md
├── requirements.txt
├── .gitignore
└── src/
    ├── main.py              # Application entry point
    ├── config.py            # Configuration and API keys
    ├── audio_engine.py      # PyAudio microphone capture
    ├── deepgram_service.py  # Deepgram WebSocket ASR
    ├── groq_service.py      # Groq API post-processing
    ├── hotkey_manager.py    # Windows global hotkey (ctypes)
    ├── text_injector.py     # Keyboard simulation/text injection
    ├── balance_tracker.py   # API balance fetching (extra feature)
    └── ui.py                # PyQt6 system tray interface
```

## Installation

### Prerequisites

- Windows 10/11
- Python 3.9+
- Microphone

### Setup

1. Clone the repository:
```bash
git clone https://github.com/sumanthmarcos34/vocalflow-windows.git
cd vocalflow-windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys in `src/config.py`:
```python
DEEPGRAM_API_KEY = "your_deepgram_key_here"
GROQ_API_KEY = "your_groq_key_here"
```

4. Run the application:
```bash
cd src
python main.py
```

## Usage

1. **Start the app**: Run `python main.py` from the `src` directory
2. **Listen**: Click "Start Listening" or press `Ctrl+Alt+D` (default hotkey)
3. **Speak**: Dictate text into your microphone
4. **View Transcript**: Transcribed text appears in real-time in the UI
5. **Inject Text**: Click "Inject Last Transcript" to type the text into the active window
6. **Check Balances**: View Deepgram and Groq balance in the API Balances section

## Configuration

Edit `src/config.py` to customize:

- `DEEPGRAM_API_KEY`: Your Deepgram API key (required)
- `GROQ_API_KEY`: Your Groq API key (required)
- `HOTKEY`: Global hotkey combination (default: Ctrl+Alt+D)
- `APP_NAME`: Application name
- `VERSION`: Application version

## How It Works

1. **Audio Capture**: PyAudio captures microphone input and streams it in real-time
2. **Speech Recognition**: Audio is sent to Deepgram via WebSocket for transcription
3. **Post-processing**: Transcripts are refined using Groq's LLM for accuracy
4. **Text Injection**: The app simulates keyboard input to type text into any window
5. **Balance Tracking**: Background thread fetches API balances periodically

## Notes

- Requires a valid Deepgram API key (get one at [deepgram.com](https://deepgram.com))
- Requires a valid Groq API key (get one at [groq.com](https://groq.com))
- The Deepgram key is hardcoded in `config.py` as per the assignment requirements
- For production, use environment variables instead of hardcoded keys

## License

MIT License
