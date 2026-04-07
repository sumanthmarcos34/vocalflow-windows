"""Audio Engine - Microphone capture and audio processing for VocalFlow Windows"""

import pyaudio
import numpy as np
import threading
import queue
import struct
from typing import Callable, Optional
from config import SAMPLE_RATE, CHANNELS, CHUNK_SIZE


class AudioEngine:
    """Handles microphone audio capture and streaming."""
    
    def __init__(self, sample_rate: int = SAMPLE_RATE, channels: int = CHANNELS,
                 chunk_size: int = CHUNK_SIZE):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.audio_queue: queue.Queue = queue.Queue()
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.audio_callback: Optional[Callable[[bytes], None]] = None
        
    def get_default_input_device(self) -> Optional[dict]:
        """Get the default input device info."""
        default_device = self.p.get_default_input_device_info()
        return default_device
    
    def list_input_devices(self) -> list:
        """List all available input devices."""
        devices = []
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': info['defaultSampleRate']
                })
        return devices
    
    def start_recording(self, audio_callback: Callable[[bytes], None]) -> bool:
        """Start recording audio from the microphone."""
        if self.is_recording:
            return False
            
        try:
            self.audio_callback = audio_callback
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            self.is_recording = True
            self.stream.start_stream()
            return True
        except Exception as e:
            print(f"Error starting recording: {e}")
            return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status) -> tuple:
        """PyAudio callback for capturing audio data."""
        if self.audio_callback and self.is_recording:
            self.audio_callback(in_data)
        return (None, pyaudio.paContinue)
    
    def stop_recording(self) -> None:
        """Stop recording audio."""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def get_audio_chunk(self) -> Optional[bytes]:
        """Get a chunk of audio data from the queue."""
        try:
            return self.audio_queue.get(timeout=0.1)
        except queue.Empty:
            return None
    
    def get_volume_level(self) -> float:
        """Get the current audio volume level (0.0 to 1.0)."""
        if not self.audio_queue.empty():
            data = self.audio_queue.get()
            audio_data = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))
            normalized = rms / 32768.0
            return min(normalized * 10, 1.0)
        return 0.0
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        self.stop_recording()
        self.p.terminate()
    
    def __del__(self):
        self.cleanup()
