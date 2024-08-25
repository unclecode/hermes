import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Cache:
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get('enabled', True)
        self.cache_dir = Path(config.get('directory', Path.home() / '.hermes' / 'cache'))
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[str]:
        if not self.enabled:
            return None
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)['transcription']
        return None

    def set(self, key: str, value: str):
        if not self.enabled:
            return
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump({'transcription': value}, f)
            
    def clear(self):
        if not self.enabled:
            return
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()