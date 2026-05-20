import keyboard
import logging
from typing import Callable, Dict


class HotkeyManager:
    """
    Manages global hotkeys for the trainer.
    Allows binding functions to key combinations.
    """

    def __init__(self):
        self._bindings: Dict[str, Callable] = {}
        self._listening = False

    def bind(self, hotkey: str, callback: Callable) -> None:
        """
        Bind a hotkey string (e.g., 'ctrl+shift+h') to a callback function.
        The callback will be called when the hotkey is pressed.
        """
        self._bindings[hotkey] = callback
        logging.info(f"Bound hotkey '{hotkey}' to {callback.__name__}.")

    def start(self) -> None:
        """Start listening for hotkeys in a background thread."""
        if self._listening:
            return
        self._listening = True
        for hotkey, callback in self._bindings.items():
            keyboard.add_hotkey(hotkey, callback)
        logging.info("Hotkey listener started.")

    def stop(self) -> None:
        """Stop listening for hotkeys and remove all hooks."""
        if not self._listening:
            return
        keyboard.unhook_all()
        self._listening = False
        logging.info("Hotkey listener stopped.")

    def remove_binding(self, hotkey: str) -> None:
        """Remove a specific hotkey binding."""
        if hotkey in self._bindings:
            del self._bindings[hotkey]
            keyboard.remove_hotkey(hotkey)
            logging.info(f"Removed binding for '{hotkey}'.")
