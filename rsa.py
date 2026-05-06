import sys
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
    return [ALPHABET.index(ch) + 1 for ch in open_text]

def undigitization(numbers: List[int]) -> str:
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

def rsa_encrypt(plain_numbers: List[int], n: int, e: int) -> List[int]:
    return [pow(m, e, n) for m in plain_numbers]

def rsa_decrypt(cipher_numbers: List[int], n: int, d: int) -> List[int]:
    return [pow(c, d, n) for c in cipher_numbers]

def main():
    print("=" * 60)
    print("АСИММЕТРИЧНЫЙ ШИФР RSA")
    print("Алфавит: 32 русские буквы (ё заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)

    while True:
        print("\n" + "─" * 40)
        print("МЕНЮ:")
        print("  1. Шифрование")
        print("  2. Расшифрование")
        print("  0. Выход")
        print("─" * 40)

        try:
            op = int(input("Выберите действие: "))
        except ValueError:
            print("  [!] Введите число.")
            continue

        if op == 0:
            print("\nДо свидания!")
            print("=" * 60)
            break

        raw_text = input("Введите текст: ").strip()
        if op == 1:
            prepared = prepare_text(raw_text)
        else:
            prepared = raw_text

        try:
            if op == 1:
                print("\n" + "-" * 40)
                print("ШИФРОВАНИЕ RSA")
                print("-" * 40)
                p = input_int("Введите простое число P: ", low=1, is_prime_needed=True)
                q = input_int("Введите простое число Q (отличное от P): ", low=1, is_prime_needed=True)
                if p == q:
                    raise ValueError("P и Q должны быть различными")
                n = p * q
                if n < ALPH_SIZE:
                    raise ValueError(f"n = {n} должно быть больше {ALPH_SIZE}")
                phi = (p-1)*(q-1)
                print(f"φ(N) = {phi}")
                e = input_int(f"Введите число E (1 < E < {phi}, взаимно простое с φ): ", low=1, high=phi)
                while True:
                    while gcd(e, phi) != 1:
                        print(f"  [!] E и φ(N) не взаимно просты. Введите другое E.")
                        e = input_int(f"Введите E (1 < E < {phi}, gcd(E,{phi})=1): ", low=1, high=phi)
                    d = mod_inverse(e, phi)
                    if d == e:
                        print("  [!] E и D совпали. Это нежелательно. Введите другое E.")
                        e = input_int(f"Введите E (1 < E < {phi}, gcd(E,{phi})=1): ", low=1, high=phi)
                    else:
                        break
                plain_numbers = digitization(prepared)
                cipher_numbers = rsa_encrypt(plain_numbers, n, e)
                print(f"\nОткрытый ключ: N = {n}, E = {e}")
                print(f"Секретный ключ (d) = {d} (сохраните для расшифровки)")
                print("\nЗАШИФРОВАННЫЙ ТЕКСТ (числа):")
                print(' '.join(str(c) for c in cipher_numbers))
                print("-" * 40)

            else:
                print("\n" + "-" * 40)
                print("РАСШИФРОВАНИЕ RSA")
                print("-" * 40)
                n = input_positive("Введите N: ")
                d = input_positive("Введите секретный ключ d: ")
                cipher_numbers = [int(x) for x in prepared.split()]
                plain_numbers = rsa_decrypt(cipher_numbers, n, d)
                plain_letters = undigitization(plain_numbers)
                restored = decryption_format(plain_letters)
                print(f"\nРАСШИФРОВАННЫЙ ТЕКСТ: {restored}")
                print("-" * 40)

        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()