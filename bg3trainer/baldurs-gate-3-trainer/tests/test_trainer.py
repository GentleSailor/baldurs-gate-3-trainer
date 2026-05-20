import unittest
from unittest.mock import patch, MagicMock
from src.trainer import BaldursGate3Trainer


class TestBaldursGate3Trainer(unittest.TestCase):
    """Unit tests for the BaldursGate3Trainer class."""

    def setUp(self):
        """Create a trainer instance with a mocked memory reader."""
        self.trainer = BaldursGate3Trainer()
        # Replace the real MemoryReader with a mock
        patcher = patch('src.trainer.MemoryReader')
        self.mock_reader_cls = patcher.start()
        self.mock_reader = MagicMock()
        self.mock_reader_cls.return_value = self.mock_reader
        self.mock_reader.base_address = 0x400000
        self.mock_reader._open_process.return_value = True
        self.addCleanup(patcher.stop)

    def test_connect_success(self):
        """Test that connect returns True when process is found."""
        result = self.trainer.connect()
        self.assertTrue(result)
        self.mock_reader._open_process.assert_called_once()

    def test_set_health(self):
        """Test setting health writes to correct offset."""
        self.trainer.connect()
        self.trainer.set_health(100)
        expected_addr = self.mock_reader.base_address + 0x00A1B2C0
        self.mock_reader.write_int.assert_called_with(expected_addr, 100)

    def test_set_gold(self):
        """Test setting gold writes to correct offset."""
        self.trainer.connect()
        self.trainer.set_gold(50000)
        expected_addr = self.mock_reader.base_address + 0x00C3D4E0
        self.mock_reader.write_int.assert_called_with(expected_addr, 50000)

    def test_toggle_god_mode(self):
        """Test toggling god mode changes state."""
        self.assertFalse(self.trainer.active_cheats['god_mode'])
        self.trainer.toggle_god_mode()
        self.assertTrue(self.trainer.active_cheats['god_mode'])
        self.trainer.toggle_god_mode()
        self.assertFalse(self.trainer.active_cheats['god_mode'])

    def test_start_loop_applies_cheats(self):
        """Test that start_loop applies active cheats repeatedly."""
        self.trainer.connect()
        self.trainer.active_cheats['god_mode'] = True
        self.trainer.active_cheats['infinite_gold'] = True
        # Run loop for a short time, then stop
        import threading
        stop_timer = threading.Timer(0.3, self.trainer.stop)
        stop_timer.start()
        self.trainer.start_loop()
        # Verify that write_int was called multiple times for health and gold
        self.assertGreater(self.mock_reader.write_int.call_count, 2)

    def test_stop_cleans_up(self):
        """Test that stop closes the reader."""
        self.trainer.connect()
        self.trainer.stop()
        self.mock_reader.close.assert_called_once()
        self.assertFalse(self.trainer._running)


if __name__ == '__main__':
    unittest.main()
