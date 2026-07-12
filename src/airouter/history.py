
import json
from pathlib import Path

HISTORY = Path.home() / ".routeai_history.jsonl"

def log(entry):
    with open(HISTORY, "a") as f:
        f.write(json.dumps(entry) + "\n")
