import sys
import struct

# [КРИПТО] Таблицы подстановки (S-блоки) стандарта ГОСТ МАГМА.
# Каждая из восьми таблиц заменяет 4 бита входного числа по фиксированному правилу.
# Это обеспечивает нелинейную связь между входом и выходом.
PI = [
    [12, 4,  6,  2, 10,  5, 11,  9, 14,  8, 13,  7,  0,  3, 15,  1],
    [ 6,  8,  2,  3,  9, 10,  5, 12,  1, 14,  4,  7, 11, 13,  0, 15],
    [11,  3,  5,  8,  2, 15, 10, 13, 14,  1,  7,  4, 12,  9,  6,  0],
    [12,  8,  2,  1, 13,  4, 15,  6,  7,  0, 10,  5,  3, 14,  9, 11],
    [ 7, 15,  5, 10,  8,  1,  6, 13,  0,  9,  3, 14, 11,  4,  2, 12],
    [ 5, 13, 15,  6,  9,  2, 12, 10, 11,  7,  8,  1,  4,  3, 14,  0],
    [ 8, 14,  2,  5,  6,  9,  1, 12, 15,  4, 11,  0, 13, 10,  3,  7],
    [ 1,  7, 14, 13,  0,  5,  8,  3,  4, 15, 10,  6,  9, 12, 11,  2],
]

def t_transform(x: int) -> int:
    # [КРИПТО] Нелинейное преобразование T. Разбивает 32-битное число на восемь частей по 4 бита
    # и заменяет каждую часть по соответствующей таблице PI.
    result = 0
    # [КРИПТО] Цикл обработки всех восьми 4-битных частей числа.
    for i in range(8):
        # [КРИПТО] Выделяем текущую 4-битную часть, находим её заменённое значение в таблице
        # и собираем обратно в итоговое число, сохраняя позицию.
        part = (x >> (4 * i)) & 0xF
        result |= PI[i][part] << (4 * i)
    return result

def left_shift_11(x: int) -> int:
    # [КРИПТО] Линейное преобразование L. Циклический сдвиг всех 32 битов влево на 11 позиций.
    # Перемешивает биты, чтобы изменение одного входного бита влияло на множество выходных.
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF

def g(k: int, a: int) -> int:
    # [КРИПТО] Раундовая функция G. Складывает полублок данных с раундовым ключом по модулю 2^32,
    # применяет подстановку T и линейный сдвиг L. Это основной шаг каждого раунда шифрования.
    return left_shift_11(t_transform((a + k) & 0xFFFFFFFF))

def key_schedule(key_bytes: bytes) -> list:
    # [КРИПТО] Подготовка ключа. Делит 256-битный ключ на восемь частей по 32 бита
    # и формирует последовательность из 32 ключей для раундов по правилу ГОСТ:
    # ключи K1..K8 повторяются три раза подряд, затем идут в обратном порядке K8..K1.
    K = list(struct.unpack('>8I', key_bytes))
    return K * 3 + K[::-1]

def magma_encrypt_block(block: bytes, round_keys: list) -> bytes:
    # [КРИПТО] Зашифрование одного блока 64 бита. Использует схему Фейстеля:
    # полублоки постоянно меняются местами, один из них проходит через функцию G
    # и складывается по XOR с другим полублоком.
    a1, a0 = struct.unpack('>II', block)
    # [КРИПТО] Цикл выполнения первых 31 раундов шифрования.
    for i in range(31):
        # [КРИПТО] Меняем половины местами. Правую часть пропускаем через G с текущим ключом,
        # результат складываем по XOR с левой частью, которая становится правой в следующем шаге.
        a1, a0 = a0, g(round_keys[i], a0) ^ a1
    # [КРИПТО] Последний 32-й раунд выполняется без перестановки половин, как требует стандарт ГОСТ.
    a1 = g(round_keys[31], a0) ^ a1
    return struct.pack('>II', a1, a0)

def magma_decrypt_block(block: bytes, round_keys: list) -> bytes:
    # [КРИПТО] Расшифрование блока. Алгоритм полностью совпадает с шифрованием,
    # но раундовые ключи подаются в строго обратном порядке.
    return magma_encrypt_block(block, round_keys[::-1])

