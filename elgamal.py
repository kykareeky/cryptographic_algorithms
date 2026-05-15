import sys
import random
from math import gcd
from typing import List, Tuple

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
ALPH_SIZE = len(ALPHABET)
punct_dict = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
    "'": 'апстр'
}
rev_punct = {v: k for k, v in punct_dict.items()}
space_repl = 'прб'

def prepare_text(txt: str) -> str:
    txt = txt.lower()
    txt = txt.replace('ё', 'е')
    for p, r in punct_dict.items():
        txt = txt.replace(p, r)
    txt = txt.replace(' ', space_repl)
    return txt

def restore_text(txt: str) -> str:
    txt = txt.replace(space_repl, ' ')
    for w, p in rev_punct.items():
        txt = txt.replace(w, p)
    return txt

def digitization(open_text: str) -> List[int]:
    # [КРИПТО] Преобразование букв в числа от 1 до 32 для математических операций
    return [ALPHABET.index(ch) + 1 for ch in open_text]

def undigitization(numbers: List[int]) -> str:
    # [КРИПТО] Обратное преобразование чисел в буквы
    return ''.join(ALPHABET[n-1] for n in numbers)

def decryption_format(dec_text: str) -> str:
    dec_text = dec_text.replace('тчк', '.').replace('зпт', ',').replace(space_repl, ' ')
    if not dec_text:
        return ""
    result = dec_text[0].upper() + dec_text[1:]
    result_list = list(result)
    for i in range(len(result_list) - 2):
        if result_list[i] == ".":
            result_list[i+2] = result_list[i+2].upper()
    return ''.join(result_list)

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def mod_inverse(a: int, m: int) -> int:
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Обратный элемент не существует")
    return x % m

def input_int(prompt: str, low: int = None, high: int = None, is_prime_needed: bool = False) -> int:
    while True:
        try:
            val = int(input(prompt).strip())
            if low is not None and val <= low:
                print(f"  [!] Число должно быть > {low}. Повторите.")
                continue
            if high is not None and val >= high:
                print(f"  [!] Число должно быть < {high}. Повторите.")
                continue
            if is_prime_needed and not is_prime(val):
                print("  [!] Число должно быть простым. Повторите.")
                continue
            return val
        except ValueError:
            print("  [!] Введите целое число.")

def input_positive(prompt: str) -> int:
    while True:
        try:
            val = int(input(prompt).strip())
            if val > 0:
                return val
            print("  [!] Введите положительное число.")
        except ValueError:
            print("  [!] Введите целое число.")

def elgamal_encrypt(plain_numbers: List[int], p: int, g: int, y: int) -> List[int]:
    result = []
    # [КРИПТО] Цикл шифрования каждого числа сообщения. Для каждого блока выбирается своё случайное k.
    for m in plain_numbers:
        # [КРИПТО] Подбор случайного k, взаимно простого с p-1, чтобы гарантировать безопасность вычислений
        k = random.randint(2, p-2)
        while gcd(k, p-1) != 1:
            k = random.randint(2, p-2)
        # [КРИПТО] Первая часть шифртекста: a = g^k mod p (зависит только от k)
        a = pow(g, k, p)
        # [КРИПТО] Вторая часть: b = m * y^k mod p (связывает сообщение, открытый ключ и k)
        b = (m * pow(y, k, p)) % p
        result.append(a)
        result.append(b)
    return result

def elgamal_decrypt(cipher_pairs: List[int], p: int, x: int) -> List[int]:
    plain = []
    # [КРИПТО] Цикл обработки шифртекста парами (a, b)
    for i in range(0, len(cipher_pairs), 2):
        a = cipher_pairs[i]
        b = cipher_pairs[i+1]
        # [КРИПТО] Вычисление обратного элемента a^(-x) mod p для извлечения сообщения
        a_inv = pow(a, p-1-x, p)
        # [КРИПТО] Восстановление исходного числа: m = b * a^(-x) mod p
        m = (b * a_inv) % p
        plain.append(m)
    return plain

def main():
    print("=" * 60)
    print("АСИММЕТРИЧНЫЙ ШИФР ELGAMAL")
    print("Алфавит: 32 русские буквы (ё заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)
    while True:
        print("\n " + "─" * 40)
        print("МЕНЮ: ")
        print("  1. Шифрование ")
        print("  2. Расшифрование ")
        print("  0. Выход ")
        print("─" * 40)

        try:
            op = int(input("Выберите действие: "))
        except ValueError:
            print("  [!] Введите число. ")
            continue

        if op == 0:
            print("\nДо свидания! ")
            print("=" * 60)
            break

        raw_text = input("Введите текст: ").strip()
        if op == 1:
            prepared = prepare_text(raw_text)
        else:
            prepared = raw_text

        try:
            if op == 1:
                print("\n " + "-" * 40)
                print("ШИФРОВАНИЕ ELGAMAL ")
                print("-" * 40)
                p = input_int("Введите простое число p (должно быть > 32): ", low=32, is_prime_needed=True)
                g = input_int(f"Введите g (1 < g < {p}): ", low=1, high=p)
                x = input_int(f"Введите секретный ключ x (1 < x < {p-1}): ", low=1, high=p-1)
                y = pow(g, x, p)
                plain_numbers = digitization(prepared)
                cipher = elgamal_encrypt(plain_numbers, p, g, y)
                print(f"\nОткрытые параметры: p = {p}, g = {g}, y = {y}")
                print(f"Секретный ключ (x) = {x} (запомните для расшифровки) ")
                print("\nЗАШИФРОВАННЫЙ ТЕКСТ (пары a,b): ")
                print(' '.join(str(c) for c in cipher))
                print("-" * 40)

            else:
                print("\n " + "-" * 40)
                print("РАСШИФРОВАНИЕ ELGAMAL ")
                print("-" * 40)
                p = input_positive("Введите p: ")
                if not is_prime(p):
                    print("  [!] Предупреждение: p не является простым. Расшифровка может быть некорректной. ")
                x = input_positive("Введите секретный ключ x: ")
                if not (1 < x < p):
                    raise ValueError("x должно быть в интервале (1, p) ")
                cipher_numbers = [int(c) for c in prepared.split()]
                if len(cipher_numbers) % 2 != 0:
                    raise ValueError("Количество чисел должно быть чётным (пары a,b) ")
                for val in cipher_numbers:
                    if not (0 <= val < p):
                        raise ValueError(f"Число {val} выходит за пределы [0, {p-1}] ")
                plain_numbers = elgamal_decrypt(cipher_numbers, p, x)
                plain_letters = undigitization(plain_numbers)
                restored = decryption_format(plain_letters)
                print(f"\nРАСШИФРОВАННЫЙ ТЕКСТ: {restored}")
                print("-" * 40)

        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()