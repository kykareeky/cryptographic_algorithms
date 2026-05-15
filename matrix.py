import os
import numpy as np

ALPHABET = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
# [КРИПТО] Размер алфавита Z_32, используемый для модульной арифметики букв
ALPHABET_SIZE = len(ALPHABET)
# [КРИПТО] Отображение маркеров пунктуации в отрицательные целые числа для сохранения структуры текста при матричном преобразовании
# Уникальные отрицательные коды для маркеров пунктуации
MARKER_CODES = {'ТЧК': -1, 'ПРБ': -2, 'ЗПТ': -3, 'ВПР': -4, 'ВСК': -5}
# [КРИПТО] Обратное отображение отрицательных кодов в символы пунктуации
CODE_TO_PUNCT = {-1: '.', -2: ' ', -3: ',', -4: '?', -5: '!'}
# ИСПРАВЛЕНО: теперь словарь сопоставляет символы с маркерами, а не числа с маркерами
PUNCT_TO_MARKER = {'.': 'ТЧК', ' ': 'ПРБ', ',': 'ЗПТ', '?': 'ВПР', '!': 'ВСК'}

def normalize_text_with_punct(text):
    """Замена спецсимволов на маркеры и приведение к верхнему регистру"""
    # [КРИПТО] Канонизация входного потока для работы в конечном поле/кольце
    text = text.upper().replace('Ё', 'Е')
    result = []
    for char in text:
        if char in ALPHABET:
            result.append(char)
        elif char in PUNCT_TO_MARKER:
            result.append(PUNCT_TO_MARKER[char])
    return ''.join(result)

def text_to_indices(text):
    """Преобразование текста в список индексов (буквы: 1..32, пунктуация: уникальные отрицательные коды)"""
    indices = []
    i = 0
    text_upper = text.upper()
    # [КРИПТО] Цикл векторизации текста: преобразование строки в числовой массив для матричных операций
    while i < len(text_upper):
        matched = False
        # Проверяем маркеры пунктуации
        for marker, code in MARKER_CODES.items():
            if text_upper[i:i+len(marker)] == marker:
                indices.append(code)
                i += len(marker)
                matched = True
                break
        if not matched:
            char = text_upper[i]
            if char in ALPHABET:
                # [КРИПТО] Сдвиг индекса на +1: буквы маппятся в диапазон [1, 32], чтобы 0 остался резервным
                indices.append(ALPHABET.index(char) + 1)
                i += 1
    return indices

def indices_to_text(indices):
    """Обратное преобразование индексов в текст с восстановлением пунктуации"""
    text = []
    # [КРИПТО] Цикл обратной декодировки числового массива в символьный алфавит
    for idx in indices:
        if idx in CODE_TO_PUNCT:
            text.append(CODE_TO_PUNCT[idx])
        elif idx > 0:
            # [КРИПТО] Возврат в диапазон [1, 32] с учётом циклического сдвига (mod 32)
            idx = ((idx - 1) % ALPHABET_SIZE) + 1
            text.append(ALPHABET[idx - 1])
    return ''.join(text)

def matrix_encrypt(text, key_matrix):
    """Шифрование текста матричным методом"""
    # [КРИПТО] Подготовка открытого текста к блочной обработке шифром Хилла
    normalized_text = normalize_text_with_punct(text)
    indices = text_to_indices(normalized_text)
    m, n = key_matrix.shape
    # [КРИПТО] Padding: дополнение массива до кратности размеру блока n (добавляем 'А'=1)
    while len(indices) % n != 0:
        indices.append(1)
    
    encrypted_indices = []
    # [КРИПТО] Цикл поблочной обработки: разбиение вектора открытого текста на подблоки длины n
    for block_num in range(0, len(indices), n):
        # [КРИПТО] B: вектор-столбец открытого текста P_i текущего блока
        B = np.array(indices[block_num:block_num+n]).reshape(n, 1)
        # [КРИПТО] Линейное преобразование: C_i = K * B_i (mod 32 не применяется явно, используется прямая арифметика)
        C = np.dot(key_matrix, B)
        encrypted_indices.extend(C.flatten().tolist())
    return encrypted_indices

