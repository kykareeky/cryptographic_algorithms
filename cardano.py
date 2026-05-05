import random

# ============================================================================
# НАСТРОЙКИ АЛФАВИТА И ПУНКТУАЦИИ
# ============================================================================
alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
alphabet = alphabet.replace('Ё', 'Е').replace('ё', 'е')
alphabet = ''.join(sorted(set(alphabet), key=lambda x: alphabet.index(x)))
assert len(alphabet) == 32

# Словарные замены для знаков препинания и пробела
PUNCT_SYMBOLS = ['.', ',', '?', '!', ':', ';', '-', '(', ')', '"', "'", ' ']
PUNCT_WORDS   = ['тчк', 'зпт', 'впр', 'вск', 'двтч', 'тчзпт', 'тире', 'скоб', 'скобз', 'квч', 'апстр', 'прб']


def replace_special_chars(text):
    """Заменяет знаки препинания и пробелы на их словесные эквиваленты"""
    result = text
    for symbol, word in zip(PUNCT_SYMBOLS, PUNCT_WORDS):
        result = result.replace(symbol, word)
    return result


def restore_special_chars(text):
    """Восстанавливает знаки препинания и пробелы из словесных эквивалентов"""
    result = text
    # Сортируем по длине (убывание), чтобы сначала заменять более длинные маркеры
    pairs = sorted(zip(PUNCT_WORDS, PUNCT_SYMBOLS), key=lambda x: len(x[0]), reverse=True)
    for word, symbol in pairs:
        result = result.replace(word, symbol)        # строчные: 'прб' → ' '
        result = result.replace(word.upper(), symbol)  # заглавные: 'ПРБ' → ' '
    return result


def normalize_text(text):
    """Нормализует текст: убирает лишние символы, приводит к верхнему регистру"""
    text = text.upper().replace('Ё', 'Е')
    return ''.join(c for c in text if c in alphabet)


def generate_empty_grid(size):
    """Генерирует пустую сетку размером size x size"""
    return [['' for _ in range(size)] for _ in range(size)]


def rotate_key(key, size):
    """Поворачивает ключ (позиции отверстий) на 90° по часовой стрелке"""
    return [(j, size - 1 - i) for i, j in key]


def insert_chars(grid, key, text_iter):
    """Вставляет символы из итератора в позиции, заданные ключом"""
    for i, j in key:
        grid[i][j] = next(text_iter, random.choice(alphabet))


def extract_chars(grid, key):
    """Извлекает символы из позиций, заданные ключом"""
    return ''.join(grid[i][j] for i, j in key)


def print_matrix_with_indices(matrix):
    """Печатает матрицу с индексами строк и столбцов"""
    print("   ", end="")
    for j in range(len(matrix[0])):
        print(f"{j:3d}", end=" ")
    print()
    
    for i in range(len(matrix)):
        print(f"{i:2d}│", end=" ")
        for j in range(len(matrix[i])):
            if matrix[i][j]:
                print(f" {matrix[i][j]} ", end=" ")
            else:
                print("  ·", end=" ")
        print()
    print()


def print_grid_with_holes(grid, key, title="Решетка"):
    """Печатает сетку с отмеченными отверстиями"""
    print(f"\n{title}:")
    print("   ", end="")
    for j in range(len(grid[0])):
        print(f"{j:3d}", end=" ")
    print()
    
    for i in range(len(grid)):
        print(f"{i:2d}│", end=" ")
        for j in range(len(grid[i])):
            if (i, j) in key:
                if grid[i][j]:
                    print(f" {grid[i][j]} ", end=" ")
                else:
                    print("  ■", end=" ")
            else:
                if grid[i][j]:
                    print(f" {grid[i][j]} ", end=" ")
                else:
                    print("  □", end=" ")
        print()
    print()


def encrypt(text, key, size):
    """Шифрует текст с помощью решетки Кардано"""
    # 1. Замена спецсимволов на слова
    text = replace_special_chars(text)
    # 2. Нормализация: только буквы алфавита в верхнем регистре
    text = normalize_text(text)
    
    total_cells = size * size

    # Добавляем случайные символы, если текст слишком короткий
    padded_len = total_cells - len(text)
    if padded_len > 0:
        text += ''.join(random.choice(alphabet) for _ in range(padded_len))
    
    text = text[:total_cells]  # Обрезаем до нужной длины

    grid = generate_empty_grid(size)
    text_iter = iter(text)
    current_key = key.copy()

    print("\n" + "=" * 80)
    print("ПРОЦЕСС ШИФРОВАНИЯ")
    print("=" * 80)

    # 4 поворота
    for rotation in range(4):
        print(f"\n{'─' * 80}")
        print(f"Поворот {rotation + 1}/4 (угол {rotation * 90}°)")
        print(f"{'─' * 80}")
        
        print(f"\nОтверстия решетки: {current_key}")
        insert_chars(grid, current_key, text_iter)
        print_grid_with_holes(grid, current_key, f"Сетка после поворота {rotation + 1}")
        
        current_key = rotate_key(current_key, size)

    # Читаем зашифрованный текст построчно
    print("\nЧтение зашифрованного текста построчно:")
    print("─" * 80)
    cipher_text = ''.join(''.join(row) for row in grid)
    for i, row in enumerate(grid):
        row_text = ''.join(row)
        print(f"Строка {i}: {row_text}")
    print("─" * 80)
    
    return cipher_text


