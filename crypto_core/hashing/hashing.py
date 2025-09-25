import hashlib
from pathlib import Path


def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    """
    Посчитать хэш от байтов.
    Поддерживает: md5, sha1, sha224, sha256, sha384, sha512.
    Возвращает hex-строку.
    """
    algo = algorithm.lower()
    if algo not in hashlib.algorithms_available:
        raise ValueError(f"Алгоритм {algorithm} не поддерживается")
    h = hashlib.new(algo)
    h.update(data)
    return h.hexdigest()


def hash_file(filepath: str | Path, algorithm: str = "sha256") -> str:
    """
    Посчитать хэш от файла.
    """
    algo = algorithm.lower()
    if algo not in hashlib.algorithms_available:
        raise ValueError(f"Алгоритм {algorithm} не поддерживается")
    h = hashlib.new(algo)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
