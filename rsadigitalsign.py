import sys
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
    for marker in sorted(REV_PUNCT.keys(), key=len, reverse=True):
        txt = txt.replace(marker, REV_PUNCT[marker])
    return txt


def hash_message(text: str, N: int) -> int:
    """Простая хеш-функция для демонстрации (не криптографически стойкая!)"""
    h = 0
    for ch in text:
        if ch in ALPHABET:
            mi = ALPHABET.index(ch) + 1
            h = (h + mi) % N
            h = (h * h) % N
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


def rsa_sign(message_hash: int, d: int, n: int) -> int:
    """Создание цифровой подписи: S = H^d mod N"""
    return pow(message_hash, d, n)


def rsa_verify(message_hash: int, signature: int, e: int, n: int) -> bool:
    """Проверка подписи: (S^e mod N) == H"""
    return pow(signature, e, n) == message_hash


def demo_signature():
    """Демонстрация работы схемы подписи RSA"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЦИФРОВОЙ ПОДПИСИ RSA")
    print("=" * 60)
    
    # Тестовые параметры (для демонстрации!)
    p_demo, q_demo = 23, 29
    n_demo = p_demo * q_demo
    phi_demo = (p_demo - 1) * (q_demo - 1)
    e_demo = 13
    d_demo = mod_inverse(e_demo, phi_demo)
    
    print(f"\nПараметры схемы:")
    print(f"  Простые числа: p = {p_demo}, q = {q_demo}")
    print(f"  Модуль N = p·q = {n_demo}")
    print(f"  φ(N) = (p-1)(q-1) = {phi_demo}")
    print(f"  Открытая e = {e_demo}")
    print(f"  Закрытая d = {d_demo}")
    
    text_demo = "приветмир"
    print(f"\nИсходное сообщение: \"{text_demo}\"")
    prepared = prepare_text(text_demo)
    h = hash_message(prepared, n_demo)
    print(f"Подготовленное сообщение: {prepared}")
    print(f"Хеш сообщения h = {h}")
    
    signature = rsa_sign(h, d_demo, n_demo)
    print(f"\nГенерация подписи:")
    print(f"  S = h^d mod N = {signature}")
    
    valid = rsa_verify(h, signature, e_demo, n_demo)
    print(f"\nПроверка подписи:")
    print(f"  S^e mod N = {pow(signature, e_demo, n_demo)}")
    print(f"  h = {h}")
    print(f"  Результат: {'[Успех] Подпись верна' if valid else '[Ошибка] Подпись неверна'}")
    print("=" * 60)


def sign_message():
    """Режим подписания сообщения"""
    print("\n" + "-" * 60)
    print("ПОДПИСАНИЕ СООБЩЕНИЯ (RSA)")
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
    
    # Генерация ключей
    print("\nВведите параметры для генерации ключей RSA:")
    p = input_int("  Простое число P: ", low=1, is_prime_needed=True)
    q = input_int("  Простое число Q (Q ≠ P): ", low=1, is_prime_needed=True)
    
    if p == q:
        print("[Ошибка] P и Q должны быть различны")
        return
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Предупреждение о безопасности
    if p < 100 or q < 100:
        print("[Внимание] Малые простые числа! Это небезопасно для реального использования.")
    
    print(f"\n[Инфо] Вычислено: N = {n}, φ(N) = {phi}")
    
    # Выбор открытой экспоненты
    e = input_int(f"  Открытая экспонента E (1 < E < {phi}, gcd(E,φ)=1): ", low=1, high=phi)
    while gcd(e, phi) != 1:
        print(f"[Ошибка] E и φ(N) не взаимно просты (gcd = {gcd(e, phi)})")
        e = input_int(f"  Введите E (1 < E < {phi}, gcd(E,{phi})=1): ", low=1, high=phi)
    
    # Вычисление закрытой экспоненты
    d = mod_inverse(e, phi)
    print(f"[Инфо] Закрытая экспонента d = {d}")
    
    # Хеширование и подпись
    h = hash_message(prepared, n)
    print(f"[Инфо] Хеш сообщения h = {h}")
    
    signature = rsa_sign(h, d, n)
    print(f"[Инфо] Подпись S = h^d mod N = {signature}")
    
    # Вывод результата
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ПОДПИСАНИЯ")
    print("=" * 60)
    print(f"Исходное сообщение: {text}")
    print(f"\nПараметры схемы:")
    print(f"  Модуль N = {n}")
    print(f"  Открытая экспонента e = {e}")
    print(f"  Закрытая экспонента d = {d}")
    print(f"\nПодпись RSA:")
    print(f"  S = {signature}")
    print(f"\n[Важно] Для проверки сохраните: сообщение, N, e и подпись S")
    print(f"[Важно] Закрытый ключ d = {d} НИКОМУ не передавайте!")
    print("=" * 60)
    
    # Опционально: сохранение в файл
    save = input("\nСохранить результат в файл? (д/н): ").strip().lower()
    if save in ['д', 'y', 'yes']:
        try:
            with open('rsa_signature.txt', 'w', encoding='utf-8') as f:
                f.write("ЦИФРОВАЯ ПОДПИСЬ RSA\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Сообщение: {text}\n")
                f.write(f"Параметры: N={n}, e={e}\n")
                f.write(f"Подпись: S={signature}\n")
                f.write(f"Хеш: h={h}\n")
                f.write(f"\n[Секретно] Закрытый ключ: d={d}\n")
            print("[Инфо] Результат сохранён в rsa_signature.txt")
        except Exception as ex:
            print(f"[Ошибка] Не удалось сохранить файл: {ex}")


def verify_signature():
    """Режим проверки подписи"""
    print("\n" + "-" * 60)
    print("ПРОВЕРКА ПОДПИСИ (RSA)")
    print("-" * 60)
    
    # Ввод сообщения
    print("\nВведите исходное сообщение для проверки:")
    text = input("Сообщение: ").strip()
    if not text:
        print("[Ошибка] Сообщение не может быть пустым")
        return
    
    # Ввод параметров
    print("\nВведите параметры схемы:")
    n = input_int("  Модуль N: ", low=1)
    e = input_int("  Открытая экспонента e: ", low=1)
    signature = input_int("  Подпись S: ", low=0)
    
    # Вычисление хеша и проверка
    prepared = prepare_text(text)
    h = hash_message(prepared, n)
    print(f"\n[Инфо] Вычисленный хеш сообщения: h = {h}")
    
    print("\n[Инфо] Проверка подписи...")
    valid = rsa_verify(h, signature, e, n)
    
    # Вывод результата
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ПРОВЕРКИ")
    print("=" * 60)
    if valid:
        print("[Успех] Подпись ВЕРНА")
        print("  • Сообщение не было изменено")
        print("  • Подпись создана владельцем закрытого ключа")
    else:
        print("[Ошибка] Подпись НЕВЕРНА")
        print("  • Сообщение могло быть изменено, ИЛИ")
        print("  • Подпись создана не тем ключом, ИЛИ")
        print("  • Параметры схемы указаны неверно")
    print("=" * 60)


def main():
    """Главная функция программы"""
    print("=" * 60)
    print("ЦИФРОВАЯ ПОДПИСЬ RSA")
    print("=" * 60)
    print("\nНазначение: аутентификация и обеспечение целостности сообщений")
    print("Алфавит: 32 русские буквы (ё → е) + маркеры для спецсимволов")
    print("\nПринцип работы:")
    print("  • Подпись: S = H(message)^d mod N (закрытым ключом)")
    print("  • Проверка: (S^e mod N) == H(message) (открытым ключом)")
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