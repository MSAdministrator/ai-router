import pytest
from unittest.mock import patch, MagicMock
from airouter.registry import ModelRegistry
from airouter.models import ModelSpec


MINIMAL_CONFIG = {
    "models": {
        "model-a": {
            "name": "model-a:latest",
            "provider": "ollama",
            "capabilities": ["coding"],
            "max_context": 32768,
            "priority": 50,
        },
        "model-b": {
            "name": "model-b:latest",
            "provider": "ollama",
            "capabilities": ["security"],
            "max_context": 32768,
            "priority": 80,
        },
    }
}


@pytest.fixture
def registry():
    return ModelRegistry(MINIMAL_CONFIG)


class TestInstalledModels:
    @patch("airouter.registry.ensure_installed")
    @patch("airouter.registry.subprocess.run")
    def test_returns_model_names(self, mock_run, _ensure):
        mock_run.return_value = MagicMock(
            stdout="NAME\nmodel-a:latest  ...\nmodel-b:latest  ...\n"
        )
        result = ModelRegistry(MINIMAL_CONFIG).installed_models()
        assert "model-a:latest" in result
        assert "model-b:latest" in result

    @patch("airouter.registry.ensure_installed")
    @patch("airouter.registry.subprocess.run")
    def test_returns_placeholder_when_empty(self, mock_run, _ensure):
        mock_run.return_value = MagicMock(stdout="NAME\n")
        result = ModelRegistry(MINIMAL_CONFIG).installed_models()
        assert result == ["no models installed"]

    @patch("airouter.registry.ensure_installed")
    @patch("airouter.registry.subprocess.run")
    def test_returns_exception_on_error(self, mock_run, _ensure):
        mock_run.side_effect = FileNotFoundError("ollama not found")
        result = ModelRegistry(MINIMAL_CONFIG).installed_models()
        assert isinstance(result, Exception)


class TestAvailableSpecs:
    @patch.object(ModelRegistry, "installed_models", return_value=["model-a:latest"])
    def test_only_installed_models_returned(self, _mock):
        specs = ModelRegistry(MINIMAL_CONFIG).available_specs()
        assert len(specs) == 1
        assert specs[0].name == "model-a:latest"

    @patch.object(ModelRegistry, "installed_models", return_value=[])
    def test_empty_when_nothing_installed(self, _mock):
        specs = ModelRegistry(MINIMAL_CONFIG).available_specs()
        assert specs == []

    @patch.object(
        ModelRegistry,
        "installed_models",
        return_value=["model-a:latest", "model-b:latest"],
    )
    def test_all_installed_configs_returned(self, _mock):
        specs = ModelRegistry(MINIMAL_CONFIG).available_specs()
        names = {s.name for s in specs}
        assert names == {"model-a:latest", "model-b:latest"}

    @patch.object(ModelRegistry, "installed_models", return_value=["model-a:latest"])
    def test_spec_fields_match_config(self, _mock):
        specs = ModelRegistry(MINIMAL_CONFIG).available_specs()
        spec = specs[0]
        assert isinstance(spec, ModelSpec)
        assert spec.capabilities == ["coding"]
        assert spec.max_context == 32768
        assert spec.priority == 50
