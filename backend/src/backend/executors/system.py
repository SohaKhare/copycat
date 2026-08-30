import platform


def get_current_environment() -> str:
    """
    Detect the operating system where
    CopyCat is currently running.
    """

    system = platform.system().lower()

    environment_mapping = {
        "windows": "windows",
        "darwin": "macos",
        "linux": "linux",
    }

    return environment_mapping.get(
        system,
        "unknown",
    )