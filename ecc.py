import sys
import random
from typing import List, Tuple, Optional
from math import gcd

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

def mod_inverse(a: int, m: int) -> Optional[int]:
    """Возвращает обратный элемент или None, если он не существует"""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def input_int(prompt: str, low: int = None, high: int = None, is_prime_needed: bool = False) -> int:
    while True:
        try:
            val = int(input(prompt).strip())
            if low is not None and val <= low:
                print(f"  [Ошибка] Число должно быть > {low}. Повторите.")
                continue
            if high is not None and val >= high:
                print(f"  [Ошибка] Число должно быть < {high}. Повторите.")
                continue
            if is_prime_needed and not is_prime(val):
                print("  [Ошибка] Число должно быть простым. Повторите.")
                continue
            return val
        except ValueError:
            print("  [Ошибка] Введите целое число.")

def input_point(prompt: str, p: int, a: int, b: int) -> Tuple[int, int]:
    """Ввод точки с проверкой принадлежности кривой"""
    while True:
        try:
            s = input(prompt).strip().replace('(', '').replace(')', '').replace(',', ' ')
            parts = s.split()
            if len(parts) != 2:
                raise ValueError()
            x = int(parts[0])
            y = int(parts[1])
            if not (0 <= x < p and 0 <= y < p):
                print(f"  [Ошибка] Координаты должны быть в [0, {p-1}].")
                continue
            # Проверка: y^2 ≡ x^3 + ax + b (mod p)
            if (y * y - (x * x * x + a * x + b)) % p != 0:
                print(f"  [Ошибка] Точка ({x}, {y}) не лежит на кривой!")
                continue
            return (x, y)
        except ValueError:
            print("  [Ошибка] Введите точку в формате x y или (x, y).")

def ecc_point_add(P: Optional[Tuple[int, int]], Q: Optional[Tuple[int, int]], a: int, p: int) -> Optional[Tuple[int, int]]:
    """Сложение точек на эллиптической кривой с безопасной обработкой обратных элементов"""
    if P is None or P == (0, 0):
        return Q
    if Q is None or Q == (0, 0):
        return P
    
    x1, y1 = P
    x2, y2 = Q
    
    # Точки противоположны → результат в бесконечности
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    
    if P == Q:
        # Удвоение точки
        if y1 == 0:
            return None
        denom = (2 * y1) % p
        inv = mod_inverse(denom, p)
        if inv is None:
            return None  # Не удалось вычислить обратный
        lam = (3 * x1 * x1 + a) * inv % p
    else:
        denom = (x2 - x1) % p
        inv = mod_inverse(denom, p)
        if inv is None:
            return None
        lam = (y2 - y1) * inv % p
    
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ecc_scalar_mult(k: int, P: Optional[Tuple[int, int]], a: int, p: int) -> Optional[Tuple[int, int]]:
    """Умножение точки на скаляр с обработкой бесконечной точки"""
    result = None  # Бесконечная точка
    Q = P
    while k:
        if k & 1:
            result = ecc_point_add(result, Q, a, p)
        Q = ecc_point_add(Q, Q, a, p)
        k >>= 1
    return result

def ecc_encrypt(plain_numbers: List[int], a: int, p: int, G: Tuple[int, int], Cb: int, q: int) -> List[int]:
    """Шифрование с гарантией, что P[0] имеет обратный элемент"""
    cipher = []
    pub_key = ecc_scalar_mult(Cb, G, a, p)  # Открытый ключ: Cb * G
    
    for m in plain_numbers:
        # Подбираем k так, чтобы P[0] != 0 и имел обратный
        while True:
            k = random.randint(1, q-1)
            R = ecc_scalar_mult(k, G, a, p)
            if R is None or R == (0, 0):
                continue
            P = ecc_scalar_mult(k, pub_key, a, p)
            if P is None or P == (0, 0):
                continue
            if P[0] != 0 and mod_inverse(P[0], p) is not None:
                break
        
        e = (m * P[0]) % p
        cipher.extend([R[0], R[1], e])
    
    return cipher

def ecc_decrypt(cipher_triples: List[int], a: int, p: int, Cb: int) -> List[int]:
    """Расшифрование с проверкой существования обратного элемента"""
    plain = []
    for i in range(0, len(cipher_triples), 3):
        R = (cipher_triples[i], cipher_triples[i+1])
        e = cipher_triples[i+2]
        
        Q = ecc_scalar_mult(Cb, R, a, p)
        if Q is None or Q == (0, 0):
            raise ValueError("Точка Q бесконечна — проверьте параметры кривой и ключ")
        
        x_inv = mod_inverse(Q[0], p)
        if x_inv is None:
            raise ValueError(f"Обратный элемент для x={Q[0]} не существует по модулю {p}")
        
        m = (e * x_inv) % p
        plain.append(m)
    
    return plain

