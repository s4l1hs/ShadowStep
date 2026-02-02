import os
import platform
import subprocess
import shutil
from utils.logger import log

class Janitor:
    """
    Sistemdeki geçici izleri (Loglar, Geçmiş, Pano, Önbellek) temizler.
    Dijital Ninja'nın 'duman bombası' modülüdür.
    """

    def __init__(self):
        self.os_type = platform.system()
        self.home_dir = os.path.expanduser("~")

    def clean_clipboard(self):
        """Sistem panosundaki (Clipboard) veriyi siler."""
        try:
            if self.os_type == "Windows":
                # Windows: clip komutu ile boşluk gönder
                os.system("echo off | clip")
            elif self.os_type == "Linux":
                # Linux: xsel veya xclip varsa kullan
                if shutil.which("xsel"):
                    os.system("xsel -bc")
                elif shutil.which("xclip"):
                    os.system("xclip -selection clipboard /dev/null")
            elif self.os_type == "Darwin": # macOS
                os.system("pbcopy < /dev/null")
            
            log.info("Pano (Clipboard) başarıyla temizlendi.")
            return True
        except Exception as e:
            log.error(f"Pano temizleme hatası: {e}")
            return False

    def clean_shell_history(self):
        """Bash ve Zsh geçmiş dosyalarını bulur ve içeriğini temizler."""
        history_files = [
            os.path.join(self.home_dir, ".bash_history"),
            os.path.join(self.home_dir, ".zsh_history"),
            os.path.join(self.home_dir, ".history") # Bazı sistemler
        ]

        cleaned_count = 0
        for h_file in history_files:
            if os.path.exists(h_file):
                try:
                    # Dosyayı silmek yerine içini boşaltıyoruz (daha az şüphe çeker)
                    open(h_file, 'w').close()
                    log.info(f"Shell geçmişi temizlendi: {h_file}")
                    cleaned_count += 1
                except PermissionError:
                    log.error(f"Erişim reddedildi: {h_file}")
        
        if cleaned_count == 0:
            log.warning("Temizlenecek shell geçmişi bulunamadı.")
            
        # Mevcut oturumun geçmişini de temizlemeye çalış (Linux/Mac)
        if self.os_type != "Windows":
            try:
                # 'history -c' komutu subprocess ile çalışmaz çünkü shell built-in'dir.
                # Ancak kullanıcıya uyarı verebiliriz.
                log.info("Not: Mevcut terminal oturumunu kapatman önerilir.")
            except:
                pass

    def flush_dns(self):
        """DNS Önbelleğini temizler."""
        try:
            if self.os_type == "Windows":
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.os_type == "Darwin": # macOS
                subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.os_type == "Linux":
                # Systemd-resolve genelde kullanılır
                subprocess.run(["resolvectl", "flush-caches"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            log.info("DNS önbelleği (Cache) temizlendi.")
        except Exception as e:
            log.warning(f"DNS temizleme sırasında hata (Yetki gerekebilir): {e}")

    def wipe_logs(self):
        """
        [Advanced] Sistem loglarını temizler.
        Windows: Event Logs
        Linux: /var/log (Root gerekir)
        """
        if self.os_type == "Windows":
            log.info("Windows Event Logları temizleniyor (Yönetici izni gerekir)...")
            try:
                # Tüm log kategorilerini listele ve temizle
                # wevtutil el: List logs, wevtutil cl: Clear log
                logs = subprocess.check_output(["wevtutil", "el"], text=True).splitlines()
                for log_name in logs:
                    subprocess.run(["wevtutil", "cl", log_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log.info("Windows Event Log temizliği tamamlandı.")
            except Exception as e:
                log.error(f"Log temizleme hatası: {e}")

        elif self.os_type == "Linux":
            log.warning("Linux log temizliği (/var/log) sadece ROOT yetkisiyle yapılabilir.")
            # Güvenlik için şimdilik otomatik kod eklemiyoruz, yanlışlıkla sistemi bozabilir.
            # Ancak /var/log/auth.log veya syslog hedeflenebilir.