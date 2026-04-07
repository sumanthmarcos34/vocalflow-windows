# VocalFlow Windows - Configuration
# Hardcoded API keys as per assignment requirements

# Deepgram API Configuration
DEEPGRAM_API_KEY = "YOUR_DEEPGRAM_API_KEY_HERE"
DEEPGRAM_MODEL = "nova-3-general"
DEEPGRAM_LANGUAGE = "en-US"

# Groq API Configuration
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Groq Processing Options
GROQ_CORRECTION_ENABLED = True
GROQ_GRAMMAR_ENABLED = True
GROQ_CODEMIX_ENABLED = False
GROQ_CODEMIX_STYLE = "Hinglish"
GROQ_TARGET_LANGUAGE = ""

# Hotkey Configuration (Windows virtual key codes)
# Options: VK_RMENU (Right Alt), VK_LMENU (Left Alt), VK_RCONTROL, VK_LCONTROL, VK_RSHIFT, VK_LSHIFT
HOTKEY_VK = 0xA5  # VK_RMENU (Right Alt) - default
HOTKEY_MODIFIER = 0x0001  # MOD_ALT

# Audio Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 4096

# Application Settings
APP_NAME = "VocalFlow Windows"
APP_VERSION = "1.0.0"
