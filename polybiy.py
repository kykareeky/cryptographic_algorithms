import os

def replace_special_chars(text):
    """Замена специальных символов на их текстовые обозначения."""
    # [КРИПТО] Маппинг пунктуации в буквенные маркеры для сохранения структуры в квадрате Полибия
    replacements = {
        ',': 'зпт', '.': 'тчк', ' ': 'прб', '"': 'квч',
        "'": 'квч', '«': 'квч', '»': 'квч', '`': 'квч', '!': 'вскл'
    }
    result = []
    for char in text:
        if char in replacements:
            result.append(replacements[char])
        else:
            result.append(char)
    return ''.join(result)

def restore_special_chars(text):
    """Восстановление специальных символов из текстовых обозначений."""
    # [КРИПТО] Обратное преобразование маркеров, отсортированных по длине для избежания частичных замен
    replacements = {'зпт': ',', 'тчк': '.', 'прб': ' ', 'квч': '"', 'вскл': '!'}
    sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
    result = text
    for key in sorted_keys:
        result = result.replace(key, replacements[key])
        result = result.replace(key.upper(), replacements[key])
    return result

def prepare_text(text):
    """Подготовка текста: замена спецсимволов и приведение к верхнему регистру с сохранением info."""
    alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    alphabet_lower = alphabet.lower()
    text_with_replacements = replace_special_chars(text)
    case_info = []
    cleaned_text = []
    # [КРИПТО] Цикл фильтрации символов: сохранение только букв алфавита и маркеров, запись исходного регистра
    for char in text_with_replacements:
        if char in alphabet:
            cleaned_text.append(char)
            case_info.append(True)  
        elif char in alphabet_lower:
            cleaned_text.append(char.upper())
            case_info.append(False) 
        else:
            cleaned_text.append(char)
            case_info.append(True)  
            
    return ''.join(cleaned_text), case_info

def restore_case(text, case_info):
    """Восстановление исходного регистра текста."""
    result = []
    # [КРИПТО] Цикл восстановления капитализации букв после расшифровки координат
    for i, char in enumerate(text):
        if i < len(case_info):
            if char.isalpha():
                result.append(char.upper() if case_info[i] else char.lower())
            else:
                result.append(char)
        else:
            result.append(char)
    return ''.join(result)

def polybius_cipher(text, encrypt=True):
    """Шифр Квадрата Полибия для русского алфавита (5x7)."""
    alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    char_to_coord = {}
    coord_to_char = {}
    idx = 0
    # [КРИПТО] Генерация таблицы координат: 7 строк x 5 столбцов = 35 ячеек. Алфавит (33 буквы) занимает первые ячейки
    for r in range(1, 8):       
        for c in range(1, 6):   
            if idx < len(alphabet):
                ch = alphabet[idx]
                coord = f"{r}{c}"
                # [КРИПТО] Прямое и обратное отображение символ <-> координата (row, col)
                char_to_coord[ch] = coord
                coord_to_char[coord] = ch
                idx += 1
                
    if encrypt:
        result = []
        # [КРИПТО] Шифрование: замена каждого символа на его двухцифровую координату
        for char in text:
            if char in char_to_coord:
                result.append(char_to_coord[char])
            else:
                result.append(char) 
        return ' '.join(result)
    else:
        result = []
        # [КРИПТО] Парсинг строки координат, разделённых пробелами
        parts = text.split()
        # [КРИПТО] Расшифрование: замена каждой координаты на соответствующий символ
        for part in parts:
            if part in coord_to_char:
                result.append(coord_to_char[part])
            else:
                result.append(part) 
        return ''.join(result)

def main():
    print("=" * 60)
    print("ШИФР КВАДРАТА ПОЛИБИЯ")
    print("=" * 60)
    action = input( "\nВыберите действие: \n1 - шифрование \n2 - расшифрование  ").strip()
    if action not in ['1', '2']:
        print( "[Ошибка] Неверный выбор действия! ")
        return
        
    print( "\nВыберите источник текста: ")
    print( "1 - Ввод текста в консоли ")
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
        original_text =  "\n ".join(lines)
        if not original_text:
            print( "[Ошибка] Текст не введен! ")
            return
    elif choice == '2':
        if not os.path.exists('input.txt'):
            print( "[Ошибка] Файл input.txt не найден! ")
            return
        with open('input.txt', 'r', encoding='utf-8') as f:
            original_text = f.read()
    else:
        print( "[Ошибка] Неверный выбор! ")
        return
        
    print( "\n " +  "-" * 40)
    print( "ПРОЦЕСС ")
    print( "-" * 40)

    if action == '1':
        prepared_text, case_info = prepare_text(original_text)
        # [КРИПТО] Запуск преобразования символ -> координаты
        result = polybius_cipher(prepared_text, encrypt=True)
        print( "\n " +  "= " * 60)
        print( "ЗАШИФРОВАННЫЙ ТЕКСТ: ")
        print(result)
        print( "= " * 60)
    else:
        # [КРИПТО] Запуск преобразования координаты -> символ
        decrypted = polybius_cipher(original_text, encrypt=False)
        
        case_info = [True] * len(decrypted)
        decrypted_with_case = restore_case(decrypted, case_info)
        result = restore_special_chars(decrypted_with_case)
        
        print( "\n " +  "= " * 60)
        print( "РАСШИФРОВАННЫЙ ТЕКСТ: ")
        print(result)
        print( "= " * 60)

if __name__ == "__main__":
    main()