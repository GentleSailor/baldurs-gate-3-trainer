import time
import logging
from typing import Dict, Optional
from .memory_reader import MemoryReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BaldursGate3Trainer:
    """
    Main trainer class that manages cheats for Baldur's Gate 3.
    Provides methods to modify in-game values like health, gold, and stats.
    """

    # Example memory offsets (these are placeholders; real offsets would be found via reverse engineering)
    OFFSETS = {
        'health': 0x00A1B2C0,
        'max_health': 0x00A1B2C4,
        'gold': 0x00C3D4E0,
        'strength': 0x00F1A2B0,
    }

    def __init__(self):
        self.reader = MemoryReader()
        self.active_cheats: Dict[str, bool] = {
            'god_mode': False,
            'infinite_gold': False,
            'max_stats': False,
        }
        self._running = False

    def connect(self) -> bool:
        """Attempt to connect to the Baldur's Gate 3 process."""
        if self.reader._open_process():
            logging.info("Connected to Baldur's Gate 3 successfully.")
            return True
        else:
            logging.error("Failed to connect to Baldur's Gate 3. Is the game running?")
            return False

    def set_health(self, value: int) -> bool:
        """Set the player's current health to a given value."""
        if self.reader.base_address:
            addr = self.reader.base_address + self.OFFSETS['health']
            return self.reader.write_int(addr, value)
        return False

    def set_gold(self, value: int) -> bool:
        """Set the player's gold to a given value."""
        if self.reader.base_address:
            addr = self.reader.base_address + self.OFFSETS['gold']
            return self.reader.write_int(addr, value)
        return False

    def set_strength(self, value: int) -> bool:
        """Set the player's strength stat (1-30 typical)."""
        if self.reader.base_address:
            addr = self.reader.base_address + self.OFFSETS['strength']
            return self.reader.write_int(addr, value)
        return False

    def toggle_god_mode(self) -> None:
        """Toggle god mode: sets health to max on each tick."""
        self.active_cheats['god_mode'] = not self.active_cheats['god_mode']
        status = "enabled" if self.active_cheats['god_mode'] else "disabled"
        logging.info(f"God mode {status}.")

    def toggle_infinite_gold(self) -> None:
        """Toggle infinite gold: sets gold to 99999 on each tick."""
        self.active_cheats['infinite_gold'] = not self.active_cheats['infinite_gold']
        status = "enabled" if self.active_cheats['infinite_gold'] else "disabled"
        logging.info(f"Infinite gold {status}.")

    def toggle_max_stats(self) -> None:
        """Toggle max stats: sets strength, dexterity, etc. to 30."""
        self.active_cheats['max_stats'] = not self.active_cheats['max_stats']
        status = "enabled" if self.active_cheats['max_stats'] else "disabled"
        logging.info(f"Max stats {status}.")

    def start_loop(self) -> None:
        """
        Start the main cheat loop that applies active cheats every 100ms.
        This runs until stop() is called.
        """
        self._running = True
        logging.info("Trainer loop started.")
        while self._running:
            if self.active_cheats['god_mode']:
                self.set_health(9999)
            if self.active_cheats['infinite_gold']:
                self.set_gold(99999)
            if self.active_cheats['max_stats']:
                self.set_strength(30)
            time.sleep(0.1)

    def stop(self) -> None:
        """Stop the cheat loop and clean up."""
        self._running = False
        self.reader.close()
        logging.info("Trainer stopped.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
