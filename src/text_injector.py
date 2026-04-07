"""
Text Injector for Windows
Simulates keyboard input to inject text into the active application.
"""
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

# Virtual key codes
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt

class TextInjector:
    """Injects text into the active window using Windows keyboard simulation."""
    
    def __init__(self):
        self._input_history = []
    
    def inject_text(self, text: str) -> None:
        """Simulate typing text into the active window."""
        for char in text:
            self._send_char(char)
    
    def _send_char(self, char: str) -> None:
        """Send a single character using keyboard events."""
        vk_code = self._get_vk_code(char)
        shift_needed = char.isupper() or char in "~!@#$%^&*()_+{}|:<>?"
        
        if shift_needed:
            user32.keybd_event(VK_SHIFT, 0, 0, 0)
        
        user32.keybd_event(vk_code, 0, 0, 0)
        user32.keybd_event(vk_code, 0, 2, 0)
        
        if shift_needed:
            user32.keybd_event(VK_SHIFT, 0, 2, 0)
    
    def _get_vk_code(self, char: str) -> int:
        """Get virtual key code for a character."""
        char = char.upper()
        vk_map = {
            'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44,
            'E': 0x45, 'F': 0x46, 'G': 0x47, 'H': 0x48,
            'I': 0x49, 'J': 0x4A, 'K': 0x4B, 'L': 0x4C,
            'M': 0x4D, 'N': 0x4E, 'O': 0x4F, 'P': 0x50,
            'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
            'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58,
            'Y': 0x59, 'Z': 0x5A,
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33,
            '4': 0x34, '5': 0x35, '6': 0x36, '7': 0x37,
            '8': 0x38, '9': 0x39,
            ' ': 0x20,
            '.': 0xBE, ',': 0xBC, ';': 0xBA, ':': 0xBA,
            '-': 0xBD, '_': 0xBD, '=': 0xBB, '+': 0xBB,
            '[': 0xDB, ']': 0xDD, '\\': 0xDC, '|': 0xDC,
            "'": 0xDE, '"': 0xDE, '/': 0xBF, '?': 0xBF,
            '~': 0xC0, '`': 0xC0,
        }
        return vk_map.get(char, 0)
    
    def press_enter(self) -> None:
        """Press Enter key."""
        VK_RETURN = 0x0D
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        user32.keybd_event(VK_RETURN, 0, 2, 0)
    
    def press_tab(self) -> None:
        """Press Tab key."""
        VK_TAB = 0x09
        user32.keybd_event(VK_TAB, 0, 0, 0)
        user32.keybd_event(VK_TAB, 0, 2, 0)
    
    def press_ctrl_a(self) -> None:
        """Press Ctrl+A."""
        VK_A = 0x41
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_A, 0, 0, 0)
        user32.keybd_event(VK_A, 0, 2, 0)
        user32.keybd_event(VK_CONTROL, 0, 2, 0)
    
    def press_ctrl_v(self) -> None:
        """Press Ctrl+V (paste)."""
        VK_V = 0x56
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_V, 0, 0, 0)
        user32.keybd_event(VK_V, 0, 2, 0)
        user32.keybd_event(VK_CONTROL, 0, 2, 0)
    
    def press_ctrl_c(self) -> None:
        """Press Ctrl+C (copy)."""
        VK_C = 0x43
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_C, 0, 0, 0)
        user32.keybd_event(VK_C, 0, 2, 0)
        user32.keybd_event(VK_CONTROL, 0, 2, 0)
    
    def press_backspace(self, count: int = 1) -> None:
        """Press backspace key."""
        VK_BACK = 0x08
        for _ in range(count):
            user32.keybd_event(VK_BACK, 0, 0, 0)
            user32.keybd_event(VK_BACK, 0, 2, 0)
    
    def get_active_window(self) -> str:
        """Get the title of the currently active window."""
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd) + 1
        buffer = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, buffer, length)
        return buffer.value