def matrix_decrypt(encrypted_indices, key_matrix):
    """Расшифрование матричным методом"""
    try:
        # [КРИПТО] Вычисление обратной матрицы ключа K^{-1} для инвертирования линейного преобразования
        matrix_inv = np.linalg.inv(key_matrix)
        matrix_inv_int = np.round(matrix_inv).astype(int)
        m, n = key_matrix.shape
        encrypted_indices = list(encrypted_indices)
        # Дополняем до кратности m
        while len(encrypted_indices) % m != 0:
            encrypted_indices.append(1)
        decrypted_indices = []
        # [КРИПТО] Цикл поблочного восстановления открытого текста
        for block_num in range(0, len(encrypted_indices), m):
            # [КРИПТО] C: вектор-столбец шифртекста текущего блока
            C = np.array(encrypted_indices[block_num:block_num+m]).reshape(m, 1)
            # [КРИПТО] Обратное преобразование: P_i = K^{-1} * C_i
            B = np.dot(matrix_inv_int, C)
            for val in B.flatten().tolist():
                # Модуль применяется ТОЛЬКО к положительным значениям (буквам)
                if val > 0:
                    # [КРИПТО] Возврат индекса в канонический диапазон [1, 32] по модулю ALPHABET_SIZE
                    val = int(((val - 1) % ALPHABET_SIZE) + 1)
                decrypted_indices.append(val)
        return decrypted_indices
    except:
        return None

def main():
    print("=" * 60)
    print("МАТРИЧНЫЙ ШИФР")
    print("=" * 60)
    action = input( "\nВыберите действие \n1 - Шифрование \n2 - Расшифрование  ").strip()

    print( "\n1 - Ввод текста в консоли ")
    print( "2 - Чтение текста из файла (input.txt) ")
    choice = input( "\nВаш выбор:  ").strip()

    if choice == '1':
        print( "\nВведите текст (для завершения введите пустую строку): ")
        lines = []
        while True:
            line = input()
            if line ==  " ":
                break
            lines.append(line)
        text =  "\n ".join(lines)
        if not text:
            print( "[Ошибка] Текст не введен! ")
            return
    elif choice == '2':
        if not os.path.exists('input.txt'):
            print( "[Ошибка] Файл input.txt не найден! ")
            return
        with open('input.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print( "[Ошибка] Неверный выбор! ")
        return

    rows = int(input( "\nВведите количество строк матрицы (минимум 2):  "))
    cols = int(input( "Введите количество столбцов матрицы (минимум 2):  "))
    print(f"\nВведите {rows*cols} чисел для матрицы {rows}x{cols}: ")
    key_input = input( "Числа через пробел:  ")
    numbers = [int(x) for x in key_input.split()]
    if len(numbers) != rows * cols:
        print( "[Ошибка] Неверное количество чисел! ")
        return
    # [КРИПТО] Формирование матрицы ключа K из пользовательского ввода
    key_matrix = np.array(numbers).reshape(rows, cols)

    print( "\n " +  "-" * 40)
    print( "РЕЗУЛЬТАТ ")
    print( "-" * 40)

    if action == '1':
        encrypted = matrix_encrypt(text, key_matrix)
        print( "\n " +  "= " * 60)
        print( "ЗАШИФРОВАННЫЕ ИНДЕКСЫ: ")
        print(' '.join(str(x) for x in encrypted))
        print( "= " * 60)
    else:
        try:
            input_indices = [int(x) for x in text.split()]
            decrypted_indices = matrix_decrypt(input_indices, key_matrix)
            if decrypted_indices:
                result = indices_to_text(decrypted_indices)
                print( "\n " +  "= " * 60)
                print( "РАСШИФРОВАННЫЙ ТЕКСТ: ")
                print(result)
                print( "= " * 60)
            else:
                print( "[Ошибка] Расшифрование не удалось! ")
        except ValueError:
            print( "[Ошибка] Некорректный формат входных данных! Ожидались числа через пробел. ")

if __name__ == "__main__":
    main()