def ecc_demo():
    """Демонстрация работы на тестовых параметрах"""
    print("\n" + "-" * 40)
    print("ДЕМОНСТРАЦИЯ ДЛЯ ВАРИАНТА 23")
    print("-" * 40)
    a, b, p = 3, -7, 11
    b_mod = b % p
    G = (0, 9)
    Cb, k = 6, 5
    m = 10
    
    print(f"Параметры: a={a}, b={b} (mod {p} → {b_mod}), p={p}, G={G}")
    print(f"Секретный ключ Cb={Cb}, случайное k={k}, сообщение m={m}")
    
    # Шифрование
    R = ecc_scalar_mult(k, G, a, p)
    pub_key = ecc_scalar_mult(Cb, G, a, p)
    P = ecc_scalar_mult(k, pub_key, a, p)
    e = (m * P[0]) % p if P and P[0] != 0 else None
    
    print(f"R = {R}, P = {P}, e = {e}")
    
    # Расшифрование
    if P and P[0] != 0:
        Q = ecc_scalar_mult(Cb, R, a, p)
        x_inv = mod_inverse(Q[0], p)
        m_dec = (e * x_inv) % p if x_inv else None
        print(f"Расшифрованное m = {m_dec} (ожидалось {m})")

def main():
    print("=" * 60)
    print("АСИММЕТРИЧНЫЙ ШИФР ECC (ЭЛЛИПТИЧЕСКИЕ КРИВЫЕ)")
    print("Алфавит: 32 русские буквы (ё заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)

    ecc_demo()

    while True:
        print("\n" + "-" * 40)
        print("МЕНЮ:")
        print("  1. Шифрование")
        print("  2. Расшифрование")
        print("  0. Выход")
        print("-" * 40)

        try:
            op = int(input("Выберите действие: "))
        except ValueError:
            print("  [Ошибка] Введите число.")
            continue

        if op == 0:
            print("\nПрограмма завершена.")
            print("=" * 60)
            break

        if op == 1:
            print("\n" + "-" * 40)
            print("ШИФРОВАНИЕ ECC")
            print("-" * 40)
            raw_text = input("Введите текст для шифрования: ").strip()
            prepared = prepare_text(raw_text)
            if not prepared:
                print("  [Ошибка] Текст пуст после предобработки.")
                continue
            
            a = input_int("Введите a: ")
            b = input_int("Введите b (может быть отрицательным): ")
            p = input_int("Введите p (простое): ", low=2, is_prime_needed=True)
            b_mod = b % p
            
            G = input_point(f"Введите базовую точку G (x y) на кривой y² = x³ + {a}x + {b_mod} mod {p}: ", p, a, b_mod)
            Cb = input_int("Введите секретный ключ Cb (0 < Cb < p): ", low=0, high=p)
            q = input_int("Введите порядок базовой точки q: ", low=1)
            
            plain_numbers = digitization(prepared)
            try:
                cipher = ecc_encrypt(plain_numbers, a, p, G, Cb, q)
                print(f"\n[Инфо] Секретный ключ Cb = {Cb} (сохраните для расшифровки)")
                print("\nЗАШИФРОВАННЫЙ ТЕКСТ (тройки Rx Ry e):")
                print(' '.join(str(c) for c in cipher))
                print("-" * 40)
            except Exception as ex:
                print(f"\n[Ошибка] Шифрование не удалось: {ex}")

        elif op == 2:
            print("\n" + "-" * 40)
            print("РАСШИФРОВАНИЕ ECC")
            print("-" * 40)
            raw_text = input("Введите зашифрованный текст (тройки Rx Ry e через пробел): ").strip()
            a = input_int("Введите a: ")
            p = input_int("Введите p: ", low=2)
            Cb = input_int("Введите секретный ключ Cb: ")
            
            try:
                cipher_numbers = [int(x) for x in raw_text.split()]
                if len(cipher_numbers) % 3 != 0:
                    raise ValueError("Количество чисел должно быть кратно 3")
                
                plain_numbers = ecc_decrypt(cipher_numbers, a, p, Cb)
                plain_letters = undigitization(plain_numbers)
                restored = decryption_format(plain_letters)
                print(f"\nРАСШИФРОВАННЫЙ ТЕКСТ: {restored}")
                print("-" * 40)
            except Exception as ex:
                print(f"\n[Ошибка] Расшифрование не удалось: {ex}")

        else:
            print("  [Ошибка] Неверный выбор.")

if __name__ == "__main__":
    main()