from pathlib import Path

import yaml

DEFAULT_MAPPING = {
    "move_forward": "W",
    "attack": "1",
    "loot": "F",
    "heal": "H",
    "stop": None,
}


def load_action_mapping(mapping_path: str | None = None) -> dict:
    if mapping_path is None:
        return DEFAULT_MAPPING.copy()
    path = Path(mapping_path)
    if not path.exists():
        raise FileNotFoundError(mapping_path)
    data = yaml.safe_load(path.read_text()) or {}
    merged = DEFAULT_MAPPING.copy()
    merged.update(data)
    return merged
