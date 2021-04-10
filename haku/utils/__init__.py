import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import IO, Any, Callable, List, Optional, Union

from PIL import Image


def tmpdir(tmpname: str = "haku") -> Path:
    """Geenrate a temporary directory"""

    tempfile.mkdtemp()
    return Path(tempfile.gettempdir()) / tmpname


def call_safe(cb: Callable, *args, **argv) -> Any:
    """Safely call a Callable"""

    try:
        cb(*args, **argv)
    except TypeError:
        return None


def abstract(method: Callable) -> Callable:
    """Marks a method as abstract"""

    def wrapper(*args, **kwargs):
        raise NotImplementedError(f"Missing required method {repr(method)}")

    return wrapper


def chunks(lst, n):
    """Yield successive n-sized chunks from lst"""

    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def write_image(image: Image.Image, path: Path, fmt="png", cleanup=True):
    """Write an image to disk"""

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(path), format=fmt)

    if cleanup:
        image.close()
        del image


def ensure_bytesio(
    candidate: Union[Path, IO[bytes]], mode="wb"
) -> Union[IO[bytes], bool]:
    """Ensure as bytes iostream"""

    if isinstance(candidate, Path):
        return candidate.open(mode), True

    return candidate, False


def cleanup_folder(folder: Path):
    """Cleanup a folder"""

    shutil.rmtree(folder)


def safe_path(
    path: Union[Path, str],
    unsafe_chars: Optional[str] = None,
    replacement: str = "",
) -> Path:
    """Clean a path from banned chars"""

    unsafe_chars = unsafe_chars or os.sep
    path = re.sub(unsafe_chars, replacement, str(path))
    return Path(path)


def get_editor(candidates: List[str] = ["vim", "emacs", "nano"]) -> str:
    """Get editor"""

    for candidate in candidates:
        if shutil.which(candidate) is not None:
            return candidate

    return None


# from https://github.com/fmoo/python-editor/blob/master/editor.py
def get_editor_args(editor: str) -> List[str]:
    """Get recommended editor flags"""

    if editor in ["vim"]:
        return ["-f", "-o"]
    elif editor in ["emacs"]:
        return ["-nw"]
    elif editor in ["nano"]:
        return ["-R"]
    elif editor in ["code", "codium"]:
        return ["-w", "-n"]

    return []
