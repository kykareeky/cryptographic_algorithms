import os

class CryptoSystem:
    def __init__(self):
        # [КРИПТО] Таблицы S-подстановок ГОСТ Р 34.12-2015 (МАГМА)
        # Реализуют нелинейное преобразование (confusion) на уровне 4-битных нибблов
        self.sboxes = [
            [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
            [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
            [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
            [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
            [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
            [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
            [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
            [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
        ]

    def magma_transform(self, input_hex):
        # [КРИПТО] Прямое S-преобразование: замена каждого 4-битного ниббла через соответствующий S-блок
        # Примечание: реализует только слой нелинейной подстановки ГОСТ, без линейной диффузии и раундов
        input_hex = input_hex.lower()
        if len(input_hex) != 8 or not all(c in '0123456789abcdef' for c in input_hex):
            return  "Ошибка: введите 8 hex символов "

        value = int(input_hex, 16)
        byte_parts = []
        # [КРИПТО] Цикл извлечения 8 нибблов из 32-битного числа
        for i in range(8):
            part = (value  >> (4 * i))  & 0xF
            byte_parts.append(part)

        result = 0
        # [КРИПТО] Цикл поблочной замены через таблицы S-box
        for i in range(8):
            substituted = self.sboxes[i][byte_parts[i]]
            result |= (substituted  << (4 * i))

        return format(result, '08x').upper()

    def magma_inverse_transform(self, input_hex):
        # [КРИПТО] Обратное S-преобразование: построение инверсных таблиц и замена нибблов
        input_hex = input_hex.lower()
        if len(input_hex) != 8 or not all(c in '0123456789abcdef' for c in input_hex):
            return  "Ошибка: введите 8 hex символов "

        value = int(input_hex, 16)
        byte_parts = []
        for i in range(8):
            part = (value  >> (4 * i))  & 0xF
            byte_parts.append(part)

        # [КРИПТО] Генерация обратных S-блоков для корректного обращения подстановки
        inverse_sboxes = []
        for sbox in self.sboxes:
            inverse = [0] * 16
            for i, val in enumerate(sbox):
                inverse[val] = i
            inverse_sboxes.append(inverse)

        result = 0
        # [КРИПТО] Цикл обратной замены
        for i in range(8):
            substituted = inverse_sboxes[i][byte_parts[i]]
            result |= (substituted  << (4 * i))

        return format(result, '08x').upper()

    def preprocess_text(self, text):
        return text

    def convert_punctuation(self, text, to_word=True):
        if to_word:
            replacements = {
                ',': 'зпт', '.': 'тчк', ' ': 'прб', ' "': 'квч',
                "' ": 'квч', '«': 'квч', '»': 'квч', '`': 'квч', '!': 'вскл'
            }
            for orig, repl in replacements.items():
                text = text.replace(orig, repl)
        else:
            replacements = {
                'зпт': ',', 'тчк': '.', 'прб': ' ', 'квч': ' "', 'вскл': '!'
            }
            for orig, repl in replacements.items():
                text = text.replace(orig, repl)
                text = text.replace(orig.upper(), repl)
        return  text

    def text_to_hex(self, text):
        text = self.preprocess_text(text)
        text_with_punct = self.convert_punctuation(text, to_word=True)
        text_no_spaces = text_with_punct.replace(' ', '')
        bytes_data = text_no_spaces.encode('utf-8')
        return bytes_data.hex()

    def hex_to_text(self, hex_string):
        try:
            bytes_data = bytes.fromhex(hex_string)
            text_result = bytes_data.decode('utf-8', errors='ignore').rstrip('\x00')
            text_result = self.convert_punctuation(text_result, to_word=False)
            return text_result
        except:
            return  "[Ошибка] при преобразовании hex в текст "

    def magma_encrypt_hex(self, input_hex):
        # [КРИПТО] Потоковая обработка hex-данных поблочным применением S-преобразования
        input_hex = input_hex.replace(' ', '').lower()
        if not all(c in '0123456789abcdef' for c in input_hex):
            return  "Ошибка: строка содержит недопустимые символы "

        if len(input_hex) % 8 != 0:
            input_hex = input_hex.ljust(((len(input_hex) // 8) + 1) * 8, '0')

        encrypted_blocks = []
        # [КРИПТО] Цикл разбиения потока на 8-hex-символьные блоки (32 бита)
        for i in range(0, len(input_hex), 8):
            block = input_hex[i:i + 8]
            encrypted_block = self.magma_transform(block)
            encrypted_blocks.append(encrypted_block)

        return ''.join(encrypted_blocks)

    def magma_decrypt_hex(self, hex_text):
        # [КРИПТО] Поблочное обращение S-преобразования для восстановления данных
        hex_text = hex_text.replace(' ', '').lower()
        if not all(c in '0123456789abcdef' for c in hex_text):
            return  "Ошибка: строка содержит недопустимые символы "

        if len(hex_text) % 8 != 0:
            return  "Ошибка: некорректная длина hex строки "

        decrypted_blocks = []
        for i in range(0, len(hex_text), 8):
            block = hex_text[i:i + 8]
            decrypted_block = self.magma_inverse_transform(block)
            decrypted_blocks.append(decrypted_block)

        return ''.join(decrypted_blocks)

def get_hex_input():
    print( "\nВыберите способ ввода hex-строки: ")
    print( "1. Ввести hex-строку вручную ")
    print( "2. Прочитать hex-строку из файла ")
    print( "3. Использовать тестовый вектор ")
    print( "4. Преобразовать текст в hex ")
    choice = input( "Ваш выбор (1-4):  ").strip()

    if choice == '1':
        hex_string = input( "Введите hex-строку (только символы 0-9, A-F):  ").strip()
        if not all(c in '0123456789abcdefABCDEF' for c in hex_string.replace(' ', '')):
            print( "[Ошибка] Строка содержит недопустимые символы. Использую тестовую строку. ")
            return  "0123456789ABCDEF " * 4, None
        return hex_string, None

    elif choice == '2':
        filename = input( "Введите имя файла с hex-строкой:  ").strip()
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                hex_string = file.read().strip()
            print(f"\nHex из файла прочитан. Длина: {len(hex_string)} символов ")
            return hex_string, filename
        except FileNotFoundError:
            print(f"[Ошибка] Файл '{filename}' не найден. Использую тестовую строку. ")
            return  "0123456789ABCDEF " * 4, None

    elif choice == '3':
        print( "\nВыберите тестовый вектор: ")
        print( "1. t(fdb97531) = 2a196f34 ")
        print( "2. t(2a196f34) = ebd9f03a ")
        print( "3. t(ebd9f03a) = b039bb3d ")
        print( "4. t(b039bb3d) = 68695433 ")

        vector_choice = input( "Ваш выбор (1-4):  ").strip()
        vectors = {
            '1':  "fdb97531 ",
            '2':  "2a196f34 ",
            '3':  "ebd9f03a ",
            '4':  "b039bb3d "
        }

        if vector_choice in vectors:
            hex_string = vectors[vector_choice]
            print(f"\nВыбран тестовый вектор: {hex_string} ")
            return hex_string, None
        else:
            print( "[Ошибка] Неверный выбор. Использую первый вектор. ")
            return  "fdb97531 ", None

    elif choice == '4':
        crypto = CryptoSystem()
        text = input( "Введите текст для преобразования в hex:  ").strip()
        if not text:
            print( "[Ошибка] Текст не введен. Использую пустую строку. ")
        hex_string = crypto.text_to_hex(text)
        print(f"\nТекст преобразован в hex: {hex_string} ")
        return hex_string, None

    else:
        print( "[Ошибка] Неверный выбор. Использую тестовую строку. ")
        return  "0123456789ABCDEF " * 4, None

def save_to_file(text, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"\nРезультат сохранен в файл {filename}")
    except Exception as e:
        print(f"[Ошибка] при сохранении в файл: {e}")

def main():
    crypto = CryptoSystem()
    test_hex =  "0123456789ABCDEF " * 100
    with open( "test_hex.txt ",  "w", encoding= "utf-8 ") as f:
        f.write(test_hex)

    print( "= " * 60)
    print( "ПРОГРАММА ШИФРОВАНИЯ МНОГОЗНАЧНОЙ ЗАМЕНЫ ")
    print( "= " * 60)

    while True:
        print( "\nВыберите шифр: ")
        print( "1. S-блок замены ГОСТ Р 34.12-2015 (МАГМА) ")
        print( "2. Выход ")

        cipher_choice = input( "Ваш выбор (1-2):  ").strip()

        if cipher_choice == '2':
            print( "Программа завершена. ")
            break

        if cipher_choice == '1':
            print( "\n " +  "= " * 60)
            print( "РЕЖИМ РАБОТЫ С 16-РИЧНЫМИ ДАННЫМИ (МАГМА) ")
            print( "= " * 60)

            hex_input, filename = get_hex_input()
            print(f"\nИсходная hex-строка: {hex_input} ")

            print( "\n " +  "-" * 40)
            print( "ПРЯМОЕ ПРЕОБРАЗОВАНИЕ МАГМА ")
            print( "-" * 40)
            transformed_hex = crypto.magma_encrypt_hex(hex_input)
            print(f"Результат преобразования: {transformed_hex} ")

            if filename:
                base_name = os.path.splitext(filename)[0]
                save_to_file(transformed_hex, f"{base_name}_transformed.txt ")

            print( "\n " +  "-" * 40)
            print( "ОБРАТНОЕ ПРЕОБРАЗОВАНИЕ МАГМА ")
            print( "-" * 40)
            decrypted_hex = crypto.magma_decrypt_hex(transformed_hex)
            print(f"Результат расшифрования: {decrypted_hex} ")

            try:
                decrypted_text = crypto.hex_to_text(decrypted_hex)
                print(f"Расшифрованный текст: {decrypted_text} ")
            except:
                pass

            continue

        else:
            print( "[Ошибка] Неверный выбор шифра ")
            continue

if __name__ == "__main__":
    main()