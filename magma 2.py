import sys

# ══════════════════════════════════════════════════════════════
# МАГМА — ГОСТ Р 34.12-2015 (блочный шифр, 64 бит, 256 бит ключ)
# ══════════════════════════════════════════════════════════════

# Нелинейная подстановка π (раздел 5.1.1 ГОСТ)
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


def t(a: int) -> int:
    """Нелинейное биективное преобразование t: V32 → V32 (формула 14 ГОСТ)"""
    result = 0
    for i in range(8):
        nibble = (a >> (4 * i)) & 0xF
        result |= PI[i][nibble] << (4 * i)
    return result


def rot11(x: int) -> int:
    """Циклический сдвиг 32-битного числа влево на 11 бит"""
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF


def g(k: int, a: int) -> int:
    """Функция g[k](a) = rot11(t((a + k) mod 2^32)) (формула 15 ГОСТ)"""
    return rot11(t((a + k) & 0xFFFFFFFF))


def key_schedule(key_bytes: bytes) -> list:
    """Расписание ключей: из 256-битного ключа формирует 32 итерационных подключа"""
    k = [int.from_bytes(key_bytes[4*i:4*i+4], 'big') for i in range(8)]
    return k * 3 + k[::-1]


def encrypt_block(blk: bytes, rk: list) -> bytes:
    """Зашифрование одного 64-битного блока (32 раунда)"""
    a1 = int.from_bytes(blk[:4], 'big')
    a0 = int.from_bytes(blk[4:], 'big')
    for i in range(31):
        a1, a0 = a0, a1 ^ g(rk[i], a0)
    a1 = a1 ^ g(rk[31], a0)
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')


def decrypt_block(blk: bytes, rk: list) -> bytes:
    """Расшифрование одного 64-битного блока (обратный порядок раундов)"""
    a1 = int.from_bytes(blk[:4], 'big')
    a0 = int.from_bytes(blk[4:], 'big')
    a1 = a1 ^ g(rk[31], a0)
    for i in range(30, -1, -1):
        a1, a0 = a0 ^ g(rk[i], a1), a1
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')


def pad( bytes) -> bytes:
    """Дополнение по стандарту (простой PKCS#7-подобный)"""
    n = 8 - len(data) % 8
    return data + bytes([n] * n)


def unpad( bytes) -> bytes:
    """Удаление дополнения"""
    return data[:-data[-1]]


def encrypt_ecb( bytes, key_bytes: bytes, use_padding: bool = True) -> bytes:
    """Шифрование в режиме ECB"""
    rk = key_schedule(key_bytes)
    if use_padding:
        data = pad(data)
    elif len(data) % 8 != 0:
        raise ValueError("Длина данных должна быть кратна 8 байтам")
    return b''.join(encrypt_block(data[i:i+8], rk) for i in range(0, len(data), 8))


def decrypt_ecb( bytes, key_bytes: bytes, use_padding: bool = True) -> bytes:
    """Расшифрование в режиме ECB"""
    rk = key_schedule(key_bytes)
    if len(data) % 8 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 8 байтам")
    dec = b''.join(decrypt_block(data[i:i+8], rk) for i in range(0, len(data), 8))
    return unpad(dec) if use_padding else dec


def input_hex(prompt: str, required_length: int = None) -> str:
    """Безопасный ввод HEX-строки"""
    while True:
        try:
            s = input(prompt).strip().replace(' ', '')
            if s.startswith('0x') or s.startswith('0X'):
                s = s[2:]
            if required_length is not None and len(s) != required_length:
                print(f"[Ошибка] Должно быть ровно {required_length} hex-символов")
                continue
            return s
        except ValueError:
            print("[Ошибка] Введите корректную HEX-строку")


