from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib

router = APIRouter(prefix="/crypto", tags=["crypto"])


class CryptoRequest(BaseModel):
    algorithm: str
    text: str


def caesar_encrypt(text: str, shift: int = 3) -> str:
    result = []
    for ch in text:
        if "А" <= ch <= "Я":
            result.append(chr((ord(ch) - ord("А") + shift) % 32 + ord("А")))
        elif "а" <= ch <= "я":
            result.append(chr((ord(ch) - ord("а") + shift) % 32 + ord("а")))
        else:
            result.append(ch)
    return "".join(result)


def caesar_decrypt(text: str, shift: int = 3) -> str:
    return caesar_encrypt(text, -shift)


@router.post("/encrypt")
def encrypt(req: CryptoRequest):
    algo = req.algorithm.lower()
    text = req.text

    if algo == "цезарь":
        return {"result": caesar_encrypt(text)}
    elif algo == "rsa":
        return {"result": "🔒 RSA encryption (not implemented)"}
    elif algo == "эль-гамаль":
        return {"result": "🔒 ElGamal encryption (not implemented)"}
    elif algo == "sha256":
        return {"result": hashlib.sha256(text.encode()).hexdigest()}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {req.algorithm}")


@router.post("/decrypt")
def decrypt(req: CryptoRequest):
    algo = req.algorithm.lower()
    text = req.text

    if algo == "цезарь":
        return {"result": caesar_decrypt(text)}
    elif algo == "rsa":
        return {"result": "🔓 RSA decryption (not implemented)"}
    elif algo == "эль-гамаль":
        return {"result": "🔓 ElGamal decryption (not implemented)"}
    elif algo == "sha256":
        return {"result": "⚠️ Хэш нельзя расшифровать"}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {req.algorithm}")


@router.post("/hash")
def hashing(req: CryptoRequest):
    algo = req.algorithm.lower()
    text = req.text

    if algo == "sha256":
        return {"result": hashlib.sha256(text.encode()).hexdigest()}
    elif algo == "md5":
        return {"result": hashlib.md5(text.encode()).hexdigest()}
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported hash algorithm: {req.algorithm}")
