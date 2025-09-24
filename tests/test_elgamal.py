from crypto_core.asymmetric import elgamal


def test_elgamal_encrypt_decrypt():
    # генерим ключи
    priv, pub = elgamal.generate_keys()

    # сообщение как число (ElGamal работает с числами < p)
    message = 12345

    ct = elgamal.encrypt(pub, message)
    pt = elgamal.decrypt(priv, ct)

    assert pt == message
