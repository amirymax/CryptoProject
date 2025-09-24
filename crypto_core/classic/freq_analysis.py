from collections import Counter
import matplotlib.pyplot as plt

# Алфавит (русский без "ё")
ALPHABET = [c for c in "абвгдежзийклмнопрстуфхцчшщъыьэюя"]

def letter_frequencies(text: str) -> dict[str, float]:
    """Подсчёт частот букв в тексте"""
    text = text.lower()
    filtered = [c for c in text if c in ALPHABET]
    total = len(filtered)
    counter = Counter(filtered)
    return {char: count / total for char, count in counter.items()} if total > 0 else {}

def plot_frequencies(freqs: dict[str, float], title: str = "Частотный анализ"):
    """Рисует гистограмму частот"""
    letters = list(freqs.keys())
    values = [freqs[ch] for ch in letters]

    plt.figure(figsize=(10, 4))
    plt.bar(letters, values, color="skyblue")
    plt.title(title)
    plt.xlabel("Буквы")
    plt.ylabel("Частота")
    plt.show()
