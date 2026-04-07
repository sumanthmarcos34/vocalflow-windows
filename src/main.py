"""
VocalFlow for Windows
Main entry point - initializes all services and starts the app.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, VERSION, HOTKEY, DEEPGRAM_API_KEY, GROQ_API_KEY
from audio_engine import AudioEngine
from deepgram_service import DeepgramService
from groq_service import GroqService
from hotkey_manager import HotkeyManager
from text_injector import TextInjector
from balance_tracker import BalanceTracker
from ui import VocalFlowWindow


class VocalFlow:
    """Main VocalFlow application class."""
    
    def __init__(self):
        self.audio_engine = None
        self.deepgram = None
        self.groq = None
        self.hotkey = None
        self.injector = None
        self.balance_tracker = None
        self.window = None
        self.current_transcript = ""
        self.is_listening = False
        
        self._init_services()
    
    def _init_services(self):
        """Initialize all backend services."""
        print(f"{APP_NAME} v{VERSION} starting...")
        
        # Audio capture
        self.audio_engine = AudioEngine()
        print("Audio engine initialized")
        
        # Deepgram speech-to-text
        self.deepgram = DeepgramService(
            api_key=DEEPGRAM_API_KEY,
            on_transcript=self._on_transcript
        )
        print("Deepgram service initialized")
        
        # Groq post-processing
        self.groq = GroqService(api_key=GROQ_API_KEY)
        print("Groq service initialized")
        
        # Text injection
        self.injector = TextInjector()
        print("Text injector initialized")
        
        # Balance tracker (extra feature)
        self.balance_tracker = BalanceTracker()
        self.balance_tracker.start_auto_refresh(interval=300)
        print("Balance tracker initialized")
        
        # Hotkey manager
        self.hotkey = HotkeyManager(HOTKEY, callback=self._on_hotkey_press)
        print(f"Hotkey registered: {HOTKEY}")
    
    def _on_transcript(self, text: str, is_final: bool):
        """Callback when new transcript is received."""
        self.current_transcript = text
        
        if is_final:
            # Post-process with Groq
            refined = self.groq.refine_text(text)
            self.current_transcript = refined
            print(f"Final transcript: {refined}")
            
            # Update UI if available
            if self.window:
                self.window.add_transcript(refined)
        else:
            print(f"Partial: {text}")
    
    def _on_hotkey_press(self):
        """Callback when hotkey is pressed."""
        print("Hotkey pressed!")
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Start audio capture and streaming to Deepgram."""
        if self.audio_engine and self.deepgram:
            self.is_listening = True
            self.audio_engine.start_stream(self.deepgram)
            self.deepgram.connect()
            print("Started listening...")
            
            if self.window:
                self.window.listening = True
    
    def stop_listening(self):
        """Stop audio capture and close Deepgram connection."""
        if self.audio_engine and self.deepgram:
            self.audio_engine.stop_stream()
            self.deepgram.disconnect()
            self.is_listening = False
            print("Stopped listening.")
            
            if self.window:
                self.window.listening = False
    
    def inject_text(self, text: str):
        """Inject text into the active window."""
        if self.injector:
            active_window = self.injector.get_active_window()
            print(f"Injecting text into: {active_window}")
            self.injector.inject_text(text)
            print("Text injected!")
    
    def run(self):
        """Run the application with PyQt6 UI."""
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        app.vocalflow = self
        
        self.window = VocalFlowWindow(app)
        self.window.show()
        
        # Initial balance fetch
        self.balance_tracker.fetch_all_balances()
        dg = self.balance_tracker.format_balance("deepgram")
        groq = self.balance_tracker.format_balance("groq")
        self.window.update_balances(dg, groq)
        
        sys.exit(app.exec())
    
    def cleanup(self):
        """Clean up all resources."""
        print("Cleaning up...")
        self.stop_listening()
        if self.hotkey:
            self.hotkey.unregister()
        if self.balance_tracker:
            self.balance_tracker.stop_auto_refresh()


def main():
    """Entry point."""
    try:
        app = VocalFlow()
        app.run()
    except KeyboardInterrupt:
        print("Interrupted.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'app' in locals():
            app.cleanup()


if __name__ == "__main__":
    main()
