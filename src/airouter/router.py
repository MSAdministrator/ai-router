from .scorer import score_request


class Router:
    def __init__(self, registry):
        self.registry = registry

    def pick_model(self, features):
        models = self.registry.available_specs()
        if not models:
            return None

        ranked = sorted(models, key=lambda m: score_request(features, m), reverse=True)
        return ranked[0]
