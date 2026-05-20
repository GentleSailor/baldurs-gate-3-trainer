import sys
import logging
from src.trainer import BaldursGate3Trainer
from src.hotkeys import HotkeyManager


def main():
    """
    Entry point for the Baldur's Gate 3 Trainer.
    Sets up the trainer and hotkeys, then starts the cheat loop.
    """
    logging.basicConfig(level=logging.INFO)

    with BaldursGate3Trainer() as trainer:
        if not trainer.reader.process_handle:
            logging.error("Could not attach to Baldur's Gate 3. Exiting.")
            sys.exit(1)

        hotkey_mgr = HotkeyManager()

        # Bind hotkeys to trainer functions
        hotkey_mgr.bind('ctrl+shift+g', trainer.toggle_god_mode)
        hotkey_mgr.bind('ctrl+shift+i', trainer.toggle_infinite_gold)
        hotkey_mgr.bind('ctrl+shift+s', trainer.toggle_max_stats)
        hotkey_mgr.bind('ctrl+shift+q', trainer.stop)

        hotkey_mgr.start()

        try:
            # The loop runs until stop() is called via hotkey
            trainer.start_loop()
        except KeyboardInterrupt:
            logging.info("Interrupted by user.")
        finally:
            hotkey_mgr.stop()
            trainer.stop()


if __name__ == "__main__":
    main()
