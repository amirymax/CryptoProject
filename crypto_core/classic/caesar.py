# Алфавит (русский без "ё")
ALPHABET = [c for c in "абвгдежзийклмнопрстуфхцчшщъыьэюя"]
ALPH_SET = {c: i for i, c in enumerate(ALPHABET)}
N = len(ALPHABET)


def _norm_text(text: str) -> str:
    """Оставляет только буквы из алфавита и приводит к нижнему регистру"""
    return ''.join(c for c in text.lower() if c in ALPH_SET)


def encrypt(text: str, shift: int) -> str:
    """Шифрование текста (шифр Цезаря)"""
    t = _norm_text(text)
    shift %= N
    return ''.join(ALPHABET[(ALPH_SET[c] + shift) % N] for c in t)


def decrypt(text: str, shift: int) -> str:
    """Дешифрование текста"""
    return encrypt(text, -shift)


def brute_force(cipher: str) -> list[tuple[int, str]]:
    """Подбор всех возможных ключей"""
    t = _norm_text(cipher)
    return [
        (k, ''.join(ALPHABET[(ALPH_SET[c] - k) % N] for c in t))
        for k in range(N)
    ]
