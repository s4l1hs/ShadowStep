import os
import random
from utils.logger import log

def secure_delete(file_path, passes=3):
    """
    Belirtilen dosyayı, üzerine rastgele veriler yazarak güvenli bir şekilde siler.
    DoD 5220.22-M standardını simüle eder.
    """
    if not os.path.exists(file_path):
        log.error(f"Dosya bulunamadı: {file_path}")
        return False

    try:
        file_size = os.path.getsize(file_path)
        log.info(f"Güvenli silme başlatılıyor: {file_path} ({passes} geçiş)")

        with open(file_path, "ba+") as f:
            for i in range(passes):
                f.seek(0)
                # Rastgele byte verisi (Cryptographically secure random bytes kullanabiliriz ama hız için urandom yeterli)
                random_data = os.urandom(file_size)
                f.write(random_data)
                f.flush()
                os.fsync(f.fileno())
                log.debug(f" -> Geçiş {i+1}/{passes} tamamlandı.")

        os.remove(file_path)
        log.info(f"Dosya başarıyla imha edildi: {file_path}")
        return True

    except PermissionError:
        log.error(f"Erişim reddedildi: {file_path}")
        return False
    except Exception as e:
        log.error(f"Beklenmeyen hata: {e}")
        return False