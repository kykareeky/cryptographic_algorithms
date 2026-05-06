import sys
import random
from math import gcd

# ------------------------------------------------------------
# Константы и словари
# ------------------------------------------------------------
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
ALPH_SIZE = len(ALPHABET)

PUNCT_DICT = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'дефис', '(': 'скоб', ')': 'скобз',
    "'": 'апстр', '—': 'тире', '\n': 'перенос',
    ':': 'двтч', ';': 'тчкзпт', ' ': 'прб'
}
# Добавляем цифры
for i, word in enumerate(['ноль', 'один', 'два', 'три', 'четыре',
                          'пять', 'шесть', 'семь', 'восемь', 'девять']):
    PUNCT_DICT[str(i)] = word

REV_PUNCT = {v: k for k, v in PUNCT_DICT.items()}


def prepare_text(txt: str) -> str:
    """Подготовка текста: нормализация и замена спецсимволов на маркеры"""
    txt = txt.lower().replace('ё', 'е')
    for orig, marker in PUNCT_DICT.items():
        txt = txt.replace(orig, marker)
    return txt


def restore_text(txt: str) -> str:
    """Восстановление исходного текста из маркеров"""
    # Сортируем по длине для корректной замены (длинные маркеры сначала)
    for marker in sorted(REV_PUNCT.keys(), key=len, reverse=True):
        txt = txt.replace(marker, REV_PUNCT[marker])
    return txt


def hash_message(text: str, p: int) -> int:
    """Простая хеш-функция для демонстрации (не для продакшена!)"""
    h = 0
    for ch in text:
        if ch in ALPHABET:
            mi = ALPHABET.index(ch) + 1
            h = (h + mi) % p
            h = (h * h) % p
    return h if h != 0 else 1


def is_prime(n: int) -> bool:
    """Проверка числа на простоту"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def extended_gcd(a: int, b: int):
    """Расширенный алгоритм Евклида"""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, m: int) -> int:
    """Вычисление модульного обратного элемента"""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Обратный элемент не существует")
    return x % m


def input_int(prompt: str, low: int = None, high: int = None, is_prime_needed: bool = False) -> int:
    """Безопасный ввод целого числа с проверками"""
    while True:
        try:
            val = int(input(prompt).strip())
            if low is not None and val <= low:
                print(f"[Ошибка] Число должно быть > {low}")
                continue
            if high is not None and val >= high:
                print(f"[Ошибка] Число должно быть < {high}")
                continue
            if is_prime_needed and not is_prime(val):
                print("[Ошибка] Число должно быть простым")
                continue
            return val
        except ValueError:
            print("[Ошибка] Введите целое число")


def elgamal_sign(message_hash: int, p: int, g: int, x: int) -> tuple:
    """Генерация подписи Эль-Гамаля: (a, b, k)"""
    while True:
        k = random.randint(2, p - 2)
        if gcd(k, p - 1) == 1:
            break
    a = pow(g, k, p)
    k_inv = mod_inverse(k, p - 1)
    b = ((message_hash - x * a) % (p - 1)) * k_inv % (p - 1)
    return a, b, k


def elgamal_verify(message_hash: int, a: int, b: int, p: int, g: int, y: int) -> bool:
    """Проверка подписи Эль-Гамаля"""
    if not (0 < a < p and 0 <= b < p - 1):
        return False
    left = (pow(y, a, p) * pow(a, b, p)) % p
    right = pow(g, message_hash, p)
    return left == right


def demo_signature():
    """Демонстрация работы схемы подписи"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЦИФРОВОЙ ПОДПИСИ")
    print("=" * 60)
    
    # Тестовые параметры
    p_demo, g_demo, x_demo = 47, 11, 5
    y_demo = pow(g_demo, x_demo, p_demo)
    text_demo = "приветмир"
    
    print(f"\nПараметры схемы:")
    print(f"  Простой модуль p = {p_demo}")
    print(f"  Генератор g = {g_demo}")
    print(f"  Секретный ключ x = {x_demo}")
    print(f"  Открытый ключ y = g^x mod p = {y_demo}")
    
    print(f"\nИсходное сообщение: \"{text_demo}\"")
    prepared = prepare_text(text_demo)
    h = hash_message(prepared, p_demo)
    print(f"Подготовленное сообщение: {prepared}")
    print(f"Хеш сообщения h = {h}")
    
    a, b, k = elgamal_sign(h, p_demo, g_demo, x_demo)
    print(f"\nГенерация подписи:")
    print(f"  Случайное k = {k}")
    print(f"  a = g^k mod p = {a}")
    print(f"  b = (h - x·a)·k⁻¹ mod (p-1) = {b}")
    print(f"  Подпись: ({a}, {b})")
    
    valid = elgamal_verify(h, a, b, p_demo, g_demo, y_demo)
    print(f"\nПроверка подписи:")
    print(f"  y^a · a^b mod p = {((pow(y_demo, a, p_demo) * pow(a, b, p_demo)) % p_demo)}")
    print(f"  g^h mod p = {pow(g_demo, h, p_demo)}")
    print(f"  Результат: {'[Успех] Подпись верна' if valid else '[Ошибка] Подпись неверна'}")
    print("=" * 60)


