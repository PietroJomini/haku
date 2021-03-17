import tempfile
from pathlib import Path
from typing import IO, Any, Callable, Union

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


def write_image(image: Image.Image, path: Path, filename: str, fmt="png", cleanup=True):
    """Write an image to disk"""

    path.mkdir(parents=True, exist_ok=True)
    image.save(str(path / f"{filename}.{fmt}"), format=fmt)

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
