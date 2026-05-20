import ctypes
import ctypes.wintypes
from typing import Optional


class MemoryReader:
    """
    Reads process memory for Baldur's Gate 3.
    Uses Win32 API via ctypes to read from the game process.
    """

    def __init__(self, process_name: str = "bg3.exe"):
        self.process_name = process_name
        self.process_handle: Optional[int] = None
        self.base_address: Optional[int] = None

    def _open_process(self) -> bool:
        """
        Open a handle to the BG3 process with necessary permissions.
        Returns True if successful, False otherwise.
        """
        kernel32 = ctypes.windll.kernel32
        PROCESS_ALL_ACCESS = 0x1F0FFF

        # Enumerate processes (simplified: find by name)
        # In a real project, use CreateToolhelp32Snapshot
        # For brevity, we assume process ID is known or found via psutil
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == self.process_name:
                pid = proc.info['pid']
                self.process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
                if self.process_handle:
                    self._get_base_address(pid)
                    return True
        return False

    def _get_base_address(self, pid: int) -> None:
        """
        Retrieve the base address of the main module.
        Uses psutil for simplicity.
        """
        import psutil
        proc = psutil.Process(pid)
        # Typically the first memory mapping with 'writable' and 'image' is the main executable
        for mmap in proc.memory_maps(grouped=False):
            if mmap.path and mmap.path.endswith('.exe'):
                # Extract base address from the first region
                # In a real tool, parse /proc/[pid]/maps or use EnumProcessModules
                self.base_address = int(mmap.addr.split('-')[0], 16)
                return

    def read_int(self, address: int) -> Optional[int]:
        """
        Read a 4-byte integer from the given virtual address.
        Returns the integer value or None on failure.
        """
        if not self.process_handle:
            return None
        kernel32 = ctypes.windll.kernel32
        buffer = ctypes.c_int(0)
        bytes_read = ctypes.c_size_t(0)
        success = kernel32.ReadProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            ctypes.byref(buffer),
            ctypes.sizeof(buffer),
            ctypes.byref(bytes_read)
        )
        if success and bytes_read.value == ctypes.sizeof(buffer):
            return buffer.value
        return None

    def write_int(self, address: int, value: int) -> bool:
        """
        Write a 4-byte integer to the given virtual address.
        Returns True if successful.
        """
        if not self.process_handle:
            return False
        kernel32 = ctypes.windll.kernel32
        buffer = ctypes.c_int(value)
        bytes_written = ctypes.c_size_t(0)
        success = kernel32.WriteProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            ctypes.byref(buffer),
            ctypes.sizeof(buffer),
            ctypes.byref(bytes_written)
        )
        return bool(success and bytes_written.value == ctypes.sizeof(buffer))

    def close(self) -> None:
        """Close the process handle."""
        if self.process_handle:
            kernel32 = ctypes.windll.kernel32
            kernel32.CloseHandle(self.process_handle)
            self.process_handle = None
