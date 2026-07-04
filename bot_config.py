import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'data', 'config.json')


@dataclass
class BotConfig:
    log_channel_id: Optional[int] = None
    log_send_enabled: bool = False

    def save(self):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls) -> 'BotConfig':
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        return cls()