def run_test():
    """Запуск контрольного примера из ГОСТ Р 34.12-2015, Приложение А.2"""
    print("\n" + "=" * 60)
    print("ТЕСТ — ГОСТ Р 34.12-2015, Приложение А.2")
    print("=" * 60)

    KEY = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    PLAIN = bytes.fromhex("fedcba9876543210")
    EXPECTED = "4ee901e5c2d8ca3d"

    rk = key_schedule(KEY)
    enc = encrypt_block(PLAIN, rk)
    dec = decrypt_block(enc, rk)

    print(f"\n[Инфо] Проверка шифрования блока")
    print("-" * 40)
    print(f"  Открытый текст: {PLAIN.hex()}")
    print(f"  Ожидается     : {EXPECTED}")
    print(f"  Получено      : {enc.hex()}")
    enc_ok = enc.hex() == EXPECTED
    print(f"  Результат     : {'[Успех] ВЕРНО' if enc_ok else '[Ошибка] НЕВЕРНО'}")

    print(f"\n[Инфо] Проверка расшифрования")
    print("-" * 40)
    print(f"  Шифртекст: {enc.hex()}")
    print(f"  Получено : {dec.hex()}")
    dec_ok = dec == PLAIN
    print(f"  Результат: {'[Успех] ВЕРНО' if dec_ok else '[Ошибка] НЕВЕРНО'}")

    print(f"\n[Инфо] Преобразование t (А.2.1)")
    print("-" * 40)
    t_tests = [
        (0xfdb97531, 0x2a196f34),
        (0x2a196f34, 0xebd9f03a),
        (0xebd9f03a, 0xb039bb3d),
        (0xb039bb3d, 0x68695433)
    ]
    for inp, exp in t_tests:
        res = t(inp)
        status = "[Успех]" if res == exp else "[Ошибка]"
        print(f"  t({inp:08x}) = {res:08x}  (ожид {exp:08x})  {status}")

    print(f"\n[Инфо] Преобразование g (А.2.2)")
    print("-" * 40)
    g_tests = [
        (0x87654321, 0xfedcba98, 0xfdcbc20c),
        (0xfdcbc20c, 0x87654321, 0x7e791a4b),
        (0x7e791a4b, 0xfdcbc20c, 0xc76549ec),
        (0xc76549ec, 0x7e791a4b, 0x9791c849)
    ]
    for kv, av, exp in g_tests:
        res = g(kv, av)
        status = "[Успех]" if res == exp else "[Ошибка]"
        print(f"  g[{kv:08x}]({av:08x}) = {res:08x}  (ожид {exp:08x})  {status}")

    print(f"\n[Инфо] Тест на тексте >1000 байт")
    print("-" * 40)
    txt = (b"Magma GOST cipher test. Block=64bit Key=256bit. " * 25)
    enc2 = encrypt_ecb(txt, KEY, use_padding=True)
    dec2 = decrypt_ecb(enc2, KEY, use_padding=True)
    ecb_ok = dec2 == txt
    print(f"  Длина текста    : {len(txt)} байт")
    print(f"  Зашифровано     : {len(enc2)} байт")
    print(f"  Результат       : {'[Успех] Совпадает' if ecb_ok else '[Ошибка] Не совпадает'}")

    print("\n" + "=" * 60)
    if enc_ok and dec_ok and ecb_ok:
        print("[Успех] Все тесты ГОСТ пройдены!")
    else:
        print("[Внимание] Некоторые тесты не пройдены")
    print("=" * 60)


def encrypt_text_mode():
    """Режим шифрования текста (UTF-8)"""
    print("\n" + "-" * 60)
    print("ШИФРОВАНИЕ ТЕКСТА (UTF-8)")
    print("-" * 60)

    kh = input("Ключ (64 hex, Enter=тестовый): ").strip()
    if not kh:
        kh = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
        print("[Инфо] Используется тестовый ключ")

    try:
        key = bytes.fromhex(kh)
        txt = input("Текст: ").encode('utf-8')
        enc = encrypt_ecb(txt, key, use_padding=True)

        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТ ШИФРОВАНИЯ")
        print("=" * 60)
        print(f"Шифртекст (hex): {enc.hex()}")
        print("=" * 60)

        save = input("Сохранить в файл? (д/н): ").strip().lower()
        if save in ['д', 'y', 'yes']:
            fname = input("Имя файла (magma.bin): ").strip() or "magma.bin"
            with open(fname, 'wb') as f:
                f.write(enc)
            print(f"[Инфо] Сохранено в {fname}")

    except Exception as e:
        print(f"\n[Ошибка] {e}")


