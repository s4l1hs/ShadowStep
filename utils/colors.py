"""Color utilities with a safe fallback if colorama is unavailable."""

try:
    from colorama import Fore, Style, init as _init  # type: ignore[import-not-found]

    def init(autoreset=True):
        _init(autoreset=autoreset)

except ModuleNotFoundError:  # pragma: no cover - fallback for missing optional dependency
    class _AnsiFallback:
        def __getattr__(self, _name):
            return ""

    Fore = _AnsiFallback()
    Style = _AnsiFallback()

    def init(*_args, **_kwargs):
        return None
