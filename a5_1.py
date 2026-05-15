import hashlib
import os

ALPHABET = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м',
            'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ',
            'ы', 'ь', 'э', 'ю', 'я']
PUNCT_WORDS = ['тире','тчк', 'зпт', 'впр', 'вск', 'двтч', 'тчзпт', 'тире', 'скоб', 'скобз', 'квч', 'апстр', 'прб']
PUNCT_SYMBOLS = ['—', '.', ',', '?', '!', ':', ';', '-', '(', ')', '"', "'", ' ']
PUNCT_WORD_TO_SYMBOL = dict(zip(PUNCT_WORDS, PUNCT_SYMBOLS))
PUNCT_SYMBOL_TO_WORD = dict(zip(PUNCT_SYMBOLS, PUNCT_WORDS))
CHAR_TO_CODE = {char: i for i, char in enumerate(ALPHABET)}
CODE_TO_CHAR = {i: char for i, char in enumerate(ALPHABET)}
OUTPUT_DIR = "все шифры"

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

class A5_1:
    def __init__(self):
        # [КРИПТО] Длина первого регистра сдвига (19 бит)
        self.R1_LENGTH = 19
        # [КРИПТО] Длина второго регистра сдвига (22 бита)
        self.R2_LENGTH = 22
        # [КРИПТО] Длина третьего регистра сдвига (23 бита)
        self.R3_LENGTH = 23
        # [КРИПТО] Позиция тактового бита в первом регистре
        self.R1_CLOCK_BIT = 8
        # [КРИПТО] Позиция тактового бита во втором регистре
        self.R2_CLOCK_BIT = 10
        # [КРИПТО] Позиция тактового бита в третьем регистре
        self.R3_CLOCK_BIT = 10
        # [КРИПТО] Позиции битов, используемых для вычисления обратного связи в первом регистре
        self.R1_FEEDBACK_TAPS = [18, 17, 16, 13]
        # [КРИПТО] Позиции битов для обратного связи во втором регистре
        self.R2_FEEDBACK_TAPS = [21, 20]
        # [КРИПТО] Позиции битов для обратного связи в третьем регистре
        self.R3_FEEDBACK_TAPS = [22, 21, 20, 7]
        # [КРИПТО] Инициализация трёх регистров нулями
        self.R1 = [0] * self.R1_LENGTH
        self.R2 = [0] * self.R2_LENGTH
        self.R3 = [0] * self.R3_LENGTH

    def _clock_registers(self, r1_in=0, r2_in=0, r3_in=0):
        # [КРИПТО] Вычисление нового бита для первого регистра: складываем входной бит с битами по заданным позициям
        r1_feedback = r1_in
        for tap in self.R1_FEEDBACK_TAPS:
            r1_feedback ^= self.R1[tap]
        # [КРИПТО] Вычисление нового бита для второго регистра
        r2_feedback = r2_in
        for tap in self.R2_FEEDBACK_TAPS:
            r2_feedback ^= self.R2[tap]
        # [КРИПТО] Вычисление нового бита для третьего регистра
        r3_feedback = r3_in
        for tap in self.R3_FEEDBACK_TAPS:
            r3_feedback ^= self.R3[tap]
        # [КРИПТО] Сдвиг всех регистров вправо: новый бит вставляется в начало, остальные перемещаются
        self.R1 = [r1_feedback] + self.R1[:-1]
        self.R2 = [r2_feedback] + self.R2[:-1]
        self.R3 = [r3_feedback] + self.R3[:-1]

    def _majority(self, x, y, z):
        # [КРИПТО] Функция большинства: возвращает 1, если два или три входных бита равны 1.
        # Используется для решения, какие регистры будут сдвигаться на текущем такте.
        return 1 if (x + y + z) >= 2 else 0

    def _clock_controlled(self):
        # [КРИПТО] Считываем тактовые биты из заданных позиций каждого регистра
        r1_clock = self.R1[self.R1_CLOCK_BIT]
        r2_clock = self.R2[self.R2_CLOCK_BIT]
        r3_clock = self.R3[self.R3_CLOCK_BIT]
        # [КРИПТО] Определяем значение большинства
        maj = self._majority(r1_clock, r2_clock, r3_clock)
        # [КРИПТО] Сдвигаем первый регистр только если его тактовый бит совпадает с большинством
        if r1_clock == maj:
            r1_feedback = 0
            for tap in self.R1_FEEDBACK_TAPS:
                r1_feedback ^= self.R1[tap]
            self.R1 = [r1_feedback] + self.R1[:-1]
        # [КРИПТО] Сдвигаем второй регистр по тому же правилу
        if r2_clock == maj:
            r2_feedback = 0
            for tap in self.R2_FEEDBACK_TAPS:
                r2_feedback ^= self.R2[tap]
            self.R2 = [r2_feedback] + self.R2[:-1]
        # [КРИПТО] Сдвигаем третий регистр по тому же правилу
        if r3_clock == maj:
            r3_feedback = 0
            for tap in self.R3_FEEDBACK_TAPS:
                r3_feedback ^= self.R3[tap]
            self.R3 = [r3_feedback] + self.R3[:-1]

    def initialize(self, key, frame_number):
        # [КРИПТО] Сброс регистров в начальное состояние
        self.R1 = [0] * self.R1_LENGTH
        self.R2 = [0] * self.R2_LENGTH
        self.R3 = [0] * self.R3_LENGTH
        # [КРИПТО] Цикл загрузки 64-битного ключа: подаём биты ключа на вход регистров и сдвигаем их
        for i in range(64):
            keybit = key[i]
            self._clock_registers(keybit, keybit, keybit)
        # [КРИПТО] Цикл загрузки 22-битного номера кадра: подаём биты кадра и сдвигаем регистры
        for i in range(22):
            framebit = frame_number[i]
            self._clock_registers(framebit, framebit, framebit)
        # [КРИПТО] 100 холостых тактов с управляемым сдвигом для полного перемешивания состояния перед генерацией
        for _ in range(100):
            self._clock_controlled()

    def generate_keystream(self, length):
        keystream = []
        # [КРИПТО] Цикл генерации гаммы нужной длины
        for _ in range(length):
            # [КРИПТО] Бит гаммы: сумма по модулю 2 последних битов трёх регистров
            output_bit = self.R1[-1] ^ self.R2[-1] ^ self.R3[-1]
            keystream.append(output_bit)
            # [КРИПТО] Сдвигаем регистры по правилу большинства для подготовки к следующему такту
            self._clock_controlled()
        return keystream

    def encrypt(self, plaintext, key, frame_number):
        # [КРИПТО] Инициализация генератора ключом и кадром
        self.initialize(key, frame_number)
        # [КРИПТО] Генерация гаммы той же длины, что и открытый текст
        keystream = self.generate_keystream(len(plaintext))
        # [КРИПТО] Побитовое сложение открытого текста с гаммой по правилу XOR
        ciphertext = [plaintext[i] ^ keystream[i] for i in range(len(plaintext))]
        return ciphertext, keystream

    def decrypt(self, ciphertext, key, frame_number):
        # [КРИПТО] Расшифрование идентично шифрованию: XOR шифртекста с той же гаммой восстанавливает исходные биты
        return self.encrypt(ciphertext, key, frame_number)

