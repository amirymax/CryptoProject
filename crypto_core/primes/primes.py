import random


def is_prime_trial_division(n: int) -> bool:
    """
    Наивная проверка простоты через перебор делителей.
    Подходит только для маленьких чисел.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def is_prime_fermat(n: int, k: int = 5) -> bool:
    """
    Тест Ферма на простоту.
    n — проверяемое число.
    k — количество случайных проверок.
    Возвращает:
      True — вероятно простое,
      False — составное.
    """
    if n < 4:
        return n in (2, 3)
    for _ in range(k):
        a = random.randint(2, n - 2)
        if pow(a, n - 1, n) != 1:
            return False
    return True


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Тест Миллера–Рабина на простоту.
    n — проверяемое число.
    k — количество случайных проверок.
    Возвращает:
      True — вероятно простое,
      False — составное.
    """
    if n < 2:
        return False
    # для маленьких чисел проверим сразу
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p

    # представляем n-1 как 2^s * d
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int = 16) -> int:
    """
    Сгенерировать вероятно простое число заданной битовой длины.
    Использует тест Миллера–Рабина.
    """
    while True:
        n = random.getrandbits(bits)
        n |= 1  # делаем нечётным
        if is_prime_miller_rabin(n, k=10):
            return n
