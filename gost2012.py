import random

# [КРИПТО] Алфавит для преобразования текста в числа
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def preprocess(text):
    """Заменяет пробелы, запятые и точки на маркеры."""
    text = text.lower().replace('ё', 'е')
    text = text.replace(' ', 'прб').replace(',', 'зпт').replace('.', 'тчк')
    return text

def compute_hash(text, q):
    # [КРИПТО] Хеширование сообщения: превращает текст в число по модулю q.
    # Суммирует позиции букв, возводит в квадрат на каждом шаге для перемешивания данных.
    h = 0
    for ch in text:
        idx = ALPHABET.find(ch)
        if idx == -1: idx = 0
        h = ((h + idx + 1) ** 2) % q
    return h if h != 0 else 1

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    d = 3
    while d * d <= n:
        if n % d == 0: return False
        d += 2
    return True

def input_int(prompt, min_val=None, max_val=None, is_prime_needed=False):
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val is not None and val <= min_val:
                print(f"[Ошибка] Значение должно быть > {min_val}")
                continue
            if max_val is not None and val >= max_val:
                print(f"[Ошибка] Значение должно быть < {max_val}")
                continue
            if is_prime_needed and not is_prime(val):
                print("[Ошибка] Число должно быть простым")
                continue
            return val
        except ValueError:
            print("[Ошибка] Введите целое число")

def input_point(prompt):
    while True:
        try:
            s = input(prompt).strip().replace('(', '').replace(')', '').replace(',', ' ')
            parts = list(map(int, s.split()))
            if len(parts) != 2:
                print("[Ошибка] Введите ровно две координаты")
                continue
            return (parts[0], parts[1])
        except ValueError:
            print("[Ошибка] Введите целые числа")

def is_on_curve(P, a, b, p):
    if P is None: return True
    x, y = P
    return (y * y) % p == (x * x * x + a * x + b) % p

