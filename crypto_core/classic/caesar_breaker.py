from crypto_core.classic import caesar
from crypto_core.classic import freq_analysis

# Средние частоты букв русского языка (приблизительно, без "ё")
RU_FREQS = {
    "о": 0.1097, "е": 0.0845, "а": 0.0801, "и": 0.0735, "н": 0.0670,
    "т": 0.0626, "с": 0.0547, "р": 0.0473, "в": 0.0454, "л": 0.0440,
    "к": 0.0349, "м": 0.0321, "д": 0.0298, "п": 0.0281, "у": 0.0262,
    "я": 0.0201, "ы": 0.0190, "ь": 0.0174, "г": 0.0170, "з": 0.0165,
    "б": 0.0145, "ч": 0.0127, "й": 0.0104, "х": 0.0097, "ж": 0.0094,
    "ш": 0.0073, "ю": 0.0064, "ц": 0.0048, "щ": 0.0036, "э": 0.0032,
    "ф": 0.0026, "ъ": 0.0004
}


def score_frequencies(freqs: dict[str, float]) -> float:
    """Сравнение распределения частот текста и русского языка"""
    score = 0.0
    for ch, expected in RU_FREQS.items():
        score += abs(freqs.get(ch, 0) - expected)
    return score


def break_caesar(ciphertext: str) -> tuple[int, str]:
    """
    Взлом Цезаря:
    - пробуем все ключи
    - считаем "близость" к частотам русского языка
    - возвращаем лучший вариант
    """
    best_key = 0
    best_text = ciphertext
    best_score = float("inf")

    for key in range(len(caesar.ALPHABET)):
        decrypted = caesar.decrypt(ciphertext, key)
        freqs = freq_analysis.letter_frequencies(decrypted)
        s = score_frequencies(freqs)
        if s < best_score:
            best_score = s
            best_key = key
            best_text = decrypted

    return best_key, best_text
