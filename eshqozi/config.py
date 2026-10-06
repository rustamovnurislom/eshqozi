from dataclasses import dataclass, field
from pathlib import Path
import os
from urllib.parse import urlsplit


def load_dotenv(path: str = ".env") -> None:
    file = Path(path)
    if not file.exists():
        return
    for raw in file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep and key.strip().replace("_", "").isalnum():
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
    mode: str = "demo"
    db_path: str = "var/eshqozi.sqlite3"
    knowledge_path: str = "data/knowledge.json"
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 4
    telegram_token: str = field(default="", repr=False)
    openai_key: str = field(default="", repr=False)
    model: str = "gpt-4.1-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    telegram_base_url: str = "https://api.telegram.org"
    history_turns: int = 6
    retention_hours: int = 72
    per_minute: int = 8
    per_day: int = 100
    global_per_day: int = 2000
    max_input_chars: int = 4000
    lease_seconds: int = 300
    max_attempts: int = 5
    backup_days: int = 7

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        mappings = {
            "mode": "ESHQOZI_MODE", "db_path": "ESHQOZI_DB",
            "knowledge_path": "ESHQOZI_KNOWLEDGE", "host": "ESHQOZI_HOST",
            "port": "ESHQOZI_PORT", "workers": "ESHQOZI_WORKERS",
            "telegram_token": "TELEGRAM_BOT_TOKEN", "openai_key": "ESHQOZI_AI_KEY",
            "model": "OPENAI_MODEL", "openai_base_url": "OPENAI_BASE_URL",
            "history_turns": "ESHQOZI_HISTORY_TURNS", "retention_hours": "ESHQOZI_RETENTION_HOURS",
            "per_minute": "ESHQOZI_PER_MINUTE", "per_day": "ESHQOZI_PER_DAY",
            "global_per_day": "ESHQOZI_GLOBAL_PER_DAY",
            "backup_days": "ESHQOZI_BACKUP_DAYS",
        }
        integer_fields = {"port", "workers", "history_turns", "retention_hours", "per_minute", "per_day", "global_per_day", "backup_days"}
        values = {key: int(os.environ[name]) if key in integer_fields else os.environ[name]
                  for key, name in mappings.items() if os.environ.get(name)}
        if 'openai_key' not in values and os.environ.get('OPENAI_API_KEY'):
            values['openai_key'] = os.environ['OPENAI_API_KEY']
        settings = cls(**values)
        settings.validate()
        return settings

    def validate(self) -> None:
        if self.mode not in {"demo", "production"}:
            raise ValueError("ESHQOZI_MODE demo yoki production bo‘lishi kerak")
        if not 1 <= self.workers <= 16 or not 1 <= self.port <= 65535:
            raise ValueError("Worker yoki port qiymati noto‘g‘ri")
        if any(value < 1 for value in (self.history_turns, self.retention_hours, self.per_minute, self.per_day, self.global_per_day, self.backup_days)):
            raise ValueError("Limitlar musbat bo‘lishi kerak")
        if self.mode == "production":
            missing = [name for name, value in (("TELEGRAM_BOT_TOKEN", self.telegram_token), ("ESHQOZI_AI_KEY", self.openai_key)) if not value]
            if missing:
                raise ValueError("Yetishmayotgan sozlama: " + ", ".join(missing))
        for url in (self.openai_base_url, self.telegram_base_url):
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query:
                raise ValueError("Tashqi API manzili HTTPS bo‘lishi kerak")
