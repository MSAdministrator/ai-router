
import subprocess

def get_git_diff():
    try:
        return subprocess.run(["git", "diff"], capture_output=True, text=True).stdout
    except Exception:
        return ""

def infer(prompt, diff):
    caps = []
    if diff:
        caps.append("repository")
    if "security" in prompt:
        caps.append("security")
    if "refactor" in prompt:
        caps.append("architecture")
    if "implement" in prompt:
        caps.append("coding")
    return caps

def build_context(prompt: str):
    diff = get_git_diff()
    return {
        "prompt": prompt,
        "repo_aware": bool(diff.strip()),
        "context_tokens": len(prompt.split()),
        "capabilities": infer(prompt, diff)
    }
