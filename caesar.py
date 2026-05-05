import os

def replace_special_chars(text):
    replacements = {',': 'зпт', '.': 'тчк', ' ': 'прб', '"': 'квч', "'": 'квч', '«': 'квч', '»': 'квч', '`': 'квч', '!': 'вскл'}
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

def caesar_cipher(text, shift=3, encrypt=True):
    alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    n = len(alphabet)
    result = []
    # Убран пропуск маркеров. Теперь шифруется весь текст целиком
    for char in text:
        if char in alphabet:
            idx = alphabet.index(char)
            new_idx = (idx + shift) % n if encrypt else (idx - shift) % n
            result.append(alphabet[new_idx])
        else:
            result.append(char)
    return ''.join(result)

def main():
    print("=" * 60)
    print("ШИФР ЦЕЗАРЯ")
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
        if not os.path.exists('input.txt'):
            print("[Ошибка] Файл input.txt не найден!")
            return
        with open('input.txt', 'r', encoding='utf-8') as f:
            original_text = f.read()
    else:
        print("[Ошибка] Неверный выбор!")
        return
    
    try:
        shift_input = input("\nВведите сдвиг (по умолчанию 3): ").strip()
        shift = int(shift_input) if shift_input else 3
    except ValueError:
        print("[Ошибка] Неверный формат сдвига! Используется значение по умолчанию: 3")
        shift = 3
        
    prepared_text, case_info = prepare_text(original_text)
    
    print("\n" + "-" * 40)
    print("ПРОЦЕСС")
    print("-" * 40)
    
    if action == '1':
        encrypted = caesar_cipher(prepared_text, shift, encrypt=True)
        print("\n" + "=" * 60)
        print("ЗАШИФРОВАННЫЙ ТЕКСТ:")
        print(encrypted)
        print("=" * 60)
    else:
        decrypted = caesar_cipher(prepared_text, shift, encrypt=False)
        decrypted_with_case = restore_case(decrypted, case_info)
        result = restore_special_chars(decrypted_with_case)
        print("\n" + "=" * 60)
        print("РАСШИФРОВАННЫЙ ТЕКСТ:")
        print(result)
        print("=" * 60)

if __name__ == "__main__":
    main()