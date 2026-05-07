import sys
import struct

# =====================================================================
#   S-блоки ГОСТ Р 34.12-2015 (МАГМА) – раздел 5.1.1
# =====================================================================
PI = [
    [12, 4,  6,  2, 10,  5, 11,  9, 14,  8, 13,  7,  0,  3, 15,  1],  # π0
    [ 6,  8,  2,  3,  9, 10,  5, 12,  1, 14,  4,  7, 11, 13,  0, 15],  # π1
    [11,  3,  5,  8,  2, 15, 10, 13, 14,  1,  7,  4, 12,  9,  6,  0],  # π2
    [12,  8,  2,  1, 13,  4, 15,  6,  7,  0, 10,  5,  3, 14,  9, 11],  # π3
    [ 7, 15,  5, 10,  8,  1,  6, 13,  0,  9,  3, 14, 11,  4,  2, 12],  # π4
    [ 5, 13, 15,  6,  9,  2, 12, 10, 11,  7,  8,  1,  4,  3, 14,  0],  # π5
    [ 8, 14,  2,  5,  6,  9,  1, 12, 15,  4, 11,  0, 13, 10,  3,  7],  # π6
    [ 1,  7, 14, 13,  0,  5,  8,  3,  4, 15, 10,  6,  9, 12, 11,  2],  # π7
]

# =====================================================================
#   Базовые преобразования МАГМЫ
# =====================================================================

def t_transform(x: int) -> int:
    """
    Нелинейное биективное преобразование t: V32 → V32.
    Разбивает 32-битное число на 8 полубайт (4 бита) и заменяет каждый
    соответствующим значением из S-блока (π0 для младшего полубайта,
    π7 для старшего). (Формула 14 ГОСТ)
    """
    result = 0
    for i in range(8):          # i = 0 – младший полубайт
        nibble = (x >> (4 * i)) & 0xF
        result |= PI[i][nibble] << (4 * i)
    return result

def left_shift_11(x: int) -> int:
    """Циклический сдвиг 32-битного числа влево на 11 бит."""
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF

def g(k: int, a: int) -> int:
    """
    Функция g[k] (формула 15 ГОСТ):
    g[k](a) = (t((a + k) mod 2^32)) <<< 11
    """
    return left_shift_11(t_transform((a + k) & 0xFFFFFFFF))

# =====================================================================
#   Развертывание ключа (Key Schedule) – раздел 5.3 ГОСТ
# =====================================================================

def key_schedule(key_bytes: bytes) -> list:
    """
    Из 256-битного ключа формирует 32 итерационных подключа.
    K1..K8 – первые 8 слов (big-endian).
    Раунды 1-24: K1..K8, K1..K8, K1..K8 (трижды)
    Раунды 25-32: K8, K7, ..., K1 (обратный порядок)
    """
    K = list(struct.unpack('>8I', key_bytes))   # K1..K8
    return K * 3 + K[::-1]                       # всего 32 ключа

# =====================================================================
#   Базовый блочный шифр МАГМА (раздел 5.4)
# =====================================================================

def magma_encrypt_block(block: bytes, round_keys: list) -> bytes:
    """
    Зашифрование одного 64-битного блока (8 байт).
    Используется 32 раунда:
      - раунды 1..31: G[k](a1,a0) = (a0, g[k](a0) ⊕ a1)
      - раунд 32:     G*[k](a1,a0) = (g[k](a0) ⊕ a1) || a0 (без перестановки)
    """
    a1, a0 = struct.unpack('>II', block)   # a = a1 || a0 (big-endian)

    for i in range(31):                    # раунды 1..31
        a1, a0 = a0, g(round_keys[i], a0) ^ a1

    a1 = g(round_keys[31], a0) ^ a1        # раунд 32
    return struct.pack('>II', a1, a0)

def magma_decrypt_block(block: bytes, round_keys: list) -> bytes:
    """
    Расшифрование одного блока – зашифрование с ключами в обратном порядке.
    """
    return magma_encrypt_block(block, round_keys[::-1])

# =====================================================================
#   Режим гаммирования CTR (ГОСТ Р 34.13-2015)
# =====================================================================

