import sys
import subprocess
from .models import ModelSpec
from .ollama import ensure_installed


class ModelRegistry:
    def __init__(self, config):
        self.config = config

    def installed_models(self):
        ensure_installed()

        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            lines = result.stdout.splitlines()[1:]
            return [line.split()[0] for line in lines if line.strip()] or [
                "no models installed"
            ]
        except Exception as e:
            return e

    def available_specs(self):
        installed = set(self.installed_models())
        specs = []
        for _, cfg in self.config["models"].items():
            if cfg["name"] in installed:
                specs.append(ModelSpec(**cfg))
        return specs

    def install_models(self):
        ensure_installed()

        for _, cfg in self.config["models"].items():
            try:
                result = subprocess.run(
                    ["ollama", "pull", cfg["name"]],
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    check=True,
                )
                yield result
            except Exception as e:
                return e
