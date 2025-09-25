import itertools


RUS_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщьыъэюя"
RUS_ALPHABET_NOYO = RUS_ALPHABET.replace("ё", "")


# -------------------------
# Шифр замены
# -------------------------
def substitution_encrypt(text: str, key_alphabet: str, alphabet: str = RUS_ALPHABET_NOYO) -> str:
    """
    Шифр замены: каждая буква алфавита заменяется на букву из key_alphabet.
    key_alphabet должен быть перестановкой alphabet.
    """
    table = str.maketrans(alphabet, key_alphabet)
    return text.translate(table)


def substitution_decrypt(ciphertext: str, key_alphabet: str, alphabet: str = RUS_ALPHABET_NOYO) -> str:
    table = str.maketrans(key_alphabet, alphabet)
    return ciphertext.translate(table)


# -------------------------
# Шифр перестановки (по блокам)
# -------------------------
def transposition_encrypt(text: str, key: list[int]) -> str:
    """
    Шифр перестановки.
    key — список индексов, например [2,0,1] означает:
      символ0 → позиция2, символ1 → позиция0, символ2 → позиция1
    """
    n = len(key)
    # дополним пробелами, чтобы текст делился на блоки
    if len(text) % n != 0:
        text += " " * (n - len(text) % n)

    blocks = [text[i:i+n] for i in range(0, len(text), n)]
    encrypted_blocks = []
    for block in blocks:
        encrypted_blocks.append("".join(block[i] for i in key))
    return "".join(encrypted_blocks)


def transposition_decrypt(ciphertext: str, key: list[int]) -> str:
    n = len(key)
    inv_key = [0] * n
    for i, pos in enumerate(key):
        inv_key[pos] = i

    blocks = [ciphertext[i:i+n] for i in range(0, len(ciphertext), n)]
    decrypted_blocks = []
    for block in blocks:
        decrypted_blocks.append("".join(block[i] for i in inv_key))
    return "".join(decrypted_blocks).rstrip()


# -------------------------
# Шифр гаммирования (XOR)
# -------------------------
def gamma_encrypt(text: str, gamma: str, alphabet: str = RUS_ALPHABET_NOYO) -> str:
    """
    Шифр гаммирования (по сути Vigenere-like).
    gamma — строка-ключ.
    """
    res = []
    m = len(alphabet)
    for i, ch in enumerate(text):
        if ch.lower() not in alphabet:
            res.append(ch)
            continue
        x = alphabet.index(ch.lower())
        g = alphabet.index(gamma[i % len(gamma)].lower())
        c = (x + g) % m
        res.append(alphabet[c])
    return "".join(res)


def gamma_decrypt(ciphertext: str, gamma: str, alphabet: str = RUS_ALPHABET_NOYO) -> str:
    res = []
    m = len(alphabet)
    for i, ch in enumerate(ciphertext):
        if ch.lower() not in alphabet:
            res.append(ch)
            continue
        y = alphabet.index(ch.lower())
        g = alphabet.index(gamma[i % len(gamma)].lower())
        p = (y - g) % m
        res.append(alphabet[p])
    return "".join(res)
