from airouter.models import ModelSpec
from airouter.scorer import score_request


def make_model(capabilities, max_context=32768, priority=50):
    return ModelSpec(
        name="test-model",
        provider="ollama",
        capabilities=capabilities,
        max_context=max_context,
        priority=priority,
    )


def make_features(capabilities=None, repo_aware=False, context_tokens=0):
    return {
        "prompt": "test",
        "capabilities": capabilities or [],
        "repo_aware": repo_aware,
        "context_tokens": context_tokens,
    }


class TestCapabilityScoring:
    def test_matching_capability_adds_30(self):
        model = make_model(capabilities=["coding"])
        features = make_features(capabilities=["coding"])
        score = score_request(features, model)
        assert score == 30 + 50  # capability match + default priority

    def test_multiple_matching_capabilities(self):
        model = make_model(capabilities=["coding", "security"])
        features = make_features(capabilities=["coding", "security"])
        score = score_request(features, model)
        assert score == 60 + 50

    def test_no_capability_match(self):
        model = make_model(capabilities=["security"])
        features = make_features(capabilities=["coding"])
        score = score_request(features, model)
        assert score == 50  # only priority

    def test_partial_capability_match(self):
        model = make_model(capabilities=["coding"])
        features = make_features(capabilities=["coding", "security"])
        score = score_request(features, model)
        assert score == 30 + 50


class TestRepoAwareScoring:
    def test_repo_aware_with_repository_capability_adds_25(self):
        model = make_model(capabilities=["repository"])
        features = make_features(repo_aware=True, capabilities=["repository"])
        score = score_request(features, model)
        # 30 capability + 25 repo + 50 priority
        assert score == 105

    def test_repo_aware_without_repository_capability_no_bonus(self):
        model = make_model(capabilities=["coding"])
        features = make_features(repo_aware=True, capabilities=[])
        score = score_request(features, model)
        assert score == 50  # only priority, no bonus

    def test_not_repo_aware_no_bonus(self):
        model = make_model(capabilities=["repository"])
        features = make_features(repo_aware=False, capabilities=[])
        score = score_request(features, model)
        assert score == 50


class TestContextTokenScoring:
    def test_tokens_exceed_half_max_context_adds_20(self):
        model = make_model(capabilities=[], max_context=32768, priority=0)
        features = make_features(context_tokens=20000)  # > 16384
        score = score_request(features, model)
        assert score == 20

    def test_tokens_below_half_max_context_no_bonus(self):
        model = make_model(capabilities=[], max_context=32768, priority=0)
        features = make_features(context_tokens=5000)  # < 16384
        score = score_request(features, model)
        assert score == 0

    def test_tokens_exactly_half_no_bonus(self):
        model = make_model(capabilities=[], max_context=32768, priority=0)
        features = make_features(context_tokens=16384)  # == half, not >
        score = score_request(features, model)
        assert score == 0


class TestPriorityScoring:
    def test_priority_is_always_added(self):
        model = make_model(capabilities=[], priority=100)
        features = make_features()
        assert score_request(features, model) == 100

    def test_zero_priority(self):
        model = make_model(capabilities=[], priority=0)
        features = make_features()
        assert score_request(features, model) == 0