def point_add(P1, P2, a, p):
    # [КРИПТО] Сложение двух точек на эллиптической кривой.
    # Если точки совпадают или симметричны относительно оси X, используется особая формула.
    # Иначе применяется формула секущей для нахождения третьей точки пересечения с кривой.
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P1 == P2:
        if y1 == 0: return None
        lam = (3 * x1**2 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        
    x3 = (lam**2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def scalar_mult(k, P, a, p):
    # [КРИПТО] Умножение точки на число (скаляр). Использует алгоритм "двой и прибавь".
    # Разбивает число k на биты, последовательно удваивая точку и прибавляя её к результату,
    # если текущий бит равен 1. Позволяет быстро вычислять k*P без k сложений.
    result = None
    Q = P
    while k > 0:
        if k & 1:
            result = point_add(result, Q, a, p)
        Q = point_add(Q, Q, a, p)
        k >>= 1
    return result

def sign_mode():
    print("\n" + "-" * 60)
    print("ФОРМИРОВАНИЕ ПОДПИСИ")
    print("-" * 60)
    msg = input("\nВведите сообщение:").strip()
    if not msg:
        print("[Ошибка] Сообщение не может быть пустым")
        return

    print("\n[Инфо] Введите параметры кривой и ключи:")
    p = input_int("  Простой модуль p:", min_val=2, is_prime_needed=True)
    a = input_int(f"  Параметр a (0 <= a < {p}):", min_val=0, max_val=p)
    b = input_int(f"  Параметр b (0 <= b < {p}):", min_val=0, max_val=p)

    if (4 * a**3 + 27 * b**2) % p == 0:
        print("[Ошибка] Кривая вырождена (4a³ + 27b² ≡ 0 mod p). Введите другие a, b")
        return
        
    G = input_point("  Базовая точка G (x y):")
    if not is_on_curve(G, a, b, p):
        print(f"[Ошибка] Точка {G} не лежит на кривой")
        return
        
    q = input_int(f"  Порядок подгруппы q (простое, 1 < q < p):", min_val=1, max_val=p, is_prime_needed=True)
    if scalar_mult(q, G, a, p) is not None:
        print("[Внимание] q * G != O. Проверьте корректность порядка q.")
        
    d = input_int(f"  Секретный ключ d (1 < d < {q}):", min_val=1, max_val=q-1)

    print("\n[Инфо] Генерация подписи...")
    e = compute_hash(preprocess(msg), q)
    Q = scalar_mult(d, G, a, p)
    print(f"[Инфо] Открытый ключ Q = d * G: {Q}")

    # [КРИПТО] Цикл подбора случайного k, пока не получим валидные компоненты подписи r и s.
    while True:
        k = random.randint(1, q - 1)
        R = scalar_mult(k, G, a, p)
        if R is None: continue
        # [КРИПТО] r = координата X точки R по модулю q
        r = R[0] % q
        if r == 0: continue
        # [КРИПТО] s = (r*d + k*e) mod q. Связывает хеш сообщения, секретный ключ и случайное k.
        s = (r * d + k * e) % q
        if s == 0: continue
        break
        
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ФОРМИРОВАНИЯ ПОДПИСИ")
    print("=" * 60)
    print(f"Сообщение      : {msg}")
    print(f"Открытый ключ Q: {Q}")
    print(f"Подпись        : r = {r}, s = {s}")
    print("\n[Важно] Сохраните следующие параметры для проверки подписи:")
    print(f"  p = {p}")
    print(f"  a = {a}")
    print(f"  b = {b}")
    print(f"  G = {G}")
    print(f"  q = {q}")
    print(f"  Q = {Q}")
    print(f"  r = {r}")
    print(f"  s = {s}")
    print("=" * 60)

def verify_mode():
    print("\n" + "-" * 60)
    print("ПРОВЕРКА ПОДПИСИ")
    print("-" * 60)
    msg = input("\nВведите сообщение:").strip()
    if not msg:
        print("[Ошибка] Сообщение не может быть пустым")
        return
        
    print("\n[Инфо] Введите параметры для проверки:")
    p = input_int("  Простой модуль p:", min_val=2)
    a = input_int(f"  Параметр a (0 <= a < {p}):", min_val=0, max_val=p)
    b = input_int(f"  Параметр b (0 <= b < {p}):", min_val=0, max_val=p)
    G = input_point("  Базовая точка G (x y):")
    q = input_int(f"  Порядок подгруппы q:", min_val=1)
    Q = input_point("  Открытый ключ Q (x y):")
    r = input_int("  Параметр подписи r:")
    s = input_int("  Параметр подписи s:")

    print("\n[Инфо] Проверка подписи...")
    valid = False
    if 0 < r < q and 0 < s < q:
        e = compute_hash(preprocess(msg), q)
        if e != 0:
            # [КРИПТО] Вычисляем обратный элемент хеша v = e^-1 mod q
            v = pow(e, -1, q)
            z1 = s * v % q
            z2 = (-r * v) % q
            # [КРИПТО] Восстанавливаем точку C = z1*G + z2*Q. Если подпись верна, C.x mod q должно совпасть с r.
            C = point_add(scalar_mult(z1, G, a, p), scalar_mult(z2, Q, a, p), a, p)
            if C is not None and C[0] % q == r:
                valid = True
                
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
        print("  • Параметры указаны неверно")
    print("=" * 60)

def main():
    print("=" * 60)
    print("ГОСТ Р 34.10-2012 (ЭЛЛИПТИЧЕСКАЯ КРИПТОГРАФИЯ)")
    print("=" * 60)
    print("\nНазначение: создание и проверка электронной подписи")
    print("Алфавит: 32 русские буквы (ё → е) + маркеры для пробелов и знаков")
    print("Кривая: y² ≡ x³ + ax + b (mod p)")
    while True:
        print("\n" + "-" * 40)
        print("МЕНЮ")
        print("-" * 40)
        print("1 - Подписать сообщение")
        print("2 - Проверить подпись")
        print("0 - Выход")
        print("-" * 40)
        
        choice = input("\nВаш выбор:").strip()
        
        if choice == '0':
            print("\n[Инфо] Программа завершена")
            print("=" * 60)
            break
        elif choice == '1':
            sign_mode()
        elif choice == '2':
            verify_mode()
        else:
            print("[Ошибка] Неверный выбор, попробуйте снова")

if __name__ == "__main__":
    main()