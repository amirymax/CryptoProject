from crypto_core.classic import freq_analysis


def test_letter_frequencies_basic():
    text = "абба"
    freqs = freq_analysis.letter_frequencies(text)
    # всего 4 буквы, 'а' встречается 2 раза, 'б' тоже 2 раза
    assert abs(freqs["а"] - 0.5) < 1e-9
    assert abs(freqs["б"] - 0.5) < 1e-9


def test_letter_frequencies_empty():
    freqs = freq_analysis.letter_frequencies("12345")
    assert freqs == {}