def sign_message():
    """Режим подписания сообщения"""
    print("\n" + "-" * 60)
    print("ПОДПИСАНИЕ СООБЩЕНИЯ")
    print("-" * 60)
    
    # Ввод сообщения
    print("\nВыберите источник сообщения:")
    print("1 - Ввод в консоли")
    print("2 - Чтение из файла (input.txt)")
    choice = input("Ваш выбор: ").strip()
    
    if choice == '1':
        text = input("\nВведите сообщение: ").strip()
    elif choice == '2':
        try:
            with open('input.txt', 'r', encoding='utf-8') as f:
                text = f.read().strip()
        except FileNotFoundError:
            print("[Ошибка] Файл input.txt не найден")
            return
    else:
        print("[Ошибка] Неверный выбор")
        return
    
    if not text:
        print("[Ошибка] Сообщение не может быть пустым")
        return
    
    # Подготовка и хеширование
    prepared = prepare_text(text)
    print(f"\n[Инфо] Сообщение подготовлено: {prepared[:50]}{'...' if len(prepared) > 50 else ''}")
    
    # Ввод параметров схемы
    print("\nВведите параметры схемы Эль-Гамаля:")
    p = input_int("  Простой модуль p (> 32): ", low=32, is_prime_needed=True)
    
    h = hash_message(prepared, p)
    print(f"[Инфо] Хеш сообщения h = {h}")
    
    g = input_int(f"  Генератор g (1 < g < {p}): ", low=1, high=p)
    x = input_int(f"  Секретный ключ x (1 < x < {p-1}): ", low=1, high=p-1)
    
    # Вычисление открытого ключа
    y = pow(g, x, p)
    print(f"\n[Инфо] Открытый ключ y = g^x mod p = {y}")
    
    # Генерация подписи
    print("\n[Инфо] Генерация подписи...")
    a, b, k = elgamal_sign(h, p, g, x)
    
    # Вывод результата
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ПОДПИСАНИЯ")
    print("=" * 60)
    print(f"Исходное сообщение: {text}")
    print(f"\nПараметры схемы:")
    print(f"  p = {p}")
    print(f"  g = {g}")
    print(f"  Открытый ключ y = {y}")
    print(f"\nПодпись Эль-Гамаля:")
    print(f"  a = {a}")
    print(f"  b = {b}")
    print(f"\n[Важно] Сохраните параметры и подпись для проверки!")
    print(f"[Важно] Секретный ключ x = {x} НЕ передавайте никому!")
    print("=" * 60)
    
    # Опционально: сохранение в файл
    save = input("\nСохранить результат в файл? (д/н): ").strip().lower()
    if save in ['д', 'y', 'yes']:
        try:
            with open('signature.txt', 'w', encoding='utf-8') as f:
                f.write("ЦИФРОВАЯ ПОДПИСЬ ELGAMAL\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Сообщение: {text}\n")
                f.write(f"Параметры: p={p}, g={g}, y={y}\n")
                f.write(f"Подпись: a={a}, b={b}\n")
                f.write(f"Хеш: h={h}\n")
            print("[Инфо] Результат сохранён в signature.txt")
        except Exception as e:
            print(f"[Ошибка] Не удалось сохранить файл: {e}")


