from dataclasses import dataclass
from typing import List


@dataclass
class ModelSpec:
    name: str
    provider: str
    capabilities: List[str]
    max_context: int
    priority: int = 50
