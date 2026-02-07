import hashlib
import pickle
from pathlib import Path
from typing import Any, Optional


def _compute_file_hash(file: Path) -> str:
    """
    Compute SHA256 hash of a file's contents.

    Args:
        file (Path): Path to the file.

    Returns:
        str: Hexadecimal hash string.
    """
    sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_cache_key(*files: Path) -> str:
    """
    Generate a cache key from multiple file hashes.

    Args:
        *files (Path): One or more file paths to hash.

    Returns:
        str: Combined hash key.
    """
    combined = "".join(_compute_file_hash(fp) for fp in files)
    return hashlib.sha256(combined.encode()).hexdigest()


def load_from_cache(cache_dir: Path, cache_key: str) -> Optional[Any]:
    """
    Load cached data if it exists.

    Args:
        cache_dir (Path): Directory containing cache files.
        cache_key (str): Unique identifier for this cache entry.

    Returns:
        Cached data if found, otherwise None.
    """
    cache_file = cache_dir / f"{cache_key}.pkl"
    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except Exception:
            # If cache is corrupted, ignore it
            return None
    return None


def save_to_cache(cache_dir: Path, cache_key: str, data: Any) -> None:
    """
    Save data to cache.

    Args:
        cache_dir (Path): Directory to store cache files.
        cache_key (str): Unique identifier for this cache entry.
        data (Any): Data to cache.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{cache_key}.pkl"
    with open(cache_file, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