def verify_signature():
    """Режим проверки подписи"""
    print("\n" + "-" * 60)
    print("ПРОВЕРКА ПОДПИСИ")
    print("-" * 60)
    
    # Ввод сообщения
    print("\nВведите исходное сообщение для проверки:")
    text = input("Сообщение: ").strip()
    if not text:
        print("[Ошибка] Сообщение не может быть пустым")
        return
    
    # Ввод параметров
    print("\nВведите параметры схемы:")
    p = input_int("  Простой модуль p: ", is_prime_needed=True)
    g = input_int(f"  Генератор g (1 < g < {p}): ", low=1, high=p)
    y = input_int(f"  Открытый ключ y (1 < y < {p}): ", low=1, high=p)
    
    # Ввод подписи
    print("\nВведите компоненты подписи:")
    a = input_int("  a = ")
    b = input_int("  b = ")
    
    # Вычисление хеша и проверка
    prepared = prepare_text(text)
    h = hash_message(prepared, p)
    print(f"\n[Инфо] Вычисленный хеш сообщения: h = {h}")
    
    print("\n[Инфо] Проверка подписи...")
    valid = elgamal_verify(h, a, b, p, g, y)
    
    # Вывод результата
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ПРОВЕРКИ")
    print("=" * 60)
    if valid:
        print("[Успех] Подпись ВЕРНА")
        print("  • Сообщение не было изменено")
        print("  • Подпись создана владельцем секретного ключа")
    else:
        print("[Ошибка] Подпись НЕВЕРНА")
        print("  • Сообщение могло быть изменено, ИЛИ")
        print("  • Подпись создана не тем ключом, ИЛИ")
        print("  • Параметры схемы указаны неверно")
    print("=" * 60)


def main():
    """Главная функция программы"""
    print("=" * 60)
    print("ЦИФРОВАЯ ПОДПИСЬ ELGAMAL")
    print("=" * 60)
    print("\nНазначение: аутентификация и обеспечение целостности сообщений")
    print("Алфавит: 32 русские буквы (ё → е) + маркеры для спецсимволов")
    print("\nПринцип работы:")
    print("  • Подпись: (a, b), где a = g^k mod p, b = (h - x·a)·k⁻¹ mod (p-1)")
    print("  • Проверка: y^a · a^b ≡ g^h (mod p)")
    print("  • Сообщение передаётся открыто, подпись удостоверяет его подлинность")
    
    # Демонстрация при первом запуске
    demo = input("\nПоказать демонстрацию работы? (д/н): ").strip().lower()
    if demo in ['д', 'y', 'yes', '']:
        demo_signature()
    
    # Главный цикл
    while True:
        print("\n" + "-" * 40)
        print("МЕНЮ")
        print("-" * 40)
        print("1 - Подписать сообщение")
        print("2 - Проверить подпись")
        print("0 - Выход")
        print("-" * 40)
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == '0':
            print("\n[Инфо] Программа завершена")
            print("=" * 60)
            break
        elif choice == '1':
            sign_message()
        elif choice == '2':
            verify_signature()
        else:
            print("[Ошибка] Неверный выбор, попробуйте снова")


if __name__ == "__main__":
    main()