"""CLI configuration management."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "sniptw"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "token"

DEFAULT_API_URL = "sniptw-production.up.railway.app"


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_api_url() -> str:
    """Get the API URL from config or return default."""
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            return config.get("api_url", DEFAULT_API_URL)
        except json.JSONDecodeError, OSError:
            pass
    return DEFAULT_API_URL


def set_api_url(url: str) -> None:
    """Set the API URL in config."""
    ensure_config_dir()
    config = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except json.JSONDecodeError, OSError:
            pass
    config["api_url"] = url.rstrip("/")
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_token() -> str | None:
    """Get the stored access token."""
    if TOKEN_FILE.exists():
        try:
            return TOKEN_FILE.read_text().strip()
        except OSError:
            pass
    return None


def save_token(token: str) -> None:
    """Save the access token."""
    ensure_config_dir()
    TOKEN_FILE.write_text(token)
    TOKEN_FILE.chmod(0o600)


def clear_token() -> None:
    """Clear the stored access token."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return get_token() is not None
