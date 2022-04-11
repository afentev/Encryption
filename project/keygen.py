import random
import math
import argparse

from typing import Tuple

length = 8


def eratosthenes(n: int) -> Tuple[int, ...]:
    array = [x for x in range(n + 1)]
    array[1] = False
    i = 2
    while i * i <= len(array):
        if array[i]:
            for index in range(i ** 2, len(array), i):
                if array[index]:
                    array[index] = False
        i += 1
    return tuple(filter(lambda a: a, array))


primes = eratosthenes(2000)


def MillerRabin(n: int, s: int) -> bool:
    for j in range(1, s + 1):
        a = random.randint(1, n - 1)
        b = bin(n - 1)[2:]
        d = 1
        for i in range(len(b) - 1, -1, -1):
            x = d
            d = (d * d) % n
            if d == 1 and x != 1 and x != n - 1:
                return True  # Составное
            if b[i] == '1':
                d = (d * a) % n
                if d != 1:
                    return True  # Составное
                return False  # Простое


def ferma(n: int, a: int) -> bool:
    return pow(a, n - 1, n) == 1


def is_prime(number: int, param: int) -> bool:
    if number % 2 == 0:
        return False
    for prime in primes:
        if number % prime == 0:
            return number == prime
    for i in range(30):
        a = random.randint(0, 2 ** param)
        if not MillerRabin(number, a) or not ferma(number, a):
            return False
    return True


def get_prime(len_bytes: int) -> int:
    lower_bound = 2 ** (len_bytes - 1)
    upper_bound = 2 * lower_bound - 1
    while True:
        number = random.randint(lower_bound, upper_bound)
        if is_prime(number, len_bytes):
            return number


def euclidean_reverse(e: int, m: int) -> int:
    b, c, i, j = m, e, 0, 1
    while c != 0:
        x, y, b = *divmod(b, c), c
        c = y
        y = j
        j = i - j * x
        i = y
    if i < 0:
        i += m
    return i


def get_rsa_keys(len_bytes: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    p = get_prime(len_bytes)
    q = p
    while p == q:
        q = get_prime(len_bytes)

    n = p * q
    f = (p - 1) * (q - 1)
    for attempt in (17, 257, 65537):
        if math.gcd(attempt, f) == 1:
            e = attempt
            break
    d = euclidean_reverse(e, f)
    return (e, n), (d, n)


parser = argparse.ArgumentParser(description="Генерация RSA ключей")
parser.add_argument('-l', '--length', metavar='bytes', type=int,
                    default=16,
                    help='Длина ключа в битах')

parser.add_argument('-s', '--seed', metavar='number', type=int,
                    default=None,
                    help='Seed для ГПСЧ')

if __name__ == "__main__":
    args = parser.parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    public, private = get_rsa_keys(args.length)
    print('Public key:')
    print('Public exponent:   ', str(public[0]))
    print('Modulo:            ', str(public[1]), end='\n\n')
    print('Private exponent:  ', str(private[0]))
    print('Modulo:            ', str(private[1]))
