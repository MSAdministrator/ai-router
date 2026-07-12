import yaml
from pathlib import Path


def load_config():
    path = Path(__file__).resolve().parent.parent / "config" / "models.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)