def ctr_process(data: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Гаммирование CTR – шифрование и расшифрование идентичны.
    data : входные байты (открытый или шифрованный текст)
    key  : 32 байта (256 бит)
    iv   : синхропосылка 8 байт (64 бита) – начальное значение счётчика
    Возвращает результат той же длины.
    """
    round_keys = key_schedule(key)
    ctr = int.from_bytes(iv, 'big')          # счётчик (64 бита)
    out = bytearray()

    for i in range(0, len(data), 8):
        # Шифрование текущего значения счётчика
        gamma = magma_encrypt_block(ctr.to_bytes(8, 'big'), round_keys)
        chunk = data[i:i+8]
        # XOR гаммы с блоком данных
        out.extend(b ^ gm for b, gm in zip(chunk, gamma))
        ctr = (ctr + 1) & 0xFFFFFFFFFFFFFFFF   # инкремент по модулю 2^64

    return bytes(out)

# =====================================================================
#   Вспомогательные функции для ввода/вывода HEX
# =====================================================================

def input_hex(prompt: str, byte_len: int) -> bytes:
    """Запрашивает HEX-строку фиксированной длины и возвращает байты."""
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) == byte_len * 2:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print(f"  [!] Нужно ровно {byte_len * 2} HEX-символов ({byte_len} байт)")

def input_hex_any(prompt: str) -> bytes:
    """Запрашивает HEX-строку любой чётной длины."""
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) % 2 == 0 and len(raw) > 0:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print("  [!] Введите корректную HEX-строку чётной длины")

def print_hex(label: str, data: bytes, bsize: int = 8):
    """Выводит HEX-данные, разбивая на блоки заданного размера."""
    blocks = ' '.join(data[i:i+bsize].hex().upper()
                      for i in range(0, len(data), bsize))
    print(f"  {label}: {blocks}")

# =====================================================================
#   Контрольный пример из ГОСТ (Приложение А.2)
# =====================================================================

def run_self_test():
    """Запускает контрольный пример из стандарта."""
    print("\n" + "=" * 62)
    print("  КОНТРОЛЬНЫЙ ПРИМЕР (ГОСТ Р 34.12-2015, Приложение А.2)")
    print("=" * 62)

    # Ключ (256 бит) из раздела А.2.3
    key_hex = ("ffeeddccbbaa9988"
               "7766554433221100"
               "f0f1f2f3f4f5f6f7"
               "f8f9fafbfcfdfeff")
    pt_hex = "fedcba9876543210"
    ct_expected = "4ee901e5c2d8ca3d"

    key = bytes.fromhex(key_hex)
    pt = bytes.fromhex(pt_hex)
    round_keys = key_schedule(key)

    ct = magma_encrypt_block(pt, round_keys)
    dec = magma_decrypt_block(ct, round_keys)

    print(f"  Ключ          : {key.hex()}")
    print(f"  Открытый текст: {pt_hex}")
    print(f"  Ожидается     : {ct_expected}")
    print(f"  Получено      : {ct.hex()}")
    print(f"  Шифр          : {'✓  ПРОЙДЕН' if ct.hex() == ct_expected else '✗  ОШИБКА'}")
    print(f"  Расшифровано  : {dec.hex()}")
    print(f"  Расшифровка   : {'✓  ВЕРНО'   if dec == pt else '✗  ОШИБКА'}")

    # Демонстрация CTR
    print()
    print("  --- Демонстрация CTR-режима ---")
    iv = bytes.fromhex("1234567890abcdef")
    message = bytes.fromhex("fedcba9876543210" * 2)   # 16 байт

    encrypted = ctr_process(message, key, iv)
    decrypted = ctr_process(encrypted, key, iv)

    print_hex("  Открытый текст", message)
    print_hex("  Шифртекст     ", encrypted)
    print_hex("  Расшифровано  ", decrypted)
    print(f"  Расшифровка CTR: {'✓  ВЕРНО' if decrypted == message else '✗  ОШИБКА'}")
    print()

# =====================================================================
#   Меню для работы с гаммированием
# =====================================================================

def gamma_menu():
    """Интерактивное гаммирование (шифрование/расшифрование) в CTR."""
    print("\n--- Гаммирование CTR (ГОСТ Р 34.13-2015 / МАГМА) ---\n")

    key = input_hex("Ключ           (32 байта, 64 HEX-символа) : ", 32)
    iv  = input_hex("Синхропосылка  ( 8 байт,  16 HEX-символов): ",  8)

    print("\n  1. Зашифровать")
    print("  2. Расшифровать")
    op = input("  Действие: ").strip()

    if op not in ("1", "2"):
        print("  [!] Неверный выбор")
        return

    data = input_hex_any("Данные (HEX): ")
    result = ctr_process(data, key, iv)

    print()
    if op == "1":
        print_hex("Открытый текст", data)
        print_hex("Шифртекст     ", result)
    else:
        print_hex("Шифртекст     ", data)
        print_hex("Открытый текст", result)

# =====================================================================
#   Главное меню
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ГАММИРОВАНИЕ CTR (ГОСТ Р 34.13-2015) на основе МАГМЫ")
    print("Блочный шифр ГОСТ Р 34.12-2015, ключ 256 бит, блок 64 бита")
    print("=" * 60)

    run_self_test()

    while True:
        print("╔" + "═" * 58 + "╗")
        print("║  МЕНЮ                                                  ║")
        print("╠" + "═" * 58 + "╣")
        print("║  1. Зашифровать / Расшифровать (CTR)                  ║")
        print("║  2. Контрольный пример (повтор)                       ║")
        print("║  0. Выход                                              ║")
        print("╚" + "═" * 58 + "╝")

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("До свидания!")
            sys.exit()
        elif choice == "1":
            gamma_menu()
        elif choice == "2":
            run_self_test()
        else:
            print("  [!] Неверный выбор!\n")
