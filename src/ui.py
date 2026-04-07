"""
PyQt6 System Tray UI for VocalFlow Windows
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QWidget,
    QVBoxLayout, QLabel, QPushButton, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon


class VocalFlowWindow(QWidget):
    """Main VocalFlow window with transcript and controls."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.balance_tracker = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("VocalFlow")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("VocalFlow")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("AI Voice-to-Text")
        subtitle.setStyleSheet("font-size: 14px; color: #888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        
        # Transcript area
        layout.addWidget(QLabel("Transcript:"))
        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setStyleSheet(
            "background-color: #1e1e1e; color: #ffffff; border: 1px solid #333;"
        )
        layout.addWidget(self.transcript)
        
        # Balance display (extra feature)
        layout.addSpacing(10)
        layout.addWidget(QLabel("API Balances:"))
        
        balance_frame = QFrame()
        balance_frame.setStyleSheet(
            "background-color: #2d2d2d; border-radius: 8px; padding: 10px;"
        )
        balance_layout = QVBoxLayout(balance_frame)
        
        self.dg_balance_label = QLabel("Deepgram: Loading...")
        self.dg_balance_label.setStyleSheet("color: #00ff00;")
        balance_layout.addWidget(self.dg_balance_label)
        
        self.groq_balance_label = QLabel("Groq: Loading...")
        self.groq_balance_label.setStyleSheet("color: #00ff00;")
        balance_layout.addWidget(self.groq_balance_label)
        
        layout.addWidget(balance_frame)
        
        # Buttons
        layout.addSpacing(10)
        
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        self.toggle_btn = QPushButton("Start Listening")
        self.toggle_btn.setStyleSheet(
            "background-color: #00ff00; color: #000; font-weight: bold; padding: 10px;"
        )
        self.toggle_btn.clicked.connect(self.toggle_listening)
        button_layout.addWidget(self.toggle_btn)
        
        self.inject_btn = QPushButton("Inject Last Transcript")
        self.inject_btn.setStyleSheet(
            "background-color: #333; color: #fff; padding: 10px;"
        )
        self.inject_btn.clicked.connect(self.inject_transcript)
        button_layout.addWidget(self.inject_btn)
        
        self.refresh_btn = QPushButton("Refresh Balances")
        self.refresh_btn.setStyleSheet(
            "background-color: #333; color: #fff; padding: 10px;"
        )
        self.refresh_btn.clicked.connect(self.refresh_balances)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        self.listening = False
    
    def toggle_listening(self):
        self.listening = not self.listening
        if self.listening:
            self.toggle_btn.setText("Stop Listening")
            self.toggle_btn.setStyleSheet(
                "background-color: #ff4444; color: #fff; font-weight: bold; padding: 10px;"
            )
            self.status_label.setText("Status: Listening...")
            if hasattr(self.app, 'vocalflow'):
                self.app.vocalflow.start_listening()
        else:
            self.toggle_btn.setText("Start Listening")
            self.toggle_btn.setStyleSheet(
                "background-color: #00ff00; color: #000; font-weight: bold; padding: 10px;"
            )
            self.status_label.setText("Status: Ready")
            if hasattr(self.app, 'vocalflow'):
                self.app.vocalflow.stop_listening()
    
    def add_transcript(self, text: str):
        self.transcript.append(text)
    
    def inject_transcript(self):
        last_text = self.transcript.toPlainText().strip()
        if last_text and hasattr(self.app, 'vocalflow'):
            self.app.vocalflow.inject_text(last_text)
            self.status_label.setText("Status: Text injected!")
    
    def update_balances(self, deepgram: str, groq: str):
        self.dg_balance_label.setText(f"Deepgram: {deepgram}")
        self.groq_balance_label.setText(f"Groq: {groq}")
    
    def refresh_balances(self):
        if hasattr(self.app, 'vocalflow') and self.app.vocalflow.balance_tracker:
            self.app.vocalflow.balance_tracker.fetch_all_balances()
            dg = self.app.vocalflow.balance_tracker.format_balance("deepgram")
            groq = self.app.vocalflow.balance_tracker.format_balance("groq")
            self.update_balances(dg, groq)
            self.status_label.setText("Status: Balances refreshed!")
