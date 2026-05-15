import sys
import random

def preprocess(text: str) -> str:
    """Заменяет пробелы, запятые и точки на маркеры."""
    text = text.replace('.', 'тчк')
    text = text.replace(',', 'зпт')
    text = text.replace(' ', 'прб')
    return text.lower()

def hash_quad(text: str, p: int, verbose: bool = False) -> int:
    # [КРИПТО] Хеширование сообщения: преобразует текст в число по модулю p.
    # На каждом шаге суммирует индекс буквы с текущим хешем и возводит результат в квадрат.
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    h = 0
    if verbose:
        print(f"\n  Формула: h_i = (h_{{i-1}} + индекс(буквы) + 1)² mod {p}")
        print(f"  {'Буква':<6} {'Индекс':<8} {'Вычисление':<38} {'h'}")
        print("   " + "-"*65)
    for ch in text:
        idx = alphabet.index(ch) + 1
        h_prev = h
        h = ((h_prev + idx) ** 2) % p
        if verbose:
            calc = f"({h_prev} + {idx})² % {p} = {(h_prev+idx)**2} % {p}"
            print(f"  '{ch}'    {idx:<8} {calc:<38} {h}")
    result = h if h != 0 else 1
    if verbose and h == 0:
        print("  h = 0 → заменяем на 1")
    return result
#Проверка числа на простоту
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

def mod_inv(a: int, p: int) -> int:
    # [КРИПТО] Находит обратный элемент к a по модулю p с помощью возведения в степень.
    # Используется для безопасного "деления" в модульной арифметике.
    a = a % p
    if a == 0:
        raise ZeroDivisionError("Обратный элемент не существует")
    return pow(a, -1, p)

def compute_a(p: int, q: int) -> int:
    # [КРИПТО] Поиск элемента a, который имеет порядок q по модулю p.
    # Это значит, что a^q ≡ 1 mod p, и ни одна меньшая степень не даёт 1.
    # Гарантирует, что вычисления будут происходить внутри безопасной подгруппы.
    print(f"\n{'='*60}")
    print(f"  ВЫЧИСЛЕНИЕ ПАРАМЕТРА a (ГОСТ Р 34.10-94)")
    print(f"{'='*60}")
    print(f"  Формула: a = d^((p-1)/q) mod p")
    print(f"  Условие: a != 1  и  a^q mod p = 1")
    print(f"  (p-1)/q = ({p}-1)/{q} = {(p-1)//q}\n")
    exp = (p - 1) // q
    candidates = []
    print(f"  {'d':<6} {'a = d^exp mod p':<25} {'a^q mod p':<12} {'Статус'}")
    print(f"  {'-'*60}")
    for d in range(2, p):
        a = pow(d, exp, p)
        check = pow(a, q, p)
        ok = (a != 1) and (check == 1)
        status = "[Успех] подходит" if ok else "[Инфо] не подходит"
        print(f"  {d:<6} {a:<25} {check:<12} {status}")
        if ok:
            candidates.append((d, a))
    if not candidates:
        raise ValueError("Не найдено подходящих значений a!")
    print(f"\n  Найдено {len(candidates)} подходящих значений a.")
    print("  Выберите одно из них (введите номер d или само a):")
    for idx, (d, a_val) in enumerate(candidates, 1):
        print(f"    {idx}. d={d}, a={a_val}")
    while True:
        choice = input("  Ваш выбор:").strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(candidates):
                return candidates[idx-1][1]
        except ValueError:
            pass
        try:
            a_val = int(choice)
            for d, a_candidate in candidates:
                if a_candidate == a_val:
                    return a_val
        except ValueError:
            pass
        print("  [Ошибка] Неверный ввод. Введите номер из списка или значение a.")

def gost94_sign(text: str, p: int, q: int, a: int, x: int) -> tuple:
    # [КРИПТО] Формирование подписи по ГОСТ Р 34.10-94.
    # Генерирует пару чисел (r, s), которая подтверждает подлинность сообщения.
    m = hash_quad(text, q, verbose=False)
    # [КРИПТО] Перебор случайных k до тех пор, пока компоненты подписи r и s не станут ненулевыми.
    candidates = list(range(1, q))
    random.shuffle(candidates)
    for k in candidates:
        r = pow(a, k, p) % q
        s = (x * r + k * m) % q
        if r != 0 and s != 0:
            return (r, s, m)
    raise ValueError("Не удалось найти подходящее k")

