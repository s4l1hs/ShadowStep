   _____ __               __               _____ __
  / ___// /_  ____ ______/ /___ _      __ / ___// /____  ____
  \__ \/ __ \/ __ `/ __  / __ \ | /| / / \__ \/ __/ _ \/ __ \\
 ___/ / / / / /_/ / /_/ / /_/ / |/ |/ / ___/ / /_/  __/ /_/ /
/____/_/ /_/\__,_/\__,_/\____/|__/|__/ /____/\__/\___/ .___/ 
                                                    /_/      

# ShadowStep

**ShadowStep** is a professional-grade, modular toolkit for **artifact management**, **metadata manipulation**, and **system sanitization**. Designed for security professionals and Red Team operators, it provides a cooperative suite of utilities to automate cover-track workflows in authorized, legal, and controlled environments.

*Minimal traces, maximum impact.* 🥷

---

## 📌 Table of Contents
- [Highlights](#highlights-)
- [Installation](#installation-)
- [Primary Modules & Usage](#primary-modules--usage-)
- [Technical Architecture](#technical-architecture-)
- [OS Support Matrix](#os-support_matrix-)
- [Configuration](#configuration-)
- [Security & Ethics Notice](#security--ethics-notice-)

---

## Highlights ⚡
- **Modular Architecture:** Clear separation of responsibilities across core modules (Janitor, Surgeon, Cleaner).
- **Cross-Platform:** Native support for Windows, Linux, and macOS with intelligent OS detection and safe fallbacks.
- **Stealth Focused:** Surgical log cleaning and RAM sanitization to minimize digital footprints without triggering alarms.
- **Identity Masking:** Network identity utilities including OUI-aware MAC spoofing using a realistic vendor list.
- **Audit Ready:** Designed specifically for security research, forensic testing, and authorized red-team operations.

## Installation 🔐

### 📦 PyPI (Python Package Index)
Recommended for most users. Use a virtual environment for a clean setup.
```bash
pip install shadowstep
```

### 🍺 Homebrew (macOS)
Install the CLI using the provided formula or tap.

```bash
brew tap s4l1hs/shadowstep
brew install shadowstep
```

### ⚡ npm (Global CLI)
A Node.js wrapper that automatically handles the Python package installation.

```bash
npm install -g shadowstep
```

## Primary Modules & Usage 🛠️
### 1) Shred (Secure File Destruction)

Implements secure overwriting standards to delete files. It ensures data recovery is practically impossible by performing multiple overwrite passes.

```bash
# Securely destroy a file with 7 custom overwrite passes
shadowstep --shred confidential.txt --passes 7
```

### 2) Log Surgeon (Surgical Sanitization)

The "Ninja" move for logs. Instead of wiping entire log files (a major red flag), it surgically removes specific lines and injects realistic decoy logs.

```bash
# Remove IP and username from Linux auth.log
shadowstep --sanitize /var/log/auth.log --keywords "192.168.1.5" "admin"

# Sanitize Windows Event Logs (System/Application)
shadowstep --sanitize --keywords "MaliciousProcess.exe" "TargetUser"
```

### 3) Janitor (System Artifact Cleanup)

A high-level orchestration module that clears volatile traces. It handles clipboard contents, shell history, and DNS caches in a single automated sequence.

```bash
# Run a full system cleanup
shadowstep --clean
```

### 4) Memory Cleaner (RAM & Swap Sanitization)

Targeting memory forensics. This module flushes file system caches and overwrites free RAM space with junk data to destroy volatile evidence remnants.

```bash
# Automatically invoked during system cleanup via --clean
shadowstep -c
```

### 5) Timestomp (Forensic View Manipulation)

Adjusts file timestamps (Access, Modify, Change) by copying metadata from a legitimate system file to blend your artifacts into the environment.

```bash
# Copy timestamps from /etc/hosts to your target file
shadowstep --timestomp target.file --ref /etc/hosts
```

## OS Support Matrix 🧬

| Feature | Windows | Linux | macOS |
|---|---|---|---|
| Secure Shredding | ✅ | ✅ | ✅ |
| MAC Spoofing | ❌ | ✅ | ❌ |
| Log Sanitization | ✅ (Event Log) | ✅ (Text) | ✅ (Text) |
| RAM Wiping | ✅ | ✅ | ✅ |
| DNS Flushing | ✅ | ✅ | ✅ |
| Metadata Stomping | ✅ | ✅ | ✅ |

## Technical Architecture 🧩
ShadowStep is built with professional modularity:

`shadowstep/cli.py`: Central entry point for argument parsing and routing.

`core/log_surgeon.py`: Engine for surgical text and binary (EVTX) log manipulation.

`core/memory_cleaner.py`: Direct interaction with system memory, swap, and caches.

`core/janitor.py`: Orchestration of system-wide artifact cleaning.

`utils/shredder.py`: Low-level I/O operations for secure data overwriting.

## Configuration ⚙️
Default configuration is located in config/default.yaml. It defines:

App Metadata: Version and environment.

Logging: Levels and file paths.

Defaults: Shredder passes and network OUI prefixes.

## Security & Ethics Notice 🛡️
ShadowStep is intended for authorized security testing and educational purposes only. You must not use this tool to commit unauthorized or illegal activity. The authors and maintainers are not responsible for misuse.

## License 📄
This project is provided under the MIT License. See LICENSE for details.

Authored and maintained by Salih Sefer.