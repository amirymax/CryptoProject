import pytest
from crypto_core.asymmetric import rsa


def test_rsa_encrypt_decrypt():
    private_key, public_key = rsa.generate_keys()
    message = "Привет, мир!"
    ciphertext = rsa.encrypt_message(public_key, message)
    decrypted = rsa.decrypt_message(private_key, ciphertext)
    assert decrypted == message


def test_rsa_sign_verify():
    private_key, public_key = rsa.generate_keys()
    message = "Тест подписи"
    signature = rsa.sign_message(private_key, message)
    assert rsa.verify_signature(public_key, message, signature)
    # проверка на подмену сообщения
    assert not rsa.verify_signature(public_key, "другое сообщение", signature)