def gost94_verify(text: str, r: int, s: int, p: int, q: int, a: int, y: int) -> bool:
    # [КРИПТО] Проверка подписи: восстанавливает значение u по компонентам r, s и открытому ключу y.
    # Если u совпадает с r, подпись считается валидной.
    m = hash_quad(text, q, verbose=False)
    if not (0 < r < q and 0 < s < q):
        return False
    # [КРИПТО] Вычисляем обратный элемент к хешу сообщения по модулю q
    v = pow(m, q - 2, q)
    z1 = (s * v) % q
    z2 = ((q - r) * v) % q
    # [КРИПТО] Комбинируем базовую точку a и открытый ключ y с весами z1 и z2
    u = (pow(a, z1, p) * pow(y, z2, p)) % p % q
    return u == r
#Безопасный ввод целого числа
def get_int_input(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("[Ошибка] Введите целое число.")

def main():
    print("=" * 60)
    print("ГОСТ Р 34.10-94 – ЦИФРОВАЯ ПОДПИСЬ")
    print("=" * 60)
    print("\nНазначение: создание и проверка электронной подписи")
    print("Алфавит: 32 русские буквы (ё → е) + маркеры для пробелов и знаков")
    print("Формула хеша: h_i = (h_{i-1} + idx + 1)² mod p")
    while True:
        print("\n" + "-" * 40)
        print("МЕНЮ")
        print("-" * 40)
        print("1 - Подписать сообщение")
        print("2 - Проверить подпись")
        print("0 - Выход")
        print("-" * 40)

        op = get_int_input("Ваш выбор:")
        if op == 0:
            print("\n[Инфо] Программа завершена")
            print("=" * 60)
            break
        if op not in (1, 2):
            print("[Ошибка] Неверный выбор")
            continue

        text = input("\nВведите текст для обработки:").strip()
        if not text:
            print("[Ошибка] Текст не может быть пустым")
            continue

        text = preprocess(text)
        print(f"[Инфо] Подготовленный текст: {text}")

        if op == 1:
            print("\n" + "-" * 60)
            print("ФОРМИРОВАНИЕ ПОДПИСИ")
            print("-" * 60)

            p = get_int_input("  Введите простое P (> 32):")
            if not is_prime(p) or p <= 32:
                print("[Ошибка] P должно быть простым и > 32")
                continue

            q = get_int_input(f"  Введите простое Q (делитель {p-1}):")
            if not is_prime(q) or (p - 1) % q != 0:
                print(f"[Ошибка] Q должно быть простым делителем {p-1}")
                continue

            try:
                a = compute_a(p, q)
            except Exception as e:
                print(f"[Ошибка] {e}")
                continue

            x = get_int_input(f"  Введите закрытый ключ X (1 < X < {q}):")
            if not (0 < x < q):
                print(f"[Ошибка] X должен быть в диапазоне (0, {q})")
                continue

            y = pow(a, x, p)
            print(f"\n[Инфо] Открытый ключ Y = a^x mod p = {y}")

            try:
                r, s, m = gost94_sign(text, p, q, a, x)
                print("\n" + "=" * 60)
                print("РЕЗУЛЬТАТ ФОРМИРОВАНИЯ ПОДПИСИ")
                print("=" * 60)
                print(f"Хеш сообщения m: {m}")
                print(f"Подпись        : r = {r}, s = {s}")
                print("\n[Важно] Для проверки сохраните: P, Q, a, Y, r, s")
                print("=" * 60)
            except Exception as e:
                print(f"[Ошибка] {e}")

        elif op == 2:
            print("\n" + "-" * 60)
            print("ПРОВЕРКА ПОДПИСИ")
            print("-" * 60)

            p = get_int_input("  Введите P:")
            q = get_int_input("  Введите Q:")
            a = get_int_input("  Введите a:")
            y = get_int_input("  Введите открытый ключ Y:")
            r = get_int_input("  Введите параметр r:")
            s = get_int_input("  Введите параметр s:")

            valid = gost94_verify(text, r, s, p, q, a, y)

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
                print("  • Параметры указаны неверно")
            print("=" * 60)

if __name__ == "__main__":
    main()