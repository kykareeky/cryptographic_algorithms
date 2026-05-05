import os

alph = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def clear(text):
    text = text.lower()
    text = text.replace(',', 'зпт')
    text = text.replace('.', 'тчк')
    text = text.replace('ё', 'е')
    text = text.replace(' ', 'прб')
    text = "".join(c for c in text if c.isalnum())
    return text

def vizhenc_autokey_cipher(text, start_key):
    cipher = ""
    key = start_key
    for i in range(len(text)):
        c_index = (alph.index(text[i]) + alph.index(key[i])) % 32
        c = alph[c_index]
        cipher += c
        key += c
    return cipher

def vizhdec_autokey_cipher(text, start_key):
    plain = ""
    key = start_key
    for i in range(len(text)):
        p_index = (alph.index(text[i]) - alph.index(key[i])) % 32
        p = alph[p_index]
        plain += p
        key += text[i]
    plain = plain.replace('зпт', ',')
    plain = plain.replace('тчк', '.')
    plain = plain.replace('прб', ' ')
    return plain

def main():
    print("=" * 60)
    print("ШИФР ВИЖИНЕРА (АВТОКЛЮЧ ПО ШИФРТЕКСТУ)")
    print("=" * 60)
    
    action = input("\nВыберите действие \n1 - шифрование \n2 - расшифрование ").strip()
    
    print("\n1 - Ввод текста в консоли")
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
            print(" Текст не введен!")
            return
    elif choice == '2':
        if not os.path.exists('input.txt'):
            print(" Файл input.txt не найден!")
            return
        with open('input.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print(" Неверный выбор!")
        return
    
    key = input("\nВведите начальный ключ (1 символ из алфавита): ")
    if len(key) != 1 or key not in alph:
        print(" Ключ должен быть одним символом из алфавита!")
        return
    
    cleaned = clear(text)
    
    print("\n" + "-" * 40)
    print("РЕЗУЛЬТАТ")
    print("-" * 40)
    
    if action == '1':
        result = vizhenc_autokey_cipher(cleaned, key)
        print("\n" + "=" * 60)
        print("ЗАШИФРОВАННЫЙ ТЕКСТ:")
        print(result)
        print("=" * 60)
    else:
        result = vizhdec_autokey_cipher(cleaned, key)
        print("\n" + "=" * 60)
        print("РАСШИФРОВАННЫЙ ТЕКСТ:")
        print(result)
        print("=" * 60)

if __name__ == "__main__":
    main()