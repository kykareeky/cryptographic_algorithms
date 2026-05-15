import os

alph = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def clear(text):
    # [КРИПТО] Нормализация текста для работы в аддитивной группе Z_32
    text = text.lower()
    text = text.replace(',', 'зпт')
    text = text.replace('.', 'тчк')
    text = text.replace('ё', 'е')
    text = text.replace(' ', 'прб')
    text = "".join(c for c in text if c.isalnum())
    return text

def vizhenc(text, key):
    shipr = ""
    # [КРИПТО] Счётчик позиций в ключевой последовательности (key stream index)
    chetcikey = 0
    # [КРИПТО] Цикл побуквенного наложения ключа на открытый текст
    for i in range(len(text)):
        # [КРИПТО] C_i = (P_i + K_i) mod 32. Индекс key[chetcikey % len(key)] обеспечивает циклическое повторение гаммы
        shipr += alph[(alph.index(text[i]) + alph.index(key[chetcikey % len(key)])) % 32]
        chetcikey += 1
    return shipr

def vizhdec(text, key):
    shipr = ""
    chetcikey = 0
    # [КРИПТО] Цикл восстановления открытого текста с динамическим наращиванием ключа
    for i in range(len(text)):
        # [КРИПТО] P_i = (C_i - K_i) mod 32. Модульное вычитание инвертирует шифрование
        dec_char = alph[(alph.index(text[i]) - alph.index(key[chetcikey % len(key)])) % 32]
        shipr += dec_char
        # [КРИПТО] Ключевое свойство автоключа: расшифрованный символ открытого текста немедленно добавляется в конец гаммы
        # [КРИПТО] Это устраняет периодичность ключа и повышает криптостойкость против частотного анализа
        key += dec_char
        chetcikey += 1
    shipr = shipr.replace('зпт', ',')
    shipr = shipr.replace('тчк', '.')
    shipr = shipr.replace('прб', ' ')
    return shipr

def main():
    print("=" * 60)
    print("ШИФР ВИЖИНЕРА (САМОКЛЮЧ)")
    print("=" * 60)
    action = input( "\nВыберите действие \n1 - шифрование \n2 - расшифрование  ").strip()

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
            print( " Текст не введен! ")
            return
    elif choice == '2':
        if not os.path.exists('input.txt'):
            print( " Файл input.txt не найден! ")
            return
        with open('input.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print( " Неверный выбор! ")
        return

    key = input( "\nВведите начальный ключ (1 символ):  ")
    cleaned = clear(text)

    print( "\n " +  "-" * 40)
    print( "РЕЗУЛЬТАТ ")
    print( "-" * 40)

    if action == '1':
        # [КРИПТО] Формирование полного самоключа: начальный символ + весь открытый текст (кроме последнего, для выравнивания длины)
        full_key = key + cleaned
        full_key = full_key[:len(full_key) - 1]
        # [КРИПТО] Передача готовой гаммы в функцию шифрования Вижинера
        result = vizhenc(cleaned, full_key)
        print( "\n " +  "= " * 60)
        print( "ЗАШИФРОВАННЫЙ ТЕКСТ: ")
        print(result)
        print( "= " * 60)
    else:
        # [КРИПТО] При расшифровке передаётся только начальный символ. Функция сама восстанавливает остальную часть гаммы
        result = vizhdec(cleaned, key)
        print( "\n " +  "= " * 60)
        print( "РАСШИФРОВАННЫЙ ТЕКСТ: ")
        print(result)
        print( "= " * 60)

if __name__ == "__main__":
    main()