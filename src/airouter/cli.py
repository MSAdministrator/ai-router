import fire
from .config import load_config
from .registry import ModelRegistry
from .router import Router
from .context import build_context
from .ollama import stream


class RouteAI:
    def __init__(self):
        self.config = load_config()
        self.registry = ModelRegistry(self.config)
        self.router = Router(self.registry)

    def chat(self, prompt: str, verbose: bool = False):
        features = build_context(prompt)
        model = self.router.pick_model(features)

        if not model:
            print("[routeai] No model available")
            return

        if verbose:
            print(f"[routeai] selected model: {model.name}")

        return stream(prompt, model.name)

    def models(self):
        return self.registry.installed_models()
    
    def install_models(self):
        return self.registry.install_models()

    def explain(self, prompt: str):
        features = build_context(prompt)
        model = self.router.pick_model(features)
        return {
            "selected_model": model.name if model else None,
            "features": features
        }

    def doctor(self):
        return {
            "ollama_installed_models": self.registry.installed_models()
        }

def main():
    fire.Fire(RouteAI)
