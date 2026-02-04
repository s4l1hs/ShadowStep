# ShadowStep

**ShadowStep** is a professional-grade, modular toolkit for artifact management, metadata manipulation, and system sanitization. It is designed as a developer-focused framework for automating and testing cover-track workflows in authorized, legal, and controlled environments.

**Design goals**
- Modular components with clear responsibilities
- Cross-platform awareness (Windows, Linux, macOS) with safe fallbacks
- Auditability and testability for research and red-team exercises

---

## 📌 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Modules & Files](#modules--files)
- [Installation](#installation)
- [Configuration](#configuration)
- [CLI Usage & Examples](#cli-usage--examples)
- [Development & Testing](#development--testing)
- [Packaging](#packaging)
- [Security, Ethics & Legal Notice](#security-ethics--legal-notice)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 🔍 Project Overview
ShadowStep provides a set of cooperative utilities for managing system artifacts and metadata. The tool is intended for use by security professionals, researchers, and system administrators who need to understand and test artifact lifecycles. The project is not intended to facilitate malicious activity — see the [Security, Ethics & Legal Notice](#security-ethics--legal-notice).

## ✨ Features
- Secure file deletion with configurable overwrite passes (`utils/shredder.py`)
- Timestamp manipulation / timestomping for analysis and testing scenarios (`core/forensic_view.py`)
- System trace cleaning helpers: clipboard, shell history, DNS cache, RAM & swap handling (`core/janitor.py`, `core/memory_cleaner.py`)
- Network identity utilities (MAC generation/change; Linux-focused) (`core/network_utils.py`)
- Surgical log operations (text-based logs on Linux/macOS, structured handling for Windows Event Logs) skeleton (`core/log_surgeon.py`)
- Centralized, colorized logging support (`utils/logger.py`, `utils/colors.py`)
- Simple YAML-based configuration (`config/default.yaml`) with a loader in `config/__init__.py`

## 🧩 Modules & Files
- `shadowstep/cli.py` — main CLI entry module and argument routing. Installable via `setup.py` entry point `shadowstep=shadowstep.cli:main`.
- `shadowstep/__main__.py` — module entry point for `python -m shadowstep`.
- `core/forensic_view.py` — `TimeStomper` class: cross-platform timestamp manipulation functions.
- `core/log_surgeon.py` — `LogSurgeon` class: surgical cleaning and (safe) decoy injection strategies; designed with platform checks.
- `core/janitor.py` — `Janitor` class: higher-level cleanup orchestration (clipboard, history, DNS, logs).
- `core/memory_cleaner.py` — `MemoryCleaner` class: RAM & swap utilities (relies on `psutil` when available).
- `core/network_utils.py` — `NetworkManager` class: MAC generation and Linux-focused MAC change functionality.
- `utils/shredder.py` — `secure_delete()` function: overwrites and deletes files.
- `utils/logger.py` & `utils/colors.py` — logging and color helpers.
- `config/default.yaml` — default configuration values (app metadata, logging level, shredder defaults, network defaults).

## 🛠️ Installation
Recommended: create and use a Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
\.venv\Scripts\activate   # Windows (PowerShell)
pip install -r requirements.txt
pip install -e .
```

After installing with `pip install -e .`, the `shadowstep` console script will be available on your PATH and resolves to `shadowstep:main`.

## ⚙️ Configuration
Default configuration is located in `config/default.yaml`. The project loads this YAML at import time via `config/__init__.py`. Example config fields include:

- `app.version` and `app.environment`
- `logging.level` and `logging.file_path`
- `shredder.default_passes` and `shredder.method`
- `network.spoof_oui`

Override configuration by editing `config/default.yaml` or by providing a different loader in your own environment when embedding the library.

## 🧪 CLI Usage & Examples
ShadowStep exposes a single-script CLI. Run `shadowstep -h` or `shadowstep --help` after install, or invoke directly via the module:

```bash
python -m shadowstep --help
```

### All CLI options (long + short)
**Primary actions**
- Help: `-h`, `--help`
- Secure delete: `-s`, `--shred` (requires FILE)
- Timestomp: `-t`, `-ts`, `--timestomp` (requires TARGET)
- MAC spoof: `-m`, `--spoof`
- System clean: `-c`, `--clean`
- Log sanitize: `-z`, `--sanitize` (requires LOGFILE; on Windows path is ignored)

**Helper options**
- Reference file: `-r`, `--ref` (for timestomp)
- Shred passes: `-p`, `--passes`
- Network interface: `-i`, `--interface`
- Manual MAC: `-M`, `--mac`
- Keywords list: `-k`, `--keywords`

### Common examples
**Secure delete a file (default 3 passes)**

```bash
shadowstep -s /path/to/secret.txt
```

**Change file timestamps using a reference file**

```bash
shadowstep -t /path/to/target.file -r /path/to/reference.file
```

**Run janitor to clear shell history, clipboard, DNS, RAM & swap (platform-dependent)**

```bash
shadowstep -c
```

**Surgical log sanitize (text log on Linux/macOS or Event Logs on Windows)**

```bash
shadowstep -z /var/log/syslog -k password admin  # Linux/macOS
shadowstep -z --keywords "sensitive-hostname" "username"           # Windows (Event Log handling)
```

### Notes & caveats
- Many operations require elevated privileges (root/Administrator). The tool will log warnings or fail gracefully if permissions are insufficient.
- Platform behavior intentionally differs where OS constraints exist (e.g., creation time on Linux cannot be set via `utime`).

## 🧩 Development & Testing
Run unit tests (project includes `tests/`):

```bash
python -m unittest discover tests
```

Linting and formatting recommendations:

```bash
pip install -r requirements-dev.txt  # if you maintain a dev requirements file
black .
flake8 .
```

Project packaging and entry points are defined in `setup.py`. Use `pip install -e .` to install in editable mode during development.

## 📦 Packaging
The `setup.py` declares `shadowstep` as a package and exposes a console script entry point. To build a wheel:

```bash
python -m pip wheel .
```

For a standalone binary, tools such as PyInstaller can be used, but be mindful of platform-specific dependencies and administrative requirements.

## 🛡️ Security, Ethics & Legal Notice
ShadowStep contains functions that may be misused. You must not use the project to commit unauthorized or illegal activity. Use this software only in environments where you have explicit written authorization (e.g., your own lab, sanctioned red-team exercise, or customer engagement with a signed rules-of-engagement).

By using or contributing to this project you agree to follow applicable laws and obtain appropriate authorizations. The authors and maintainers are not responsible for misuse.

## 🗺️ Roadmap
Planned and suggested improvements:
- Harden and formalize `log_surgeon` with non-destructive simulation modes and improved Windows Event Log handling.
- Add platform-specific safe-check flags and a dry-run mode that reports intended changes without applying them.
- Expand tests and add integration tests for privileged operations (mocked where appropriate).
- Implement pluggable backends for log formats and better decoy generation templates.
- Add a `--sanitize-policy` feature to define reusable cleanup profiles.

## 🤝 Contributing
Contributions are welcome. Recommended workflow:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Add tests for new behavior.
4. Run the test suite and linters.
5. Submit a pull request with a clear description and rationale.

Please keep changes focused and well-tested. Document breaking changes in PR descriptions.

## 📄 License
This project is provided under the MIT License. See `LICENSE` for details.

## 🙌 Acknowledgements
ShadowStep was authored and maintained by contributors. The project bundles several third-party helper libraries — see `requirements.txt` and `setup.py` for runtime dependencies.

---

If you want, I can:
- Expand any module-specific documentation in this README (API signatures, examples)
- Add a `docs/` folder and Sphinx/Markdown pages
- Add a `SECURITY.md` and `CONTRIBUTING.md`

Let me know which items to continue with next.