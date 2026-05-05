alph = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def clear(text):
    text = text.lower()
    text = text.replace(',', 'зпт')
    text = text.replace('.', 'тчк')
    text = text.replace('ё', 'е')
    text = text.replace(' ', 'прб')
    text = "".join(c for c in text if c.isalnum())
    return text

def tritenc(text):
    restext = ""
    k = 0
    for i in range(len(text)):
        restext += alph[(alph.index(text[i]) + k) % 32]
        k += 1
    return restext

def tritdec(text):
    restext = ""
    k = 0
    for i in range(len(text)):
        restext += alph[(alph.index(text[i]) - k) % 32]
        k += 1
    restext = restext.replace('зпт', ',')
    restext = restext.replace('тчк', '.')
    restext = restext.replace('прб', ' ')
    return restext

def main():
    print("=" * 60)
    print("ШИФР ТРИТЕМИЯ")
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
    
    cleaned = clear(text)
    
    print("\n" + "-" * 40)
    print("РЕЗУЛЬТАТ")
    print("-" * 40)
    
    if action == '1':
        result = tritenc(cleaned)
        print("\n" + "=" * 60)
        print("ЗАШИФРОВАННЫЙ ТЕКСТ:")
        print(result)
        print("=" * 60)
    else:
        result = tritdec(cleaned)
        print("\n" + "=" * 60)
        print("РАСШИФРОВАННЫЙ ТЕКСТ:")
        print(result)
        print("=" * 60)

if __name__ == "__main__":
    main()