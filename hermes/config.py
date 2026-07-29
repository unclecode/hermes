import os
import yaml
from typing import Dict, Any, Optional

# Isolated from Nous Hermes Agent (~/.hermes and %LOCALAPPDATA%/hermes).
_DEFAULT_HOME = os.path.join("~", ".unclecode-hermes")


def _home_dir() -> str:
    override = os.environ.get("UNCLECODE_HERMES_HOME")
    if override:
        return os.path.expanduser(override)
    return os.path.expanduser(_DEFAULT_HOME)


DEFAULT_CONFIG = {
    "llm": {
        "provider": "groq",
        "model": "llama-3.1-8b-instant",
        "api_key": None,
    },
    "transcription": {
        "provider": "groq",
        "model": "distil-whisper-large-v3-en",
        "api_key": None,
    },
    "cache": {
        "enabled": True,
        "directory": os.path.join(_DEFAULT_HOME, "cache"),
    },
    "source_type": "auto",
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _config_path() -> str:
    home = _home_dir()
    # Upstream setup wrote config.yaml; loader historically used config.yml.
    for name in ("config.yml", "config.yaml"):
        path = os.path.join(home, name)
        if os.path.exists(path):
            return path
    return os.path.join(home, "config.yml")


def ensure_default_config() -> str:
    """Create isolated config dir + default config if missing. Returns config path."""
    home = _home_dir()
    os.makedirs(home, exist_ok=True)
    path = _config_path()
    if not os.path.exists(path):
        cfg = dict(DEFAULT_CONFIG)
        cfg["cache"] = dict(DEFAULT_CONFIG["cache"])
        cfg["cache"]["directory"] = os.path.join(home, "cache")
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, default_flow_style=False)
    os.makedirs(os.path.join(home, "cache"), exist_ok=True)
    return path


def load_config(require_api_keys: bool = True) -> Dict[str, Any]:
    ensure_default_config()
    config_path = _config_path()
    user_config: Dict[str, Any] = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
            if isinstance(loaded, dict):
                user_config = loaded

    config = _deep_merge(DEFAULT_CONFIG, user_config)

    for service in ("llm", "transcription"):
        service_cfg = config.setdefault(service, {})
        provider = service_cfg.get("provider") or "groq"
        env_var = f"{provider.upper()}_API_KEY"
        if not service_cfg.get("api_key"):
            service_cfg["api_key"] = os.getenv(env_var)
        if require_api_keys and not service_cfg.get("api_key"):
            # mlx is local — no API key required for transcription
            if service == "transcription" and provider == "mlx":
                continue
            if service == "llm":
                # LLM only required when --llm_prompt is used; keep soft here
                continue
            raise ValueError(
                f"No API key found for {provider} in config or environment variable {env_var}. "
                f"Set it in {config_path} or as an environment variable."
            )

    cache_dir = config.get("cache", {}).get("directory") or os.path.join(_home_dir(), "cache")
    config.setdefault("cache", {})["directory"] = os.path.expanduser(cache_dir)
    return config


class _LazyConfig:
    """Avoid import-time hard fail when API keys are not set yet."""

    def __init__(self) -> None:
        self._cfg: Optional[Dict[str, Any]] = None

    def _get(self) -> Dict[str, Any]:
        if self._cfg is None:
            self._cfg = load_config(require_api_keys=False)
        return self._cfg

    def reload(self, require_api_keys: bool = False) -> Dict[str, Any]:
        self._cfg = load_config(require_api_keys=require_api_keys)
        return self._cfg

    def __getitem__(self, key):
        return self._get()[key]

    def get(self, key, default=None):
        return self._get().get(key, default)

    def __contains__(self, key):
        return key in self._get()

    def keys(self):
        return self._get().keys()

    def items(self):
        return self._get().items()

    def values(self):
        return self._get().values()

    def __repr__(self) -> str:
        return f"LazyConfig({self._get()!r})"


CONFIG = _LazyConfig()
