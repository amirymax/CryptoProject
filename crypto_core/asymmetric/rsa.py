from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# ---------------------------
# Генерация ключей
# ---------------------------
def generate_keys(key_size: int = 2048):
    """Генерация пары RSA-ключей"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# ---------------------------
# Сериализация ключей
# ---------------------------
def save_private_key(private_key, filepath: str, password: str | None = None):
    """Сохранение приватного ключа в PEM"""
    enc_alg = (serialization.BestAvailableEncryption(password.encode())
               if password else serialization.NoEncryption())
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc_alg
    )
    with open(filepath, "wb") as f:
        f.write(pem)

def save_public_key(public_key, filepath: str):
    """Сохранение публичного ключа в PEM"""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filepath, "wb") as f:
        f.write(pem)

def load_private_key(filepath: str, password: str | None = None):
    with open(filepath, "rb") as f:
        data = f.read()
    return serialization.load_pem_private_key(
        data, password=password.encode() if password else None,
        backend=default_backend()
    )

def load_public_key(filepath: str):
    with open(filepath, "rb") as f:
        data = f.read()
    return serialization.load_pem_public_key(data, backend=default_backend())

# ---------------------------
# Шифрование / дешифрование
# ---------------------------
def encrypt_message(public_key, message: str) -> bytes:
    """Шифрование строки"""
    return public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_message(private_key, ciphertext: bytes) -> str:
    """Дешифрование строки"""
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()

# ---------------------------
# Подпись / проверка подписи
# ---------------------------
def sign_message(private_key, message: str) -> bytes:
    return private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verify_signature(public_key, message: str, signature: bytes) -> bool:
    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
