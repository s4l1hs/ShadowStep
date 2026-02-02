import os
import platform
import subprocess
import shutil
from utils.logger import log

class Janitor:
    """
    Cleans system traces including Clipboard, Shell History, and DNS Cache.
    Acts as the 'Digital Smoke Bomb' for the operator.
    """

    def __init__(self):
        self.os_type = platform.system()
        self.home_dir = os.path.expanduser("~")

    def clean_clipboard(self):
        """Wipes the system clipboard content."""
        try:
            if self.os_type == "Windows":
                # Windows: redirect null to clip
                os.system("echo off | clip")
            elif self.os_type == "Linux":
                # Linux: try xsel or xclip
                if shutil.which("xsel"):
                    os.system("xsel -bc")
                elif shutil.which("xclip"):
                    os.system("xclip -selection clipboard /dev/null")
            elif self.os_type == "Darwin": # macOS
                os.system("pbcopy < /dev/null")
            
            log.info("Clipboard cleared successfully.")
            return True
        except Exception as e:
            log.error(f"Clipboard cleaning failed: {e}")
            return False

    def clean_shell_history(self):
        """Locates and wipes bash/zsh history files."""
        history_files = [
            os.path.join(self.home_dir, ".bash_history"),
            os.path.join(self.home_dir, ".zsh_history"),
            os.path.join(self.home_dir, ".history") # Generic
        ]

        cleaned_count = 0
        for h_file in history_files:
            if os.path.exists(h_file):
                try:
                    # Truncate file (wipe content, keep file)
                    open(h_file, 'w').close()
                    log.info(f"Shell history wiped: {h_file}")
                    cleaned_count += 1
                except PermissionError:
                    log.error(f"Access denied: {h_file}")
        
        if cleaned_count == 0:
            log.warning("No standard shell history files found.")
            
        # Advisory for current session
        if self.os_type != "Windows":
            log.info("Advisory: It is recommended to close the current terminal session to clear memory buffers.")

    def flush_dns(self):
        """Flushes the DNS Resolver Cache."""
        try:
            if self.os_type == "Windows":
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.os_type == "Darwin": # macOS
                subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.os_type == "Linux":
                # Systemd-resolve is common on modern distros
                subprocess.run(["resolvectl", "flush-caches"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            log.info("DNS Cache flushed.")
        except Exception as e:
            log.warning(f"DNS flush failed (Privileges might be required): {e}")

    def wipe_logs(self):
        """
        [Windows Only] Aggressive Log Wiping.
        Clears all Event Logs using wevtutil. This creates an Event ID 1102 (Log Clear).
        """
        if self.os_type == "Windows":
            log.warning("Starting aggressive Windows Event Log wipe (Administrator required)...")
            try:
                # List all logs
                logs = subprocess.check_output(["wevtutil", "el"], text=True).splitlines()
                for log_name in logs:
                    # Clear each log
                    subprocess.run(["wevtutil", "cl", log_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log.info("All Windows Event Logs have been cleared.")
            except Exception as e:
                log.error(f"Log wipe error: {e}")

        elif self.os_type == "Linux":
            log.warning("Aggressive log wiping on Linux (/var/log) requires manual ROOT intervention.")
            log.info("Suggestion: Use --sanitize for surgical cleaning instead.")