from hashlib import sha256
from pathlib import Path
from pickle import HIGHEST_PROTOCOL, dump, load
from typing import Any, Optional


def _compute_file_hash(file: Path) -> str:
    """
    Compute SHA256 hash of a file's contents.

    Args:
        file (Path): Path to the file.

    Returns:
        str: Hexadecimal hash string.
    """
    sha256_hash = sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def get_cache_key(*files: Path) -> str:
    """
    Generate a cache key from multiple file hashes.

    Args:
        *files (Path): One or more file paths to hash.

    Returns:
        str: Combined hash key.
    """
    combined = "".join(_compute_file_hash(file_path) for file_path in files)
    return sha256(combined.encode()).hexdigest()


def load_from_cache(cache_directory: Path, cache_key: str) -> Optional[Any]:
    """
    Load cached data if it exists.

    Args:
        cache_directory (Path): Directory containing cache files.
        cache_key (str): Unique identifier for this cache entry.

    Returns:
        Cached data if found, otherwise None.
    """
    cache_file = cache_directory / f"{cache_key}.pkl"
    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                return load(f)
        except Exception:
            # If cache is corrupted, ignore it
            return None
    return None


def save_to_cache(cache_directory: Path, cache_key: str, data: Any) -> None:
    """
    Save data to cache.

    Args:
        cache_directory (Path): Directory to store cache files.
        cache_key (str): Unique identifier for this cache entry.
        data (Any): Data to cache.
    """
    cache_directory.mkdir(parents=True, exist_ok=True)
    cache_file = cache_directory / f"{cache_key}.pkl"
    with open(cache_file, "wb") as f:
        dump(data, f, protocol=HIGHEST_PROTOCOL)
