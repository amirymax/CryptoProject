import random
from typing import Tuple


def modinv(a: int, m: int) -> int:
    """Обратный элемент по модулю m (алгоритм Евклида)"""
    def egcd(x, y):
        if x == 0:
            return y, 0, 1
        g, b, a = egcd(y % x, x)
        return g, a - (y // x) * b, b

    g, x, y = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % m


def generate_keys(p: int = 30803, g: int = 2) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """
    Генерация ключей для ElGamal.
    :param p: большое простое число
    :param g: первообразный корень по модулю p
    :return: (private_key, public_key)
    """
    x = random.randint(2, p - 2)       # секретный ключ
    y = pow(g, x, p)                   # открытый ключ
    private_key = (p, g, x)
    public_key = (p, g, y)
    return private_key, public_key


def encrypt(public_key: Tuple[int, int, int], message: int) -> Tuple[int, int]:
    """Шифрование числа message"""
    p, g, y = public_key
    k = random.randint(2, p - 2)
    a = pow(g, k, p)
    b = (message * pow(y, k, p)) % p
    return a, b


def decrypt(private_key: Tuple[int, int, int], ciphertext: Tuple[int, int]) -> int:
    """Дешифрование"""
    p, g, x = private_key
    a, b = ciphertext
    s = pow(a, x, p)
    m = (b * modinv(s, p)) % p
    return m