def decrypt(cipher_text, key, size):
    """Расшифровывает текст с помощью решетки Кардано"""
    grid = generate_empty_grid(size)
    idx = 0
    
    # Заполняем сетку зашифрованным текстом
    for i in range(size):
        for j in range(size):
            if idx < len(cipher_text):
                grid[i][j] = cipher_text[idx]
                idx += 1
    
    print("\n" + "=" * 80)
    print("ПРОЦЕСС РАСШИФРОВАНИЯ")
    print("=" * 80)
    
    print("\nСетка с зашифрованным текстом:")
    print_matrix_with_indices(grid)
    
    result = ''
    current_key = key.copy()
    
    # 4 поворота
    for rotation in range(4):
        print(f"\n{'─' * 80}")
        print(f"Поворот {rotation + 1}/4 (угол {rotation * 90}°)")
        print(f"{'─' * 80}")
        
        print(f"\nОтверстия решетки: {current_key}")
        extracted = extract_chars(grid, current_key)
        print(f"Извлеченные символы: {extracted}")
        result += extracted
        
        print_grid_with_holes(grid, current_key, f"Чтение через отверстия (поворот {rotation + 1})")
        
        current_key = rotate_key(current_key, size)
    
    # Восстанавливаем спецсимволы из словесных маркеров
    result = restore_special_chars(result)
    
    return result


def generate_valid_cardano_key(size):
    """Генерирует валидный ключ для решетки Кардано"""
    total_cells = size * size
    num_holes = total_cells // 4
    
    all_coords = [(i, j) for i in range(size) for j in range(size)]
    used = set()
    key = []
    
    attempts = 0
    max_attempts = 10000
    
    while len(key) < num_holes and attempts < max_attempts:
        attempts += 1
        coord = random.choice(all_coords)
        
        c0 = coord
        c90 = (coord[1], size - 1 - coord[0])
        c180 = (size - 1 - coord[1], coord[0])
        c270 = (size - 1 - coord[0], size - 1 - coord[1])
        
        if not (c0 in used or c90 in used or c180 in used or c270 in used):
            key.append(c0)
            used.update([c0, c90, c180, c270])
    
    if len(key) < num_holes:
        print(f" Не удалось сгенерировать полный ключ. Сгенерировано {len(key)} из {num_holes}")
    
    return key


# ============================================================================
# ГЛАВНАЯ ПРОГРАММА
# ============================================================================
print("=" * 80)
print("ШИФР РЕШЕТКИ КАРДАНО")
print("=" * 80)

print(f"\nАлфавит ({len(alphabet)} букв): {alphabet}")
print("Примечание: буква Ё заменяется на Е")
print(f"Замена знаков: {dict(zip(PUNCT_SYMBOLS, PUNCT_WORDS))}")

# ----------------------------------------------------------------------------
# Ввод размера таблицы
# ----------------------------------------------------------------------------
while True:
    size_input = input("\nВведите размерность таблицы (size x size, четное число ≥ 4): ")
    try:
        size_matrix = int(size_input)
        if size_matrix % 2 != 0:
            print("[Ошибка] Размер должен быть четным!")
            size_matrix += 1
            print(f"  Используется размер: {size_matrix}")
        if size_matrix < 4:
            print("[Ошибка] Минимальный размер - 4")
            continue
        break
    except ValueError:
        print("[Ошибка] Введите целое число!")

# ----------------------------------------------------------------------------
# Генерация ключа
# ----------------------------------------------------------------------------
print(f"\n Генерация случайного ключа для решетки {size_matrix}x{size_matrix}...")
key = generate_valid_cardano_key(size_matrix)
print(f" Ключ сгенерирован! Количество отверстий на один поворот: {len(key)}")
print(f"Позиции отверстий (0-индексация): {key}")

# ============================================================================
# ВИЗУАЛИЗАЦИЯ КЛЮЧА
# ============================================================================
print("\n" + "=" * 80)
print("ВИЗУАЛИЗАЦИЯ КЛЮЧА (все 4 поворота)")
print("=" * 80)

current_key_vis = key.copy()
for rot in range(4):
    empty_grid = generate_empty_grid(size_matrix)
    print(f"\nПоворот {rot + 1} (угол {rot * 90}°):")
    print_grid_with_holes(empty_grid, current_key_vis, f"Отверстия решетки")
    current_key_vis = rotate_key(current_key_vis, size_matrix)

# ============================================================================
# ШИФРОВАНИЕ
# ============================================================================
print("\n" + "=" * 80)
print("ШИФРОВАНИЕ")
print("=" * 80)

text = input("\nВведите текст для шифрования: ")

cipher = encrypt(text, key, size_matrix)

print("\n" + "=" * 80)
print("РЕЗУЛЬТАТ ШИФРОВАНИЯ")
print("=" * 80)
print(f"Исходный текст:       {text}")
print(f"Зашифрованный текст:  {cipher}")
print(f"Длина:                {len(cipher)} символов")

# ============================================================================
# РАСШИФРОВАНИЕ
# ============================================================================
print("\n" + "=" * 80)
print("РАСШИФРОВАНИЕ")
print("=" * 80)

plain = decrypt(cipher, key, size_matrix)

print("\n" + "=" * 80)
print("РЕЗУЛЬТАТ РАСШИФРОВАНИЯ")
print("=" * 80)
print(f"Зашифрованный текст:  {cipher}")
print(f"Расшифрованный текст: {plain}")
print(f"Длина:                {len(plain)} символов")

# Проверка корректности
print("\n" + "-" * 80)
# Для сравнения нормализуем исходный текст так же, как при шифровании
original_normalized = normalize_text(replace_special_chars(text))
if original_normalized[:len(plain)] == plain[:len(original_normalized)]:
    print(" Расшифрование успешно!")
else:
    print("[Ошибка] Ошибка расшифрования!")
print("-" * 80)