from crypto_core.classic import caesar


def test_encrypt_decrypt_roundtrip():
    text = "пример текста для проверки"
    for shift in range(1, len(caesar.ALPHABET)):
        encrypted = caesar.encrypt(text, shift)
        decrypted = caesar.decrypt(encrypted, shift)
        normalized_text = ''.join(c for c in text.lower() if c in caesar.ALPH_SET)
        assert decrypted == normalized_text


def test_brute_force_contains_original():
    text = "секрет"
    shift = 5
    cipher = caesar.encrypt(text, shift)
    options = caesar.brute_force(cipher)
    # brute_force должен вернуть список (ключ, текст)
    decrypted_texts = [t for _, t in options]
    normalized_text = ''.join(c for c in text.lower() if c in caesar.ALPH_SET)
    assert normalized_text in decrypted_texts
