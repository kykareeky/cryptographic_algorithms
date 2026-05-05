import os

def replace_special_chars(text):
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
    replacements = {'зпт': ',', 'тчк': '.', 'прб': ' ', 'квч': '"', 'вскл': '!'}
    sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
    result = text
    for key in sorted_keys:
        # Заменяем как строчные, так и заглавные варианты маркеров
        result = result.replace(key, replacements[key])
        result = result.replace(key.upper(), replacements[key])
    return result

def prepare_text(text):
    alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    alphabet_lower = alphabet.lower()
    text_with_replacements = replace_special_chars(text)
    case_info = []
    cleaned_text = []
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
    result = []
    for i, char in enumerate(text):
        if i < len(case_info):
            if char.isalpha():
                if case_info[i]:
                    result.append(char.upper())
                else:
                    result.append(char.lower())
            else:
                result.append(char)
        else:
            result.append(char)
    return ''.join(result)

def atbash_cipher(text):
    alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    reversed_alphabet = alphabet[::-1]
    atbash_dict = {alphabet[i]: reversed_alphabet[i] for i in range(len(alphabet))}
    specials = ['зпт', 'тчк', 'прб', 'квч', 'вскл']
    result = []
    i = 0
    while i < len(text):
        special_found = False
        for special in specials:
            chunk = text[i:i+len(special)]
            # Проверяем маркеры без учёта регистра
            if chunk == special or chunk == special.upper():
                result.append(chunk)  # сохраняем исходный регистр маркера
                i += len(special)
                special_found = True
                break
        if not special_found:
            current_char = text[i]
            if current_char in atbash_dict:
                result.append(atbash_dict[current_char])
            else:
                result.append(current_char)
            i += 1
    return ''.join(result)

def main():
    print("=" * 60)
    print("ШИФР АТБАШ")
    print("=" * 60)
    
    action = input("\nВыберите действие: \n1 - шифрование \n2 - расшифрование ").strip()
    
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
        original_text = "\n".join(lines)
        if not original_text:
            print("[Ошибка] Текст не введен!")
            return
    elif choice == '2':
        input_file = 'input.txt'
        if not os.path.exists(input_file):
            print(f"[Ошибка] Файл {input_file} не найден!")
            return
        with open(input_file, 'r', encoding='utf-8') as f:
            original_text = f.read()
    else:
        print("[Ошибка] Неверный выбор!")
        return
    
    prepared_text, case_info = prepare_text(original_text)
    
    if action == '1':
        print("\n" + "-" * 40)
        print("ШИФРОВАНИЕ")
        print("-" * 40)
        result = atbash_cipher(prepared_text)
        print("\n" + "=" * 60)
        print("ЗАШИФРОВАННЫЙ  ТЕКСТ:")
        print(result)
        print("=" * 60)
    else:
        print("\n" + "-" * 40)
        print("РАСШИФРОВКА")
        print("-" * 40)
        decrypted = atbash_cipher(prepared_text)
        decrypted_with_case = restore_case(decrypted, case_info)
        result = restore_special_chars(decrypted_with_case)
        print("\n" + "=" * 60)
        print("РАСШИФРОВАННЫЙ ТЕКСТ:")
        print(result)
        print("=" * 60)

if __name__ == "__main__":
    main()