def password_to_key(password: str) -> list[int]:
    hash_bytes = hashlib.sha256(password.encode("utf-8")).digest()
    key_bits = []
    # [КРИПТО] Преобразование пароля в 64-битный ключ: берём первые 8 байт хеша, каждый разбиваем на 8 бит
    for byte in hash_bytes[:8]:
        key_bits.extend(int(b) for b in format(byte, "08b"))
    return key_bits

def format_key_bits(key_bits):
    result = ""
    # [КРИПТО] Форматирование битов ключа в читаемый вид (байты через пробел)
    for i in range(0, len(key_bits), 8):
        if i + 8 <= len(key_bits):
            byte = key_bits[i:i+8]
            byte_str = ''.join(map(str, byte))
            result += byte_str + " "
    return result.strip()

def frame_to_bits(frame_str: str) -> list[int]:
    return [int(bit) for bit in frame_str]

def text_to_punct_words(text):
    result = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in PUNCT_SYMBOL_TO_WORD:
            result.append(PUNCT_SYMBOL_TO_WORD[char])
        else:
            result.append(char)
        i += 1
    return ''.join(result)

def punct_words_to_text(text_with_punct):
    result = []
    i = 0
    text_lower = text_with_punct.lower()
    while i < len(text_lower):
        matched = False
        for punct_word in sorted(PUNCT_WORDS, key=len, reverse=True):
            if text_lower[i:].startswith(punct_word):
                result.append(PUNCT_WORD_TO_SYMBOL[punct_word])
                i += len(punct_word)
                matched = True
                break
        if not matched:
            result.append(text_with_punct[i])
            i += 1
    return ''.join(result)

def text_to_5bit_codes(text):
    text_with_punct_words = text_to_punct_words(text)
    text_lower = text_with_punct_words.lower()
    codes = []
    processed_chars = []
    # [КРИПТО] Цикл кодирования текста: каждая буква превращается в 5-битный код (от 0 до 31)
    for char in text_lower:
        if char in CHAR_TO_CODE:
            codes.append(CHAR_TO_CODE[char])
            processed_chars.append(char)
        else:
            codes.append(0)
            processed_chars.append('а')
    processed_text = ''.join(processed_chars)
    return codes, processed_text, text_with_punct_words

