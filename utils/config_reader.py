"""
Central configuration access for the framework.

Precedence (highest wins):
  1. Environment variable (UPPERCASE key) — this is what CI/CD (GitHub Actions
     secrets/variables, nightly scheduled workflow) uses to override behaviour
     without any code or file changes.
  2. .env file (local development convenience, loaded via python-dotenv).
  3. config/config.yaml (checked-in defaults).
"""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_FILE = _PROJECT_ROOT / "config" / "config.yaml"

load_dotenv(_PROJECT_ROOT / ".env")


class ConfigReader:
    """Thin wrapper that merges config.yaml defaults with environment overrides."""

    _yaml_config: dict = None

    @classmethod
    def _load_yaml(cls) -> dict:
        if cls._yaml_config is None:
            with open(_CONFIG_FILE, "r", encoding="utf-8") as fh:
                cls._yaml_config = yaml.safe_load(fh) or {}
        return cls._yaml_config

    @classmethod
    def get(cls, key: str, default=None):
        """Return a raw value for key, env var takes precedence over yaml."""
        env_value = os.getenv(key.upper())
        if env_value is not None:
            return env_value
        return cls._load_yaml().get(key.lower(), default)

    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        value = cls.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")

    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        return int(cls.get(key, default))

    @classmethod
    def base_url(cls) -> str:
        return cls.get("base_url")

    @classmethod
    def browser(cls) -> str:
        return cls.get("browser", "chrome").lower()

    @classmethod
    def headless(cls) -> bool:
        return cls.get_bool("headless", False)

    @classmethod
    def explicit_wait(cls) -> int:
        return cls.get_int("explicit_wait", 15)

    @classmethod
    def page_load_timeout(cls) -> int:
        return cls.get_int("page_load_timeout", 30)

    @classmethod
    def screenshot_on_failure(cls) -> bool:
        return cls.get_bool("screenshot_on_failure", True)

    @classmethod
    def login_email(cls) -> str:
        return cls.get("login_email")


    @classmethod
    def login_password(cls) -> str:
        return cls.get("login_password")
