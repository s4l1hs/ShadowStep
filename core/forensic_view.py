import os
import platform
import time
from utils.logger import log

# Load platform-specific libraries
if platform.system() == "Windows":
    import ctypes
    from ctypes import wintypes

class TimeStomper:
    """
    Manipulates file timestamps (Creation, Access, Modification).
    Uses Win32 API on Windows and os.utime on Linux.
    """

    def __init__(self):
        self.os_type = platform.system()

    def get_file_times(self, path):
        """Fetch timestamps from a reference file."""
        if not os.path.exists(path):
            log.error(f"Reference file not found: {path}")
            return None
        
        stat = os.stat(path)
        # On Windows, st_ctime is creation time; on Linux, it's metadata change time
        creation_time = stat.st_ctime 
        access_time = stat.st_atime
        modify_time = stat.st_mtime
        
        return (creation_time, access_time, modify_time)

    def stomp(self, target_path, ref_path=None, custom_date=None):
        """
        Changes timestamps on target_path.
        Copies from ref_path or uses custom_date.
        """
        if not os.path.exists(target_path):
            log.error(f"Target file not found: {target_path}")
            return False

        times = None
        if ref_path:
            log.info(f"Using reference file: {ref_path}")
            times = self.get_file_times(ref_path)
        
        if not times:
            # TODO: add current time or custom_date handling here if needed
            log.warning("No time data provided; operation aborted.")
            return False

        c_time, a_time, m_time = times
        log.info(f"Applying timestamps to target: {target_path}")

        if self.os_type == "Windows":
            return self._set_windows_times(target_path, c_time, a_time, m_time)
        else:
            return self._set_linux_times(target_path, a_time, m_time)

    def _set_linux_times(self, path, atime, mtime):
        """Linux: only Access and Modify change (Creation is limited)."""
        try:
            os.utime(path, (atime, mtime))
            log.info("Linux timestamps updated (Access/Modify).")
            return True
        except Exception as e:
            log.error(f"Linux timestomp error: {e}")
            return False

    def _set_windows_times(self, path, c_time, a_time, m_time):
        """Windows: uses Win32 API to update Creation, Access, and Write times."""
        try:
            # Get a file handle
            fh = ctypes.windll.kernel32.CreateFileW(
                path, 256, 0, None, 3, 128, None
            )
            if fh == -1:
                log.error("Failed to acquire Windows file handle.")
                return False

            # Unix timestamp -> Windows FileTime (100-nanosecond intervals)
            # 116444736000000000: offset between 1601 and 1970
            def to_filetime(ts):
                return int((ts * 10000000) + 116444736000000000)

            ctime_ft = wintypes.FILETIME(to_filetime(c_time) & 0xFFFFFFFF, to_filetime(c_time) >> 32)
            atime_ft = wintypes.FILETIME(to_filetime(a_time) & 0xFFFFFFFF, to_filetime(a_time) >> 32)
            mtime_ft = wintypes.FILETIME(to_filetime(m_time) & 0xFFFFFFFF, to_filetime(m_time) >> 32)

            # SetFileTime API call
            success = ctypes.windll.kernel32.SetFileTime(
                fh, ctypes.byref(ctime_ft), ctypes.byref(atime_ft), ctypes.byref(mtime_ft)
            )
            
            ctypes.windll.kernel32.CloseHandle(fh)
            
            if success:
                log.info("Windows timestamps updated (Creation/Access/Write).")
                return True
            else:
                log.error("SetFileTime API failed.")
                return False

        except Exception as e:
            log.error(f"Win32 API error: {e}")
            return False