def codes_to_text(codes):
    chars = []
    # [КРИПТО] Цикл обратного преобразования: 5-битные коды возвращаются в буквы
    for code in codes:
        if 0 <= code < len(ALPHABET):
            chars.append(ALPHABET[code])
        else:
            chars.append('а')
    text_with_punct_words = ''.join(chars)
    final_text = punct_words_to_text(text_with_punct_words)
    return final_text

def codes_to_bits(codes):
    bits = []
    # [КРИПТО] Цикл разбивки 5-битных кодов на отдельные биты для поточного шифрования
    for code in codes:
        bits.extend(int(b) for b in format(code, '05b'))
    return bits

def bits_to_codes(bits):
    codes = []
    # [КРИПТО] Цикл сборки битов обратно в 5-битные коды
    for i in range(0, len(bits), 5):
        if i + 5 <= len(bits):
            code_bits = bits[i:i+5]
            code = int(''.join(map(str, code_bits)), 2)
            codes.append(code)
    return codes

def get_file_path(filename):
    ensure_output_dir()
    return os.path.join(OUTPUT_DIR, filename)

def save_to_file(filename, content):
    filepath = get_file_path(filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

def load_from_file(filename):
    filepath = get_file_path(filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def print_progress(current, total, prefix="Прогресс"):
    if total > 1000:
        percent = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print(f'\r{prefix}: |{bar}| {percent:.1f}% ({current}/{total})', end='', flush=True)
        if current == total:
            print()

def verify_decryption(original_text, decrypted_text):
    if original_text and decrypted_text:
        if original_text == decrypted_text:
            print("\n РАСШИФРОВКА УСПЕШНА!")
            return True
        else:
            print("\n РАСШИФРОВКА НЕ УДАЛАСЬ")
            min_len = min(len(original_text), len(decrypted_text))
            for i in range(min_len):
                if original_text[i] != decrypted_text[i]:
                    print(f"Первое несовпадение на позиции {i}:")
                    start = max(0, i-20)
                    end = min(len(original_text), i+20)
                    print(f"Оригинал: {original_text[start:end]}")
                    print(f"Расшифр: {decrypted_text[start:end]}")
                    break
            return False
    return False

def main():
    ensure_output_dir()
    original_text = None
    print("=" * 60)
    print("A5/1 (5 бит на символ) ")
    print("=" * 60)

    while True:
        print("\n " + "─" * 40)
        print("МЕНЮ: ")
        print("1. Зашифровать текст ")
        print("2. Расшифровать текст ")
        print("3. Показать список файлов ")
        print("0. Выход ")
        print("─" * 40)

        choice = input("Ваш выбор: ")

        if choice == "0":
            print("\nДо свидания! ")
            print("=" * 60)
            break
            
        elif choice == "3":
            print(f"\nФайлы в директории {OUTPUT_DIR}: ")
            try:
                files = os.listdir(OUTPUT_DIR)
                if files:
                    for file in sorted(files):
                        filepath = os.path.join(OUTPUT_DIR, file)
                        size = os.path.getsize(filepath)
                        print(f"   - {file} ({size} байт) ")
                else:
                    print("   Директория пуста ")
            except FileNotFoundError:
                print("   Директория не найдена ")
            continue

        password = input("\nВведите пароль (строка): ")
        frame_str = input("Введите номер кадра (22 бита): ")

        if len(frame_str) != 22 or not all(bit in '01' for bit in frame_str):
            print(" Номер кадра должен содержать 22 бита (только 0 и 1)! ")
            continue

        key_bits = password_to_key(password)
        frame_bits = frame_to_bits(frame_str)
        
        print(f"\nКлюч (64 бита): {format_key_bits(key_bits)} ")
        print(f"Номер кадра: {frame_str} ")

        cipher = A5_1()

        if choice == "1":
            print("\n " + "-" * 40)
            print("ШИФРОВАНИЕ ТЕКСТА ")
            print("-" * 40)
            print("Введите открытый текст (для завершения введите пустую строку): ")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            text = '\n'.join(lines)
            
            if not text:
                print(" Текст не введен ")
                continue
            
            original_text = text
            
            print(f"\nОбработка текста длиной {len(text)} символов... ")
            
            print("\nПример преобразования знаков препинания: ")
            example_text = text[:100] + "..." if len(text) > 100 else text
            example_converted = text_to_punct_words(example_text)
            print(f"   Исходный: {example_text} ")
            print(f"   После замены: {example_converted} ")
            
            codes, processed_text, text_with_punct = text_to_5bit_codes(text)
            chars_count = len(codes)
            print(f"\nКоличество символов после обработки: {chars_count} ")
            
            bits = codes_to_bits(codes)
            bits_count = len(bits)
            print(f"Всего бит для шифрования: {bits_count} ")
            
            print("\nПроцесс шифрования... ")
            cipher.initialize(key_bits, frame_bits)
            
            chunk_size = 10000
            cipher_bits = []
            
            # [КРИПТО] Цикл поблочного шифрования: данные обрабатываются кусками по 10000 бит
            for i in range(0, bits_count, chunk_size):
                end = min(i + chunk_size, bits_count)
                chunk_plain = bits[i:end]
                # [КРИПТО] Генерация гаммы нужной длины для текущего куска данных
                chunk_keystream = cipher.generate_keystream(len(chunk_plain))
                # [КРИПТО] Побитовое сложение открытого текста с гаммой через XOR
                chunk_cipher = [chunk_plain[j] ^ chunk_keystream[j] for j in range(len(chunk_plain))]
                cipher_bits.extend(chunk_cipher)
                print_progress(end, bits_count, "Шифрование ")
            
            cipher_text = " ".join(map(str, cipher_bits))
            cipher_file = save_to_file("cipher_text_A5_1.txt", cipher_text)

            info_content = f"""=== ИНФОРМАЦИЯ О ШИФРОВАНИИ ===
Пароль: {password}
Ключ (64 бита): {format_key_bits(key_bits)}
Номер кадра: {frame_str}
Количество символов: {chars_count}
Количество бит: {bits_count}
ИСХОДНЫЙ ТЕКСТ:
{text}
ТЕКСТ СО ВСТАВЛЕННЫМИ СЛОВАМИ-ЗНАКАМИ:
{text_with_punct}
5-БИТНЫЕ КОДЫ:
{codes}
"""
            info_file = save_to_file("cipher_info.txt", info_content)
            print(f"\n Шифротекст сохранён: {cipher_file} ")
            print(f" Информация сохранена: {info_file} ")

        elif choice == "2":
            print("\n " + "-" * 40)
            print("РАСШИФРОВАНИЕ ТЕКСТА ")
            print("-" * 40)
            
            filename = input("Введите имя файла с шифротекстом: ")
            
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            try:
                cipher_text = load_from_file(filename)
                cipher_bits = [int(bit) for bit in cipher_text.strip() if bit in '01']
                bits_count = len(cipher_bits)
                print(f"Загружено {bits_count} бит из файла: {filename} ")
                
            except FileNotFoundError:
                print(f" Файл {filename} не найден ")
                continue
            except ValueError as e:
                print(f" Ошибка чтения файла: {e} ")
                continue

            print("\nПроцесс расшифровки... ")
            cipher.initialize(key_bits, frame_bits)
            
            chunk_size = 10000
            plain_bits = []
            
            # [КРИПТО] Цикл поблочного расшифрования: идентичен шифрованию благодаря свойству XOR
            for i in range(0, bits_count, chunk_size):
                end = min(i + chunk_size, bits_count)
                chunk_cipher = cipher_bits[i:end]
                # [КРИПТО] Генерация идентичной гаммы для текущего куска шифртекста
                chunk_keystream = cipher.generate_keystream(len(chunk_cipher))
                # [КРИПТО] Снятие гаммы с шифртекста через XOR, получение исходных битов
                chunk_plain = [chunk_cipher[j] ^ chunk_keystream[j] for j in range(len(chunk_cipher))]
                plain_bits.extend(chunk_plain)
                print_progress(end, bits_count, "Расшифровка ")

            codes = bits_to_codes(plain_bits)
            print(f"\nВосстановлено кодов: {len(codes)} ")
            
            text_with_punct = codes_to_text(codes)

            decrypted_file = save_to_file("decrypted_text_A5_1.txt", text_with_punct)
            
            info_content = f"""=== ИНФОРМАЦИЯ О РАСШИФРОВАНИИ ===
Пароль: {password}
Ключ (64 бита): {format_key_bits(key_bits)}
Номер кадра: {frame_str}
Исходный файл: {filename}
Количество бит: {bits_count}
Количество символов: {len(codes)}
5-битные коды: {codes}
РАСШИФРОВАННЫЙ ТЕКСТ:
{text_with_punct}
"""
            info_file = save_to_file("decrypt_info.txt", info_content)
            print(f"\n Расшифрованный текст сохранён: {decrypted_file} ")
            print(f" Информация сохранена: {info_file} ")
            
            print("\n " + "-" * 40)
            print("ИТОГОВЫЙ РАСШИФРОВАННЫЙ ТЕКСТ ")
            print("-" * 40)
            print(text_with_punct[:500] + ("..." if len(text_with_punct) > 500 else ""))
            print("-" * 40)
            
            if original_text:
                verify_decryption(original_text, text_with_punct)

if __name__ == "__main__":
    main()