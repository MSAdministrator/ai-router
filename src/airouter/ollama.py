import platform
import shutil
import subprocess


def ensure_installed() -> None:
    """
    Ensure Ollama exists before continuing.
    """
    if not is_installed():
        install_ollama()

    if not is_installed():
        raise OllamaError("Ollama is required but is not installed.")


def stream(prompt: str, model: str):
    ensure_installed()

    process = subprocess.Popen(
        ["ollama", "run", model],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    if process.stdin is None or process.stdout is None:
        raise OllamaError("Failed to open Ollama process streams")

    process.stdin.write(prompt)
    process.stdin.close()

    for line in process.stdout:
        yield line


class OllamaError(RuntimeError):
    """Base exception for Ollama-related failures."""


def is_installed() -> bool:
    """
    Returns True if the Ollama executable can be found.
    """
    return shutil.which("ollama") is not None


def get_version() -> str | None:
    """
    Returns the installed Ollama version or None if unavailable.
    """
    if not is_installed():
        return None

    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception:
        return None


def install_ollama(force: bool = False) -> bool:
    """
    Install Ollama if it is not already installed.

    Returns
    -------
    bool
        True if Ollama is installed after this function completes.

    Raises
    ------
    OllamaError
        If installation fails.
    """

    if is_installed() and not force:
        return True

    system = platform.system()

    try:
        if system in ("Linux", "Darwin"):
            # Official installer
            subprocess.run(
                "curl -fsSL https://ollama.com/install.sh | sh",
                shell=True,
                check=True,
            )

        elif system == "Windows":
            powershell = (
                "winget install Ollama.Ollama "
                "--accept-package-agreements "
                "--accept-source-agreements"
            )

            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    powershell,
                ],
                check=True,
            )

        else:
            raise OllamaError(f"Unsupported platform: {system}")

    except subprocess.CalledProcessError as exc:
        raise OllamaError(f"Failed installing Ollama: {exc}") from exc

    if not is_installed():
        raise OllamaError(
            "Installation completed but the ollama executable could not be found."
        )

    return True