def ctr_process(data: bytes, key: bytes, iv: bytes) -> bytes:
    # [КРИПТО] Режим гаммирования CTR. Позволяет шифровать данные любой длины блоками,
    # не требуя выравнивания размера. Шифрование и расшифрование выполняются одной функцией.
    round_keys = key_schedule(key)
    # [КРИПТО] Инициализируем счётчик синхропосылкой (IV), преобразуя её в целое число.
    ctr = int.from_bytes(iv, 'big')
    out = bytearray()
    # [КРИПТО] Цикл обработки входных данных порциями по 8 байт (64 бита).
    for i in range(0, len(data), 8):
        # [КРИПТО] Получаем гамму: шифруем текущее значение счётчика алгоритмом МАГМА.
        gamma = magma_encrypt_block(ctr.to_bytes(8, 'big'), round_keys)
        chunk = data[i:i+8]
        # [КРИПТО] Вырезаем часть данных и побайтово складываем её с гаммой по правилу XOR.
        # При шифровании это накладывает гамму, при расшифровании — снимает её.
        out.extend(b ^ gm for b, gm in zip(chunk, gamma))
        # [КРИПТО] Увеличиваем счётчик на 1, чтобы следующий блок получил уникальную гамму.
        ctr = (ctr + 1) & 0xFFFFFFFFFFFFFFFF
    return bytes(out)

def input_hex(prompt: str, byte_len: int) -> bytes:
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) == byte_len * 2:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print(f"  [!] Нужно ровно {byte_len * 2} HEX-символов ({byte_len} байт)")

def input_iv(prompt: str) -> bytes:
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) > 16:
            print("  [!] IV должен быть не более 16 HEX-символов (8 байт)")
            continue
        if len(raw) % 2 != 0:
            print("  [!] IV должен содержать чётное число HEX-символов")
            continue
        raw = raw.ljust(16, '0')
        try:
            return bytes.fromhex(raw)
        except ValueError:
            print("  [!] Некорректный HEX")

def input_hex_any(prompt: str) -> bytes:
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) % 2 == 0 and len(raw) > 0:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print("  [!] Введите корректную HEX-строку чётной длины")

def print_hex(label: str, data: bytes, bsize: int = 8):
    blocks = ' '.join(data[i:i+bsize].hex().upper()
                      for i in range(0, len(data), bsize))
    print(f"  {label}: {blocks}")

def encrypt_menu():
    print("\n--- ШИФРОВАНИЕ (CTR) ---\n")
    key = input_hex("Ключ (32 байта, 64 HEX-символа) : ", 32)
    iv  = input_iv("Синхропосылка  (до 16 HEX-символов): ")
    data = input_hex_any("Открытый текст (HEX): ")
    ciphertext = ctr_process(data, key, iv)
    print()
    print_hex("Открытый текст", data)
    print_hex("Шифртекст ", ciphertext)

def decrypt_menu():
    print("\n--- РАСШИФРОВАНИЕ (CTR) ---\n")
    key = input_hex("Ключ (32 байта, 64 HEX-символа) : ", 32)
    iv  = input_iv("Синхропосылка (до 16 HEX-символов): ")
    data = input_hex_any("Шифртекст (HEX): ")
    plaintext = ctr_process(data, key, iv)
    print()
    print_hex("Шифртекст ", data)
    print_hex("Открытый текст" , plaintext)

if __name__ == "__main__":
    print("=" * 60)
    print("ГАММИРОВАНИЕ CTR (ГОСТ Р 34.13-2015) на основе МАГМЫ")
    print("Блочный шифр ГОСТ Р 34.12-2015, ключ 256 бит, блок 64 бита")
    print("=" * 60)
    while True:
        print("\n" + "─" * 40)
        print("МЕНЮ: ")
        print("  1. Зашифровать ")
        print("  2. Расшифровать ")
        print("  0. Выход ")
        print("─" * 40)

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("До свидания! ")
            sys.exit()
        elif choice == "1":
            encrypt_menu()
        elif choice == "2":
            decrypt_menu()
        else:
            print("  [!] Неверный выбор! ")