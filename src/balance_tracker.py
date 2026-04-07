"""
Balance Tracker - Extra Feature
Fetches and displays Deepgram and Groq (Grok) balance information.
"""
import requests
import threading
from datetime import datetime
from config import DEEPGRAM_API_KEY, GROQ_API_KEY


class BalanceTracker:
    """Tracks API balances for Deepgram and Groq services."""
    
    def __init__(self):
        self.deepgram_balance = None
        self.groq_balance = None
        self.deepgram_last_updated = None
        self.groq_last_updated = None
        self._update_thread = None
        self._running = False
    
    def fetch_deepgram_balance(self) -> float:
        """Fetch Deepgram account balance via API."""
        try:
            # Deepgram billing API endpoint
            url = "https://api.deepgram.com/v1/billing/balance"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Accept": "application/json"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Deepgram returns balance in cents, convert to dollars
                balance = data.get("balance", 0) / 100.0
                self.deepgram_balance = balance
                self.deepgram_last_updated = datetime.now()
                return balance
            else:
                print(f"Deepgram balance API error: {response.status_code}")
                return -1
        except Exception as e:
            print(f"Error fetching Deepgram balance: {e}")
            return -1
    
    def fetch_groq_balance(self) -> float:
        """Fetch Groq API usage/balance information."""
        try:
            # Groq API usage endpoint
            url = "https://api.groq.com/openai/v1/usage"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Groq may return usage info differently
                # If balance/credits not directly available, show usage
                usage = data.get("usage", {})
                tokens_used = usage.get("total_tokens", 0)
                # Approximate: $0.000001 per token (Llama 3 8B)
                estimated_cost = tokens_used * 0.000001
                self.groq_balance = -estimated_cost  # Negative = spent
                self.groq_last_updated = datetime.now()
                return -estimated_cost
            else:
                print(f"Groq balance API error: {response.status_code}")
                return -1
        except Exception as e:
            print(f"Error fetching Groq balance: {e}")
            return -1
    
    def fetch_all_balances(self) -> dict:
        """Fetch both Deepgram and Groq balances."""
        self.fetch_deepgram_balance()
        self.fetch_groq_balance()
        return self.get_balances()
    
    def get_balances(self) -> dict:
        """Get current balance information."""
        return {
            "deepgram": {
                "balance": self.deepgram_balance,
                "last_updated": self.deepgram_last_updated.isoformat() if self.deepgram_last_updated else None
            },
            "groq": {
                "balance": self.groq_balance,
                "last_updated": self.groq_last_updated.isoformat() if self.groq_last_updated else None
            }
        }
    
    def start_auto_refresh(self, interval: int = 300) -> None:
        """Start background thread to refresh balances periodically."""
        self._running = True
        self._update_thread = threading.Thread(
            target=self._refresh_loop,
            args=(interval,),
            daemon=True
        )
        self._update_thread.start()
    
    def _refresh_loop(self, interval: int) -> None:
        """Background loop to refresh balances."""
        while self._running:
            self.fetch_all_balances()
            import time
            time.sleep(interval)
    
    def stop_auto_refresh(self) -> None:
        """Stop the auto-refresh thread."""
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=1)
    
    def format_balance(self, service: str) -> str:
        """Format balance as human-readable string."""
        balances = self.get_balances()
        bal = balances.get(service, {}).get("balance")
        
        if bal is None:
            return "N/A"
        elif bal < 0:
            return f"-${abs(bal):.2f}"
        else:
            return f"${bal:.2f}"
