from unittest.mock import patch
from airouter.context import infer, build_context


class TestInfer:
    def test_security_keyword_inferred(self):
        caps = infer("check security issue", diff="")
        assert "security" in caps

    def test_refactor_keyword_inferred(self):
        caps = infer("refactor the module", diff="")
        assert "architecture" in caps

    def test_implement_keyword_inferred(self):
        caps = infer("implement login flow", diff="")
        assert "coding" in caps

    def test_non_empty_diff_adds_repository(self):
        caps = infer("do something", diff="--- a/foo.py\n+++ b/foo.py")
        assert "repository" in caps

    def test_empty_diff_no_repository(self):
        caps = infer("do something", diff="")
        assert "repository" not in caps

    def test_no_keywords_no_caps(self):
        caps = infer("hello world", diff="")
        assert caps == []

    def test_multiple_keywords_all_inferred(self):
        caps = infer("implement security refactor", diff="")
        assert "coding" in caps
        assert "security" in caps
        assert "architecture" in caps


class TestBuildContext:
    @patch("airouter.context.get_git_diff", return_value="diff --git a/foo.py")
    def test_repo_aware_when_diff_present(self, _mock):
        result = build_context("implement login")
        assert result["repo_aware"] is True

    @patch("airouter.context.get_git_diff", return_value="")
    def test_not_repo_aware_when_no_diff(self, _mock):
        result = build_context("implement login")
        assert result["repo_aware"] is False

    @patch("airouter.context.get_git_diff", return_value="")
    def test_context_tokens_is_word_count(self, _mock):
        result = build_context("one two three four five")
        assert result["context_tokens"] == 5

    @patch("airouter.context.get_git_diff", return_value="")
    def test_prompt_preserved(self, _mock):
        result = build_context("hello world")
        assert result["prompt"] == "hello world"

    @patch("airouter.context.get_git_diff", return_value="")
    def test_capabilities_inferred(self, _mock):
        result = build_context("implement a security check")
        assert "coding" in result["capabilities"]
        assert "security" in result["capabilities"]
