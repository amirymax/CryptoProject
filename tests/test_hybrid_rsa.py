from crypto_core.asymmetric import rsa
from crypto_core.hybrid import hybrid_rsa


def test_hybrid_rsa_encrypt_decrypt():
    priv, pub = rsa.generate_keys()

    message = "Секретное сообщение с гибридным шифрованием".encode("utf-8")
    data = hybrid_rsa.hybrid_encrypt(pub, message)
    decrypted = hybrid_rsa.hybrid_decrypt(priv, data)

    assert decrypted == message
