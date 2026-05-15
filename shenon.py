import random

ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
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
    # [КРИПТО] Приведение к каноническому виду для работы в поле Z_32
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

def generate_key(length):
    # [КРИПТО] Генерация истинно случайной гаммы длины, равной длине открытого текста. Условие совершенной секретности по Шеннону.
    return "".join(random.choice(ALPHABET) for _ in range(length))

def generate_key_from_lcg(length, t0, a, c, mod=32):
    key_chars = []
    # [КРИПТО] Инициализация состояния генератора псевдослучайных чисел (ЛКГ)
    t = t0 % mod
    # [КРИПТО] Цикл генерации гаммы по рекуррентной формуле t_{n+1} = (a * t_n + c) mod m
    for _ in range(length):
        key_chars.append(ALPHABET[t])
        # [КРИПТО] Линейное конгруэнтное преобразование. При правильно выбранных a, c, mod обеспечивает максимальный период
        t = (a * t + c) % mod
    return ''.join(key_chars)

def chars_to_numbers(text):
    numbers = []
    for char in text:
        idx = ALPHABET.find(char)
        numbers.append(f"{idx:02d}")
    return " ".join(numbers)

def numbers_to_chars(numbers_str):
    chars = []
    for num_str in numbers_str.split():
        try:
            idx = int(num_str)
            if 0 <= idx < len(ALPHABET):
                chars.append(ALPHABET[idx])
            else:
                raise ValueError(f"Номер {idx} вне диапазона 0-31")
        except ValueError:
            raise ValueError(f"Неверный формат числа: {num_str}")
    return ''.join(chars)

def encrypt_otp(text, key):
    if len(text) != len(key):
        raise ValueError(f"Длина текста ({len(text)}) должна равняться длине ключа ({len(key)})")
    result_numbers = []
    result_chars = []
    print( "\n " +  "= " * 60)
    print( "ПРОЦЕСС ШИФРОВАНИЯ ")
    print( "= " * 60)
    print(f"\nФормула: C = (P + K) mod {len(ALPHABET)} ")
    print( "Номера букв: А=00, Б=01, ..., Я=31 ")
    print( "\nПосимвольное шифрование: ")
    print( "-" * 40)

    # [КРИПТО] Цикл поблочного (посимвольного) сложения открытого текста и гаммы в кольце вычетов Z_32
    for i in range(len(text)):
        # [КРИПТО] P_i: индекс текущего символа открытого текста в алфавите
        p_char = text[i]
        k_char = key[i]
        p_idx = ALPHABET.find(p_char)
        # [КРИПТО] K_i: индекс текущего символа ключа (гаммы)
        k_idx = ALPHABET.find(k_char)
        # [КРИПТО] C_i = (P_i + K_i) mod 32. Модульное сложение гарантирует равномерное распределение вероятностей при случайном ключе
        c_idx = (p_idx + k_idx) % len(ALPHABET)
        c_char = ALPHABET[c_idx]
        result_numbers.append(f"{c_idx:02d} ")
        result_chars.append(c_char)

        if i  < 10 or i  >= len(text) - 3:
            print(f"  [{i+1:3d}] {p_char}({p_idx:02d}) + {k_char}({k_idx:02d}) = {c_char}({c_idx:02d}) ")
        elif i == 10:
            print( "  ... ")
    print( "-" * 40)

    return  "  ".join(result_numbers), ''.join(result_chars)

