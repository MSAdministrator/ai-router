from unittest.mock import MagicMock
from airouter.models import ModelSpec
from airouter.router import Router


def make_spec(name, capabilities, max_context=32768, priority=50):
    return ModelSpec(
        name=name,
        provider="ollama",
        capabilities=capabilities,
        max_context=max_context,
        priority=priority,
    )


def make_router(specs):
    registry = MagicMock()
    registry.available_specs.return_value = specs
    return Router(registry)


def make_features(capabilities=None, repo_aware=False, context_tokens=0):
    return {
        "prompt": "test",
        "capabilities": capabilities or [],
        "repo_aware": repo_aware,
        "context_tokens": context_tokens,
    }


class TestPickModel:
    def test_returns_none_when_no_models(self):
        router = make_router([])
        assert router.pick_model(make_features()) is None

    def test_returns_single_available_model(self):
        spec = make_spec("only-model", capabilities=[])
        router = make_router([spec])
        assert router.pick_model(make_features()) is spec

    def test_picks_higher_priority_model(self):
        low = make_spec("low", capabilities=[], priority=10)
        high = make_spec("high", capabilities=[], priority=90)
        router = make_router([low, high])
        assert router.pick_model(make_features()).name == "high"

    def test_picks_model_with_matching_capabilities(self):
        generic = make_spec("generic", capabilities=[], priority=80)
        specialist = make_spec("specialist", capabilities=["coding"], priority=50)
        router = make_router([generic, specialist])
        result = router.pick_model(make_features(capabilities=["coding"]))
        # specialist: 30 (cap) + 50 (priority) = 80; generic: 80 (priority)
        # tie broken by sorted stability – first encountered wins; both equal here.
        # Use a case that clearly favours the specialist.
        assert result.name in ("generic", "specialist")  # sanity check
        # Now make specialist clearly win
        dominant = make_spec(
            "dominant", capabilities=["coding", "security"], priority=50
        )
        router2 = make_router([generic, dominant])
        result2 = router2.pick_model(make_features(capabilities=["coding", "security"]))
        assert result2.name == "dominant"

    def test_picks_repo_aware_model_for_diff(self):
        plain = make_spec("plain", capabilities=[], priority=70)
        repo = make_spec("repo-model", capabilities=["repository"], priority=50)
        router = make_router([plain, repo])
        result = router.pick_model(
            make_features(repo_aware=True, capabilities=["repository"])
        )
        # repo-model: 30 (cap) + 25 (repo_aware) + 50 (priority) = 105; plain: 70
        assert result.name == "repo-model"

    def test_registry_available_specs_called(self):
        registry = MagicMock()
        registry.available_specs.return_value = []
        router = Router(registry)
        router.pick_model(make_features())
        registry.available_specs.assert_called_once()
