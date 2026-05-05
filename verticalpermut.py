import os

ALPHABET = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

# Словарь замены спецсимволов на маркеры
PUNCT_TO_MARKER = {
    ' ': 'ПРБ',
    ',': 'ЗПТ',
    '.': 'ТЧК',
    '!': 'ВСК',
    '?': 'ВПР'
}

# Обратный словарь для восстановления
MARKER_TO_PUNCT = {v: k for k, v in PUNCT_TO_MARKER.items()}


def replace_special_chars(text):
    """Замена спецсимволов на буквенные маркеры"""
    text = text.upper().replace('Ё', 'Е')
    result = []
    for char in text:
        if char in ALPHABET:
            result.append(char)
        elif char in PUNCT_TO_MARKER:
            result.append(PUNCT_TO_MARKER[char])
        # Остальные символы игнорируются
    return ''.join(result)


def restore_special_chars(text):
    """Восстановление спецсимволов из маркеров"""
    result = text
    # Сортируем по длине (от длинных к коротким) для корректной замены
    sorted_markers = sorted(MARKER_TO_PUNCT.keys(), key=len, reverse=True)
    for marker in sorted_markers:
        result = result.replace(marker, MARKER_TO_PUNCT[marker])
    return result


def generate_key_order(keyword):
    """Генерация порядка колонок на основе ключевого слова"""
    keyword = replace_special_chars(keyword)
    indexed_chars = [(char, i) for i, char in enumerate(keyword)]
    sorted_chars = sorted(indexed_chars, key=lambda x: x[0])
    order = [0] * len(keyword)
    for rank, (char, original_pos) in enumerate(sorted_chars):
        order[original_pos] = rank + 1
    return order


def vertical_permutation_encrypt(text, keyword):
    """Шифрование методом вертикальной перестановки"""
    text = replace_special_chars(text)
    keyword = replace_special_chars(keyword)
    
    if not keyword or not text:
        return "[Ошибка] пустой текст или ключ"
    
    key_order = generate_key_order(keyword)
    num_cols = len(keyword)
    num_rows = (len(text) + num_cols - 1) // num_cols
    
    # Заполнение таблицы
    table = []
    index = 0
    for row in range(num_rows):
        table_row = []
        for col in range(num_cols):
            if index < len(text):
                table_row.append(text[index])
                index += 1
            else:
                table_row.append('')  # Пустая ячейка для дополнения
        table.append(table_row)
    
    # Чтение по колонкам в порядке ключа
    encrypted = ""
    column_positions = [(key_order[i], i) for i in range(num_cols)]
    column_positions.sort(key=lambda x: x[0])
    
    for rank, col_index in column_positions:
        for row in range(num_rows):
            if table[row][col_index]:
                encrypted += table[row][col_index]
    
    return encrypted


def vertical_permutation_decrypt(encrypted_text, keyword):
    """Расшифрование методом вертикальной перестановки"""
    keyword = replace_special_chars(keyword)
    
    if not keyword or not encrypted_text:
        return "[Ошибка] пустой текст или ключ"
    
    key_order = generate_key_order(keyword)
    num_cols = len(keyword)
    num_rows = (len(encrypted_text) + num_cols - 1) // num_cols
    remainder = len(encrypted_text) % num_cols
    
    # Вычисляем длину каждой колонки
    if remainder == 0:
        col_lengths = [num_rows] * num_cols
    else:
        col_lengths = [num_rows if i < remainder else num_rows - 1 for i in range(num_cols)]
    
    # Создаём пустую таблицу
    table = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    
    # Заполняем колонки в порядке ключа
    column_positions = [(key_order[i], i) for i in range(num_cols)]
    column_positions.sort(key=lambda x: x[0])
    
    text_index = 0
    for rank, col_index in column_positions:
        col_len = col_lengths[col_index]
        for row in range(col_len):
            if text_index < len(encrypted_text):
                table[row][col_index] = encrypted_text[text_index]
                text_index += 1
    
    # Читаем таблицу построчно
    decrypted = ""
    for row in range(num_rows):
        for col in range(num_cols):
            if table[row][col]:
                decrypted += table[row][col]
    
    return decrypted


def get_text_input():
    """Получение текста от пользователя"""
    print("\nВыберите источник текста:")
    print("1 - Ввод текста в консоли")
    print("2 - Чтение текста из файла (input.txt)")
    choice = input("\nВаш выбор: ").strip()
    
    if choice == '1':
        print("\nВведите текст (для завершения введите пустую строку):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        text = "\n".join(lines)
        if not text:
            print("[Ошибка] Текст не введен!")
            return None
        return text
    elif choice == '2':
        if not os.path.exists('input.txt'):
            print("[Ошибка] Файл input.txt не найден!")
            return None
        with open('input.txt', 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print("[Ошибка] Неверный выбор!")
        return None


def main():
    print("=" * 60)
    print("ШИФР ВЕРТИКАЛЬНОЙ ПЕРЕСТАНОВКИ")
    print("=" * 60)
    
    action = input("\nВыберите действие \n1 - Шифрование \n2 - Расшифрование ").strip()
    if action not in ['1', '2']:
        print("[Ошибка] Неверный выбор действия!")
        return
    
    text = get_text_input()
    if text is None:
        return
    
    keyword = input("\nВведите ключевое слово: ").strip()
    if not keyword:
        print("[Ошибка] Ключ не введен!")
        return
    
    print("\n" + "-" * 40)
    print("ПРОЦЕСС")
    print("-" * 40)
    
    if action == '1':
        # Шифрование: текст с маркерами -> шифр
        result = vertical_permutation_encrypt(text, keyword)
        print("\n" + "=" * 60)
        print("ЗАШИФРОВАННЫЙ ТЕКСТ:")
        print(result)
        print("=" * 60)
    else:
        # Расшифрование: шифр -> текст с маркерами -> восстановление спецсимволов
        decrypted = vertical_permutation_decrypt(text, keyword)
        result = restore_special_chars(decrypted)
        print("\n" + "=" * 60)
        print("РАСШИФРОВАННЫЙ ТЕКСТ:")
        print(result)
        print("=" * 60)


if __name__ == "__main__":
    main()