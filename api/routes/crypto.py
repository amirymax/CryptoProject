# api/routes/crypto.py
from typing import Optional, Dict, Any, List
from base64 import b64encode, b64decode
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# --- Импорты из вашего crypto_core ---
# Классика (Цезарь)
try:
    from crypto_core.classic.caesar import encrypt as caesar_enc, decrypt as caesar_dec  # type: ignore
except Exception:
    caesar_enc = caesar_dec = None

# Хэши
try:
    from crypto_core.hashing import sha256_hex  # type: ignore
except Exception:
    sha256_hex = None

# RSA (на cryptography)
try:
    from crypto_core.asymmetric import rsa as rsa_core  # type: ignore
except Exception:
    rsa_core = None

router = APIRouter(prefix="/crypto", tags=["crypto"])


class CryptoRequest(BaseModel):
    algorithm: str
    text: str
    params: Optional[Dict[str, Any]] = None


# ------------- Вспомогательные -------------
def _require(obj, name: str):
    if obj is None:
        raise HTTPException(status_code=500, detail=f"{name} не подключён(а) в crypto_core")
    return obj

def _require_int(d: Dict[str, Any], key: str, title: str) -> int:
    if d is None or key not in d:
        raise HTTPException(status_code=422, detail=f"{title} обязателен (params.{key})")
    try:
        return int(d[key])
    except Exception:
        raise HTTPException(status_code=422, detail=f"{title} должен быть целым числом")

def _load_public_key_from_params(params: Dict[str, Any]):
    """public_pem (string) или public_key_path (file) → public_key object; иначе используется глобальная пара."""
    _require(rsa_core, "RSA")
    if not params:
        return _RSA_PUB
    pub_pem = params.get("public_pem")
    pub_path = params.get("public_key_path")
    if pub_pem:
        from cryptography.hazmat.primitives import serialization
        return serialization.load_pem_public_key(pub_pem.encode())
    if pub_path:
        return rsa_core.load_public_key(pub_path)
    return _RSA_PUB

def _load_private_key_from_params(params: Dict[str, Any]):
    """private_pem (string) или private_key_path (file) → private_key object; иначе используется глобальная пара."""
    _require(rsa_core, "RSA")
    if not params:
        return _RSA_PRIV
    priv_pem = params.get("private_pem")
    priv_path = params.get("private_key_path")
    if priv_pem:
        from cryptography.hazmat.primitives import serialization
        return serialization.load_pem_private_key(priv_pem.encode(), password=None)
    if priv_path:
        return rsa_core.load_private_key(priv_path, password=None)
    return _RSA_PRIV

def _rsa_max_chunk_bytes(public_key) -> int:
    """max plaintext bytes for RSA-OAEP(SHA-256): k - 2*hLen - 2"""
    key_size_bytes = public_key.key_size // 8
    hlen = 32  # SHA-256
    return key_size_bytes - 2 * hlen - 2

def _rsa_encrypt_to_base64_parts(public_key, text: str) -> List[str]:
    """Шифруем длинный текст кусками и кодируем каждую часть в base64."""
    max_chunk = _rsa_max_chunk_bytes(public_key)
    plaintext = text.encode("utf-8")
    parts: List[str] = []
    for i in range(0, len(plaintext), max_chunk):
        chunk = plaintext[i:i + max_chunk]
        ct = rsa_core.encrypt_message(public_key, chunk.decode("utf-8"))
        parts.append(b64encode(ct).decode("ascii"))
    return parts

def _rsa_decrypt_from_base64_parts(private_key, cipher_concat: str) -> str:
    """Дешифруем base64-части (разделены ';') и склеиваем результат."""
    raw_parts = [p for p in cipher_concat.split(";") if p]
    out = bytearray()
    for b64 in raw_parts:
        ct = b64decode(b64)
        # Ваша decrypt_message ожидает bytes
        pt = rsa_core.decrypt_message(private_key, ct).encode("utf-8")
        out.extend(pt)
    return out.decode("utf-8")


# ------------- Глобальная demo-пара ключей (для простых проверок) -------------
if rsa_core is not None:
    _RSA_PRIV, _RSA_PUB = rsa_core.generate_keys(key_size=2048)
else:
    _RSA_PRIV = _RSA_PUB = None


# ================= /crypto/encrypt =================
@router.post("/encrypt")
def encrypt(req: CryptoRequest):
    algo = (req.algorithm or "").strip().lower()
    text = req.text
    params = req.params or {}

    # Цезарь
    if algo in {"цезарь", "caesar"}:
        _require(caesar_enc, "Цезарь")
        key = _require_int(params, "key", "Ключ")
        try:
            return {"result": caesar_enc(text, key)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка Цезаря (encrypt): {e}")

    # SHA256
    if algo in {"sha256", "sha-256"}:
        if sha256_hex is not None:
            try:
                return {"result": sha256_hex(text)}
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Ошибка SHA256: {e}")
        else:
            # fallback
            import hashlib
            return {"result": hashlib.sha256(text.encode("utf-8")).hexdigest()}

    # RSA
    if algo == "rsa":
        pub_key = _load_public_key_from_params(params)
        try:
            parts = _rsa_encrypt_to_base64_parts(pub_key, text)
            # Возвращаем через ';' — как договорились
            return {"result": ";".join(parts)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка RSA (encrypt): {e}")

    # Эль-Гамаль — при необходимости добавите аналогично
    if algo in {"эль-гамаль", "elgamal", "el-gamal"}:
        raise HTTPException(status_code=501, detail="Эль-Гамаль не реализован в этом роутере (добавьте при необходимости)")

    raise HTTPException(status_code=400, detail=f"Неизвестный алгоритм: {req.algorithm}")


# ================= /crypto/decrypt =================
@router.post("/decrypt")
def decrypt(req: CryptoRequest):
    algo = (req.algorithm or "").strip().lower()
    text = req.text  # для RSA здесь придёт строка из base64-частей, соединённых ';'
    params = req.params or {}

    # Цезарь
    if algo in {"цезарь", "caesar"}:
        _require(caesar_dec, "Цезарь")
        key = _require_int(params, "key", "Ключ")
        try:
            return {"result": caesar_dec(text, key)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка Цезаря (decrypt): {e}")

    # RSA
    if algo == "rsa":
        priv_key = _load_private_key_from_params(params)
        try:
            plain = _rsa_decrypt_from_base64_parts(priv_key, text)
            return {"result": plain}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка RSA (decrypt): {e}")

    raise HTTPException(status_code=400, detail=f"Неизвестный алгоритм: {req.algorithm}")


# ================= /crypto/hash =================
@router.post("/hash")
def do_hash(req: CryptoRequest):
    algo = (req.algorithm or "").strip().lower()
    text = req.text

    if algo in {"sha256", "sha-256"}:
        if sha256_hex is not None:
            try:
                return {"result": sha256_hex(text)}
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Ошибка SHA256: {e}")
        else:
            import hashlib
            return {"result": hashlib.sha256(text.encode("utf-8")).hexdigest()}

    raise HTTPException(status_code=400, detail=f"Неизвестный хэш-алгоритм: {req.algorithm}")
