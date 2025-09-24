import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def aes_encrypt(key: bytes, plaintext: bytes) -> tuple[bytes, bytes, bytes]:
    """Шифрование AES-GCM"""
    iv = os.urandom(12)  # nonce
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
    ).encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return iv, ciphertext, encryptor.tag


def aes_decrypt(key: bytes, iv: bytes, ciphertext: bytes, tag: bytes) -> bytes:
    """Дешифрование AES-GCM"""
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
    ).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def hybrid_encrypt(public_key: rsa.RSAPublicKey, plaintext: bytes) -> dict:
    """
    Гибридное шифрование:
    - данные шифруются AES
    - AES-ключ шифруется RSA
    """
    # Генерация AES-ключа
    aes_key = os.urandom(32)  # AES-256
    iv, ciphertext, tag = aes_encrypt(aes_key, plaintext)

    # Шифруем AES-ключ RSA
    enc_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return {
        "enc_key": enc_key,
        "iv": iv,
        "tag": tag,
        "ciphertext": ciphertext,
    }


def hybrid_decrypt(private_key: rsa.RSAPrivateKey, data: dict) -> bytes:
    """
    Расшифрование:
    - AES-ключ расшифровывается RSA
    - данные расшифровываются AES
    """
    aes_key = private_key.decrypt(
        data["enc_key"],
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return aes_decrypt(aes_key, data["iv"], data["ciphertext"], data["tag"])
