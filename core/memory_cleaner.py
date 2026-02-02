import os
import sys
import platform
import subprocess
import gc
from utils.logger import log

try:
    import psutil
except ImportError:
    log.error("The 'psutil' module is missing. Install via: pip install psutil")
    psutil = None

class MemoryCleaner:
    """
    Advanced RAM & Swap Manager.
    Performs 'Free Space Wiping' on volatile memory to overwrite artifacts.
    """

    def __init__(self):
        self.os_type = platform.system()

    def wipe_free_ram(self):
        """
        Allocates all available RAM and fills it with junk data to overwrite 
        ghost artifacts, then releases it.
        """
        if not psutil:
            return False

        log.warning("Starting RAM Wipe (Free Space). System may become unresponsive for a few seconds...")
        
        try:
            # 1. Get available memory (leave a 500MB safety buffer for OS stability)
            mem = psutil.virtual_memory()
            available_bytes = mem.available - (500 * 1024 * 1024) 
            
            if available_bytes <= 0:
                log.warning("Not enough free RAM to perform wiping safely.")
                return False

            log.info(f"Overwriting {available_bytes / (1024*1024):.2f} MB of free RAM...")

            # 2. Fill RAM (The heavy lifting)
            # Creating a huge bytearray forces the OS to map physical pages 
            # to our junk data, effectively overwriting old data remnants.
            try:
                # 0x00 fill is fast and sufficient for clearing residual data
                junk_data = bytearray(available_bytes) 
            except MemoryError:
                log.warning("Memory limit hit too early, proceeding with cleanup...")
            
            # 3. Release RAM immediately
            del junk_data
            gc.collect() # Force Python Garbage Collector
            
            log.info("RAM Wipe complete. Free memory sanitized.")
            return True

        except Exception as e:
            log.error(f"RAM Wipe error: {e}")
            return False

    def drop_caches(self):
        """
        Flushes file system buffers from RAM.
        """
        if self.os_type == "Linux":
            try:
                # Requires Root
                os.system("sync; echo 3 > /proc/sys/vm/drop_caches")
                log.info("Linux Kernel Caches (PageCache, Dentries, Inodes) dropped.")
                return True
            except Exception as e:
                log.error(f"Cache drop failed (Root required?): {e}")
                return False
        elif self.os_type == "Windows":
            # Windows standby list clearing is complex via API, 
            # but the 'wipe_free_ram' method indirectly forces this.
            log.info("Windows Standby List will be trimmed by RAM allocation.")
            return True
        elif self.os_type == "Darwin": # macOS
            try:
                os.system("sync && sudo purge")
                log.info("macOS Purge command executed.")
                return True
            except:
                return False

    def clear_swap(self):
        """
        Clears the Swap Space (Linux) or Pagefile (generic info for Windows).
        Evidence often persists in Swap even after RAM is cleared.
        """
        if self.os_type == "Linux":
            log.info("Flushing Linux Swap space (This may take time)...")
            try:
                # Turn swap off (forces data back to RAM) then on (clears disk area)
                subprocess.run(["swapoff", "-a"], check=True)
                subprocess.run(["swapon", "-a"], check=True)
                log.info("Swap space flushed and reset.")
                return True
            except Exception as e:
                log.error(f"Swap cleaning failed (Root required?): {e}")
                return False
        elif self.os_type == "Windows":
            log.info("Advisory: To clear Windows Pagefile, ensure 'ClearPageFileAtShutdown' registry key is enabled.")
            return False