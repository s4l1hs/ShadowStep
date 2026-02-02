import os
import platform
import time
from utils.logger import log

# İşletim sistemine göre kütüphaneleri yükle
if platform.system() == "Windows":
    import ctypes
    from ctypes import wintypes

class TimeStomper:
    """
    Dosya zaman damgalarını (Creation, Access, Modification) manipüle eder.
    Windows için Win32 API, Linux için os.utime kullanır.
    """

    def __init__(self):
        self.os_type = platform.system()

    def get_file_times(self, path):
        """Bir referans dosyanın zaman damgalarını çeker."""
        if not os.path.exists(path):
            log.error(f"Referans dosya bulunamadı: {path}")
            return None
        
        stat = os.stat(path)
        # Windows'ta creation time (st_ctime), Linux'ta metadata change time
        creation_time = stat.st_ctime 
        access_time = stat.st_atime
        modify_time = stat.st_mtime
        
        return (creation_time, access_time, modify_time)

    def stomp(self, target_path, ref_path=None, custom_date=None):
        """
        target_path dosyasının tarihlerini değiştirir.
        Ya ref_path'ten kopyalar ya da custom_date kullanır.
        """
        if not os.path.exists(target_path):
            log.error(f"Hedef dosya yok: {target_path}")
            return False

        times = None
        if ref_path:
            log.info(f"Referans alınıyor: {ref_path}")
            times = self.get_file_times(ref_path)
        
        if not times:
            # Şimdilik varsayılan olarak şu anki zamanı veya custom_date mantığını buraya ekleyebilirsin
            log.warning("Zaman verisi sağlanmadı, işlem iptal.")
            return False

        c_time, a_time, m_time = times
        log.info(f"Hedef damgalanıyor: {target_path}")

        if self.os_type == "Windows":
            return self._set_windows_times(target_path, c_time, a_time, m_time)
        else:
            return self._set_linux_times(target_path, a_time, m_time)

    def _set_linux_times(self, path, atime, mtime):
        """Linux: Sadece Access ve Modify değişir (Creation zordur)."""
        try:
            os.utime(path, (atime, mtime))
            log.info("Linux zaman damgaları güncellendi (Access/Modify).")
            return True
        except Exception as e:
            log.error(f"Linux timestomp hatası: {e}")
            return False

    def _set_windows_times(self, path, c_time, a_time, m_time):
        """Windows: Win32 API kullanarak Creation Time dahil hepsini değiştirir."""
        try:
            # Dosya tanıtıcısını (handle) al
            fh = ctypes.windll.kernel32.CreateFileW(
                path, 256, 0, None, 3, 128, None
            )
            if fh == -1:
                log.error("Windows dosya tanıtıcısı alınamadı.")
                return False

            # Unix timestamp -> Windows FileTime dönüştürme (100 nanosaniye aralıkları)
            # 116444736000000000: 1601-1970 arası fark
            def to_filetime(ts):
                return int((ts * 10000000) + 116444736000000000)

            ctime_ft = wintypes.FILETIME(to_filetime(c_time) & 0xFFFFFFFF, to_filetime(c_time) >> 32)
            atime_ft = wintypes.FILETIME(to_filetime(a_time) & 0xFFFFFFFF, to_filetime(a_time) >> 32)
            mtime_ft = wintypes.FILETIME(to_filetime(m_time) & 0xFFFFFFFF, to_filetime(m_time) >> 32)

            # SetFileTime API çağrısı
            success = ctypes.windll.kernel32.SetFileTime(
                fh, ctypes.byref(ctime_ft), ctypes.byref(atime_ft), ctypes.byref(mtime_ft)
            )
            
            ctypes.windll.kernel32.CloseHandle(fh)
            
            if success:
                log.info("Windows MFT zaman damgaları (Creation/Access/Write) güncellendi.")
                return True
            else:
                log.error("SetFileTime API başarısız oldu.")
                return False

        except Exception as e:
            log.error(f"Win32 API hatası: {e}")
            return False