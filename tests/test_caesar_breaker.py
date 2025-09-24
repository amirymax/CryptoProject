from crypto_core.classic import caesar, caesar_breaker

def test_caesar_breaker_basic():
    plain = "это тестовое сообщение для проверки"
    # используем сдвиг 7 (пример)
    key = 7
    cipher = caesar.encrypt(plain, key)

    found_key, found_text = caesar_breaker.break_caesar(cipher)

    # проверяем, что найденный текст совпадает с исходным (нормализованным)
    # caesar._norm_text удаляет все символы, не входящие в алфавит, и переводит в нижний регистр,
    # поэтому сравниваем с нормализованной версией исходного текста.
    normalized_plain = ''.join(c for c in plain.lower() if c in caesar.ALPH_SET)
    assert found_text == normalized_plain

    # проверяем, что найденный ключ равен использованному (в пределах длины алфавита)
    assert found_key % len(caesar.ALPHABET) == key % len(caesar.ALPHABET)
