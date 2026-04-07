"""Deepgram Service - WebSocket streaming to Deepgram for real-time ASR"""

import websocket
import json
import threading
from typing import Callable, Optional, List
from config import SAMPLE_RATE, DEEPGRAM_MODEL, DEEPGRAM_LANGUAGE


class DeepgramModel:
    """Represents a Deepgram model."""
    def __init__(self, canonical_name: str, display_name: str, languages: List[str]):
        self.canonical_name = canonical_name
        self.display_name = display_name
        self.languages = languages
        self.id = canonical_name

    def __repr__(self):
        return f"DeepgramModel({self.display_name})"


class DeepgramService:
    """Handles WebSocket communication with Deepgram for speech-to-text."""
    
    def __init__(self):
        self.ws: Optional[websocket.WebSocket] = None
        self.ws_thread: Optional[threading.Thread] = None
        self.is_connected = False
        self.is_waiting_for_final = False
        self.accumulated_transcript = ""
        self.final_transcript_callback: Optional[Callable[[str], None]] = None
        self.interim_transcript_callback: Optional[Callable[[str], None]] = None
        self._recv_thread: Optional[threading.Thread] = None
        
    def connect(self, api_key: str, model: str = None, language: str = None,
                final_callback: Callable[[str], None] = None,
                interim_callback: Callable[[str], None] = None) -> bool:
        """Connect to Deepgram WebSocket API."""
        if not api_key:
            print("Deepgram API key is required")
            return False
            
        model = model or DEEPGRAM_MODEL
        language = language or DEEPGRAM_LANGUAGE
        
        self.final_transcript_callback = final_callback
        self.interim_transcript_callback = interim_callback
        self.accumulated_transcript = ""
        self.is_waiting_for_final = False
        
        # Build WebSocket URL with query parameters
        url = (
            f"wss://api.deepgram.com/v1/listen?"
            f"encoding=linear16&"
            f"sample_rate={SAMPLE_RATE}&"
            f"channels=1&"
            f"model={model}&"
            f"language={language}&"
            f"punctuate=true&"
            f"interim_results=true&"
            f"vad_events=true"
        )
        
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(url, header={"Authorization": f"Token {api_key}"})
            self.is_connected = True
            
            # Start receive thread
            self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._recv_thread.start()
            
            print(f"Connected to Deepgram with model: {model}")
            return True
        except Exception as e:
            print(f"Error connecting to Deepgram: {e}")
            return False
    
    def send_audio(self, audio_data: bytes) -> None:
        """Send audio data to Deepgram."""
        if self.ws and self.is_connected:
            try:
                self.ws.send_binary(audio_data)
            except Exception as e:
                print(f"Error sending audio to Deepgram: {e}")
                self.is_connected = False
    
    def close(self) -> str:
        """Close the WebSocket connection and return the final transcript."""
        self.is_waiting_for_final = True
        
        # Send empty frame to signal end of speech
        if self.ws and self.is_connected:
            try:
                self.ws.send_binary(b"")
            except:
                pass
        
        # Wait a bit for final response
        import time
        time.sleep(2)
        
        self.disconnect()
        return self.accumulated_transcript
    
    def disconnect(self) -> None:
        """Disconnect from Deepgram."""
        self.is_connected = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None
    
    def _receive_loop(self) -> None:
        """Receive messages from Deepgram WebSocket."""
        while self.is_connected and self.ws:
            try:
                message = self.ws.recv()
                if message:
                    self._handle_message(message)
            except Exception as e:
                if self.is_waiting_for_final:
                    break
                print(f"Error receiving from Deepgram: {e}")
                self.is_connected = False
    
    def _handle_message(self, message: str) -> None:
        """Handle a message from Deepgram."""
        try:
            response = json.loads(message)
            channel = response.get("channel", {})
            alternatives = channel.get("alternatives", [])
            
            if alternatives:
                transcript = alternatives[0].get("transcript", "")
                is_final = response.get("is_final", False)
                
                if is_final and transcript:
                    if self.accumulated_transcript:
                        self.accumulated_transcript += " "
                    self.accumulated_transcript += transcript
                    if self.interim_transcript_callback:
                        self.interim_transcript_callback(transcript)
                else:
                    if self.interim_transcript_callback:
                        self.interim_transcript_callback(transcript)
                
                # Check if speech is final
                if self.is_waiting_for_final and response.get("speech_final", False):
                    if self.final_transcript_callback:
                        self.final_transcript_callback(self.accumulated_transcript)
                    self.disconnect()
                    
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error handling Deepgram message: {e}")
    
    def fetch_models(self, api_key: str) -> List[DeepgramModel]:
        """Fetch available Deepgram models."""
        import requests
        models = []
        try:
            response = requests.get(
                "https://api.deepgram.com/v1/models",
                headers={"Authorization": f"Token {api_key}"}
            )
            if response.status_code == 200:
                data = response.json()
                stt_models = data.get("stt", [])
                for m in stt_models:
                    canonical = m.get("canonical_name", "")
                    if canonical and m.get("streaming", False):
                        models.append(DeepgramModel(
                            canonical_name=canonical,
                            display_name=m.get("name", canonical),
                            languages=m.get("languages", [])
                        ))
        except Exception as e:
            print(f"Error fetching Deepgram models: {e}")
        return models
