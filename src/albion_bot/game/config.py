import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "islands.json"


@dataclass
class Point:
    rel_x: int
    rel_y: int


def load_island_config(path: Path = CONFIG_PATH) -> dict[str, Point]:
    with open(path) as f:
        raw = json.load(f)
    return {name: Point(**vals) for name, vals in raw.items()}