def decrypt_file_mode():
    """Режим расшифрования из файла"""
    print("\n" + "-" * 60)
    print("РАСШИФРОВАНИЕ ИЗ ФАЙЛА")
    print("-" * 60)

    fname = input("Имя файла: ").strip()
    kh = input("Ключ (64 hex): ").strip()

    try:
        with open(fname, 'rb') as f:
            enc = f.read()
        key = bytes.fromhex(kh)
        dec = decrypt_ecb(enc, key, use_padding=True)
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТ РАСШИФРОВАНИЯ")
        print("=" * 60)
        print(f"Расшифрованный текст: {dec.decode('utf-8')}")
        print("=" * 60)
    except FileNotFoundError:
        print(f"[Ошибка] Файл '{fname}' не найден")
    except Exception as e:
        print(f"[Ошибка] {e}")


def encrypt_hex_mode():
    """Режим шифрования HEX-данных (без padding)"""
    print("\n" + "-" * 60)
    print("ШИФРОВАНИЕ HEX-ДАННЫХ (без padding)")
    print("-" * 60)

    try:
        kh = input("Ключ (64 hex, Enter=тестовый): ").strip()
        if not kh:
            kh = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
            print("[Инфо] Используется тестовый ключ")

        plain_hex = input_hex("Введите открытый текст (hex): ")
        plain_bytes = bytes.fromhex(plain_hex)

        if len(plain_bytes) % 8 != 0:
            print("[Ошибка] Длина открытого текста должна быть кратна 8 байтам")
            return

        key = bytes.fromhex(kh)
        cipher_bytes = encrypt_ecb(plain_bytes, key, use_padding=False)

        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТ ШИФРОВАНИЯ")
        print("=" * 60)
        print(f"Шифртекст (hex): {cipher_bytes.hex().lower()}")
        print("=" * 60)

    except Exception as e:
        print(f"[Ошибка] {e}")


def decrypt_hex_mode():
    """Режим расшифрования HEX-данных (без padding)"""
    print("\n" + "-" * 60)
    print("РАСШИФРОВАНИЕ HEX-ДАННЫХ (без padding)")
    print("-" * 60)

    try:
        kh = input("Ключ (64 hex, Enter=тестовый): ").strip()
        if not kh:
            kh = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
            print("[Инфо] Используется тестовый ключ")

        cipher_hex = input_hex("Введите шифртекст (hex): ")
        cipher_bytes = bytes.fromhex(cipher_hex)

        if len(cipher_bytes) % 8 != 0:
            print("[Ошибка] Длина шифртекста должна быть кратна 8 байтам")
            return

        key = bytes.fromhex(kh)
        plain_bytes = decrypt_ecb(cipher_bytes, key, use_padding=False)

        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТ РАСШИФРОВАНИЯ")
        print("=" * 60)
        print(f"Открытый текст (hex): {plain_bytes.hex().lower()}")
        print("=" * 60)

    except Exception as e:
        print(f"[Ошибка] {e}")


def main():
    """Главная функция программы"""
    print("=" * 60)
    print("МАГМА — ГОСТ Р 34.12-2015")
    print("=" * 60)
    print("\nБлочный шифр: 64 бит блок, 256 бит ключ")
    print("Режим: ECB (для демонстрации)")

    while True:
        print("\n" + "-" * 40)
        print("МЕНЮ")
        print("-" * 40)
        print("1 - Тест по ГОСТ Р 34.12-2015 (А.2)")
        print("2 - Шифрование текста (UTF-8)")
        print("3 - Расшифрование из файла")
        print("4 - Шифрование HEX-данных (без padding)")
        print("5 - Расшифрование HEX-данных (без padding)")
        print("0 - Выход")
        print("-" * 40)

        ch = input("Ваш выбор: ").strip()

        if ch == "0":
            print("\n[Инфо] Программа завершена")
            print("=" * 60)
            sys.exit(0)
        elif ch == "1":
            run_test()
        elif ch == "2":
            encrypt_text_mode()
        elif ch == "3":
            decrypt_file_mode()
        elif ch == "4":
            encrypt_hex_mode()
        elif ch == "5":
            decrypt_hex_mode()
        else:
            print("[Ошибка] Неверный выбор")


if __name__ == "__main__":
    main()