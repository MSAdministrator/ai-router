import pytest
from unittest.mock import patch, MagicMock
from airouter.ollama import is_installed, get_version, ensure_installed, OllamaError


class TestIsInstalled:
    @patch("airouter.ollama.shutil.which", return_value="/usr/local/bin/ollama")
    def test_true_when_ollama_on_path(self, _mock):
        assert is_installed() is True

    @patch("airouter.ollama.shutil.which", return_value=None)
    def test_false_when_not_on_path(self, _mock):
        assert is_installed() is False


class TestGetVersion:
    @patch("airouter.ollama.is_installed", return_value=False)
    def test_none_when_not_installed(self, _mock):
        assert get_version() is None

    @patch("airouter.ollama.is_installed", return_value=True)
    @patch("airouter.ollama.subprocess.run")
    def test_returns_version_string(self, mock_run, _installed):
        mock_run.return_value = MagicMock(stdout="ollama version 0.3.0\n", stderr="")
        assert get_version() == "ollama version 0.3.0"

    @patch("airouter.ollama.is_installed", return_value=True)
    @patch("airouter.ollama.subprocess.run")
    def test_falls_back_to_stderr(self, mock_run, _installed):
        mock_run.return_value = MagicMock(stdout="", stderr="ollama version 0.3.0")
        assert get_version() == "ollama version 0.3.0"

    @patch("airouter.ollama.is_installed", return_value=True)
    @patch("airouter.ollama.subprocess.run", side_effect=Exception("fail"))
    def test_returns_none_on_subprocess_error(self, _run, _installed):
        assert get_version() is None


class TestEnsureInstalled:
    @patch("airouter.ollama.is_installed", return_value=True)
    def test_does_not_install_when_already_present(self, mock_installed):
        ensure_installed()  # should not raise
        mock_installed.assert_called()

    @patch("airouter.ollama.install_ollama")
    @patch("airouter.ollama.is_installed", side_effect=[False, True])
    def test_calls_install_when_missing(self, _installed, mock_install):
        ensure_installed()
        mock_install.assert_called_once()

    @patch("airouter.ollama.install_ollama")
    @patch("airouter.ollama.is_installed", side_effect=[False, False])
    def test_raises_if_still_missing_after_install(self, _installed, _install):
        with pytest.raises(OllamaError):
            ensure_installed()