def decrypt_otp(cipher_numbers, key):
    if len(cipher_numbers) != len(key):
        raise ValueError(f"Длина шифртекста ({len(cipher_numbers)}) должна равняться длине ключа ({len(key)})")
    result_chars = []
    print( "\n " +  "= " * 60)
    print( "ПРОЦЕСС РАСШИФРОВАНИЯ ")
    print( "= " * 60)
    print(f"\nФормула: P = (C - K) mod {len(ALPHABET)} ")
    print( "Номера букв: А=00, Б=01, ..., Я=31 ")
    print( "\nПосимвольное расшифрование: ")
    print( "-" * 40)

    # [КРИПТО] Цикл восстановления открытого текста путём модульного вычитания гаммы из шифртекста
    for i in range(len(cipher_numbers)):
        c_idx = cipher_numbers[i]
        k_char = key[i]
        # [КРИПТО] K_i: восстановление индекса гаммы из буквенного представления
        k_idx = ALPHABET.find(k_char)
        # [КРИПТО] P_i = (C_i - K_i) mod 32. Обратная операция к шифрованию в аддитивной группе
        p_idx = (c_idx - k_idx) % len(ALPHABET)
        p_char = ALPHABET[p_idx]
        result_chars.append(p_char)

        if i  < 10 or i  >= len(cipher_numbers) - 3:
            print(f"  [{i+1:3d}] {c_idx:02d} - {k_char}({k_idx:02d}) = {p_char}({p_idx:02d}) ")
        elif i == 10:
            print( "  ... ")
    print( "-" * 40)

    return ''.join(result_chars)

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
        try:
            with open('input.txt', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print("[Ошибка] Файл input.txt не найден!")
            return None
    else:
        print("[Ошибка] Неверный выбор!")
        return None

def main():
    print( "= " * 60)
    print( "ШИФР ГАММИРОВАНИЯ (ОДНОРАЗОВЫЙ БЛОКНОТ) ")
    print( "= " * 60)
    print(f"\nАлфавит ({len(ALPHABET)} букв): {ALPHABET} ")
    print( "Примечание: буква Ё заменяется на Е, номера букв: А=00, Б=01, ..., Я=31 ")
    print( "\nПринцип работы: ")
    print( "• Шифрование: C = (P + K) mod 32 ")
    print( "• Расшифрование: P = (C - K) mod 32 ")
    print( "• Ключ должен быть равен длине текста ")
    print( "• Ключ используется только 1 раз ")
    while True:
        print( "\n " +  "-" * 40)
        print( "ГЛАВНОЕ МЕНЮ ")
        print( "-" * 40)
        print( "1 - Зашифровать текст (случайный ключ) ")
        print( "2 - Зашифровать текст (LCG параметры) ")
        print( "3 - Расшифровать текст ")
        print( "0 - Выход ")
        print( "-" * 40)

        choice = input( "\nВаш выбор:  ").strip()

        if choice == '0':
            print( "\nПрограмма завершена. ")
            print( "= " * 60)
            break

        elif choice == '1':
            print( "\n " +  "-" * 40)
            print( "ШИФРОВАНИЕ С ГЕНЕРАЦИЕЙ СЛУЧАЙНОГО КЛЮЧА ")
            print( "-" * 40)

            text = get_text_input()
            if text is None:
                continue

            # Преобразуем спецсимволы в маркеры
            prepared_text = replace_special_chars(text)
            if not prepared_text:
                print( "[Ошибка] Текст не содержит допустимых символов! ")
                continue

            print(f"\nИсходный текст:        {text} ")
            print(f"Подготовленный текст:  {prepared_text} ")
            print(f"Длина текста:          {len(prepared_text)} символов ")

            # [КРИПТО] Генерация одноразового ключа, статистически независимого от открытого текста
            current_key = generate_key(len(prepared_text))
            print(f"\nСгенерирован случайный ключ (буквы): {current_key} ")
            print(f"Сгенерирован случайный ключ (номера): {chars_to_numbers(current_key)} ")

            try:
                ciphertext_numbers, ciphertext_chars = encrypt_otp(prepared_text, current_key)
                print( "\n " +  "= " * 60)
                print( "РЕЗУЛЬТАТ ШИФРОВАНИЯ ")
                print( "= " * 60)
                print(f"Подготовленный текст (буквы):      {prepared_text} ")
                print(f"Подготовленный текст (номера):     {chars_to_numbers(prepared_text)} ")
                print(f"Ключ (буквы):                      {current_key} ")
                print(f"Ключ (номера):                     {chars_to_numbers(current_key)} ")
                print(f"Зашифрованный текст (номера):      {ciphertext_numbers} ")
                print(f"Зашифрованный текст (буквы):       {ciphertext_chars} ")
                print(f"Длина:                             {len(prepared_text)} символов ")
                print( "= " * 60)
            except Exception as e:
                print(f"\n[Ошибка] Ошибка при шифровании: {e} ")

        elif choice == '2':
            print( "\n " +  "-" * 40)
            print( "ШИФРОВАНИЕ С ПАРАМЕТРАМИ LCG ")
            print( "-" * 40)
            print( "Гамма генерируется по формуле: t_{i+1} = (A * t_i + C) mod 32 ")

            text = get_text_input()
            if text is None:
                continue

            # Преобразуем спецсимволы в маркеры
            prepared_text = replace_special_chars(text)
            if not prepared_text:
                print( "[Ошибка] Текст не содержит допустимых символов! ")
                continue

            print(f"\nИсходный текст:        {text} ")
            print(f"Подготовленный текст:  {prepared_text} ")
            print(f"Длина текста:          {len(prepared_text)} символов ")

            try:
                t0 = int(input( "Введите T0 (начальное значение):  "))
                c = int(input( "Введите C (приращение):  "))
                a = int(input( "Введите A (множитель):  "))
            except ValueError:
                print( "[Ошибка] Параметры должны быть целыми числами. ")
                continue

            # [КРИПТО] Генерация псевдослучайной гаммы через линейный конгруэнтный метод
            current_key = generate_key_from_lcg(len(prepared_text), t0, a, c, mod=32)
            print(f"\nСгенерированный ключ (буквы): {current_key} ")
            print(f"Сгенерированный ключ (номера): {chars_to_numbers(current_key)} ")

            try:
                ciphertext_numbers, ciphertext_chars = encrypt_otp(prepared_text, current_key)
                print( "\n " +  "= " * 60)
                print( "РЕЗУЛЬТАТ ШИФРОВАНИЯ ")
                print( "= " * 60)
                print(f"Подготовленный текст (буквы):      {prepared_text} ")
                print(f"Подготовленный текст (номера):     {chars_to_numbers(prepared_text)} ")
                print(f"Параметры: T0={t0}, C={c}, A={a} ")
                print(f"Сгенерированный ключ (буквы):      {current_key} ")
                print(f"Сгенерированный ключ (номера):     {chars_to_numbers(current_key)} ")
                print(f"Зашифрованный текст (номера):      {ciphertext_numbers} ")
                print(f"Зашифрованный текст (буквы):       {ciphertext_chars} ")
                print(f"Длина:                             {len(prepared_text)} символов ")
                print( "= " * 60)
                print( "Сохраните ключ (или параметры) для расшифровки. ")
            except Exception as e:
                print(f"\n[Ошибка] Ошибка при шифровании: {e} ")

        elif choice == '3':
            print( "\n " +  "-" * 40)
            print( "РАСШИФРОВАНИЕ ТЕКСТА ")
            print( "-" * 40)
            print( "Введите шифртекст в виде номеров через пробел (00-31) ")
            print( "Пример: 15 07 28 03 31 00 12 ")

            cipher_input = input( "\nВведите зашифрованный текст (номера через пробел):  ").strip()
            if not cipher_input:
                print( "[Ошибка] Текст не может быть пустым! ")
                continue

            try:
                cipher_numbers = []
                for num_str in cipher_input.split():
                    idx = int(num_str)
                    if 0  <= idx  < len(ALPHABET):
                        cipher_numbers.append(idx)
                    else:
                        print(f"[Ошибка] Номер {idx} вне диапазона 0-31 ")
                        continue
                if not cipher_numbers:
                    print( "[Ошибка] Не удалось распознать ни одного корректного номера! ")
                    continue
            except ValueError:
                print( "[Ошибка] Введите числа от 00 до 31 через пробел! ")
                continue

            print(f"\nЗашифрованный текст (номера): {' '.join(f'{x:02d}' for x in cipher_numbers)} ")
            print(f"Длина текста:                 {len(cipher_numbers)} символов ")

            key_input = input(f"\nВведите ключ ({len(cipher_numbers)} символов, буквы или номера):  ").strip()
            
            try:
                if ' ' in key_input:
                    key = numbers_to_chars(key_input)
                else:
                    key = replace_special_chars(key_input)
            except:
                key = replace_special_chars(key_input)

            if len(key) != len(cipher_numbers):
                print(f"\n[Ошибка] Длина ключа ({len(key)}) не равна длине шифртекста ({len(cipher_numbers)}) ")
                continue

            try:
                plaintext_with_markers = decrypt_otp(cipher_numbers, key)
                # Восстанавливаем спецсимволы из маркеров
                result  = restore_special_chars(plaintext_with_markers)
                print( "\n " +  "= " * 60)
                print( "РЕЗУЛЬТАТ РАСШИФРОВАНИЯ ")
                print( "= " * 60)
                print(f"Зашифрованный текст (номера): {' '.join(f'{x:02d}' for x in cipher_numbers)} ")
                print(f"Ключ (буквы):                 {key} ")
                print(f"Ключ (номера):                {chars_to_numbers(key)} ")
                print(f"Расшифрованный текст:         {result} ")
                print(f"Длина:                        {len(result)} символов ")
                print( "= " * 60)
            except Exception as e:
                print(f"\n[Ошибка] Ошибка при расшифровании: {e} ")

        else:
            print( "\n[Ошибка] Неверный выбор. Попробуйте снова. ")

if __name__ == "__main__":
    main()