import sys

# [КРИПТО] Таблицы замен S-блоков ГОСТ Р 34.12-2015 (МАГМА)
PI = [
    [12,4,6,2,10,5,11,9,14,8,13,7,0,3,15,1],
    [6,8,2,3,9,10,5,12,1,14,4,7,11,13,0,15],
    [11,3,5,8,2,15,10,13,14,1,7,4,12,9,6,0],
    [12,8,2,1,13,4,15,6,7,0,10,5,3,14,9,11],
    [7,15,5,10,8,1,6,13,0,9,3,14,11,4,2,12],
    [5,13,15,6,9,2,12,10,11,7,8,1,4,3,14,0],
    [8,14,2,5,6,9,1,12,15,4,11,0,13,10,3,7],
    [1,7,14,13,0,5,8,3,4,15,10,6,9,12,11,2],
]

def t(a):
    # [КРИПТО] Нелинейное преобразование T: параллельная подстановка 8 нибблов через S-блоки PI
    result = 0
    # [КРИПТО] Цикл обработки 4-битных сегментов 32-битного слова
    for i in range(8):
        nibble = (a >> (4 * i)) & 0xF
        result |= PI[i][nibble] << (4 * i)
    return result

def rot11(x):
    # [КРИПТО] Линейное преобразование L: циклический сдвиг влево на 11 бит (диффузия)
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF

def g(k, a):
    # [КРИПТО] Раундовая функция G: G_k(a) = L(T((a + k) mod 2^32))
    # Базовый строительный блок сети Фейстеля ГОСТ
    return rot11(t((a + k) & 0xFFFFFFFF))

def key_schedule(key_bytes):
    # [КРИПТО] Развёртывание 256-битного ключа в 8x32-битных подключей
    k = [int.from_bytes(key_bytes[4*i:4*i+4], 'big') for i in range(8)]
    # [КРИПТО] Формирование последовательности из 32 раундовых ключей: K1..K8 трижды, затем K8..K1
    return k * 3 + k[::-1]

def encrypt_block(blk, rk):
    # [КРИПТО] Зашифрование 64-битного блока в сети Фейстеля (32 раунда)
    a1 = int.from_bytes(blk[:4], 'big')
    a0 = int.from_bytes(blk[4:], 'big')
    # [КРИПТО] Цикл первых 31 раундов с обменом половин
    for i in range(31):
        a1, a0 = a0, a1 ^ g(rk[i], a0)
    # [КРИПТО] 32-й раунд без обмена (согласно стандарту ГОСТ)
    a1 = a1 ^ g(rk[31], a0)
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')

def decrypt_block(blk, rk):
    # [КРИПТО] Расшифрование: обратный порядок ключей, структура алгоритма идентична шифрованию
    a1 = int.from_bytes(blk[:4], 'big')
    a0 = int.from_bytes(blk[4:], 'big')
    # [КРИПТО] Инверсия 32-го раунда
    a1 = a1 ^ g(rk[31], a0)
    # [КРИПТО] Цикл обратных раундов от 30 до 0
    for i in range(30, -1, -1):
        a1, a0 = a0 ^ g(rk[i], a1), a1
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')

def pad(data):
    # [КРИПТО] Добавление заполнения PKCS#7 для выравнивания длины данных до кратности 8 байтам
    n = 8 - len(data) % 8
    return data + bytes([n]*n)

def unpad(data):
    # [КРИПТО] Удаление PKCS#7 заполнения по значению последнего байта
    return data[:-data[-1]]

def encrypt_ecb(data, key_bytes, use_padding=True):
    # [КРИПТО] Режим электронной кодовой книги (ECB): независимое шифрование каждого блока
    rk = key_schedule(key_bytes)
    if use_padding:
        data = pad(data)
    else:
        if len(data) % 8 != 0:
            raise ValueError("Длина данных должна быть кратна 8 байтам при use_padding=False")
    # [КРИПТО] Цикл поблочного шифрования
    return b''.join(encrypt_block(data[i:i+8], rk) for i in range(0, len(data), 8))

def decrypt_ecb(data, key_bytes, use_padding=True):
    # [КРИПТО] Расшифрование в режиме ECB с последующим удалением заполнения
    rk = key_schedule(key_bytes)
    if len(data) % 8 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 8")
    dec = b''.join(decrypt_block(data[i:i+8], rk) for i in range(0, len(data), 8))
    if use_padding:
        return unpad(dec)
    else:
        return dec

def run_test():
    print("\n" + "=" * 60)
    print("ТЕСТ — ГОСТ Р 34.12-2015, Приложение А.2")
    print("=" * 60)
    KEY = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100 "
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff "
    )
    PLAIN   = bytes.fromhex( "fedcba9876543210 ")
    EXPECTED=  "4ee901e5c2d8ca3d "

    rk = key_schedule(KEY)
    enc = encrypt_block(PLAIN, rk)
    dec = decrypt_block(enc, rk)

    print(f"\nОткрытый : {PLAIN.hex()} ")
    print(f"Ожидается: {EXPECTED} ")
    print(f"Получено : {enc.hex()} ")
    ok = enc.hex() == EXPECTED
    print(f"Результат: {'[Успех] ВЕРНО' if ok else '[Ошибка] НЕВЕРНО'} ")
    print(f"Расшифр  : {dec.hex()}  {'[Успех] ВЕРНО' if dec==PLAIN else '[Ошибка] НЕВЕРНО'} ")

    print(f"\n{'-' * 40} ")
    print( "Преобразование t (А.2.1) ")
    print( "-" * 40)
    # [КРИПТО] Валидация нелинейного преобразования по тестовым векторам ГОСТ
    for i,e in [(0xfdb97531,0x2a196f34),(0x2a196f34,0xebd9f03a),
                (0xebd9f03a,0xb039bb3d),(0xb039bb3d,0x68695433)]:
        r = t(i)
        print(f"  t({i:08x}) = {r:08x}  ожид {e:08x}  {'[Успех]' if r==e else '[Ошибка]'} ")

    print(f"\n{'-' * 40} ")
    print( "Преобразование g (А.2.2) ")
    print( "-" * 40)
    # [КРИПТО] Валидация раундовой функции G
    for kv,av,e in [(0x87654321,0xfedcba98,0xfdcbc20c),
                    (0xfdcbc20c,0x87654321,0x7e791a4b),
                    (0x7e791a4b,0xfdcbc20c,0xc76549ec),
                    (0xc76549ec,0x7e791a4b,0x9791c849)]:
        r = g(kv,av)
        print(f"  g[{kv:08x}]({av:08x}) = {r:08x}  ожид {e:08x}  {'[Успех]' if r==e else '[Ошибка]'} ")

    print(f"\n{'-' * 40} ")
    print( "Тест на тексте  >1000 символов ")
    print( "-" * 40)
    txt = (b"Magma GOST cipher test. Block=64bit Key=256bit.  " * 25)  # 1175 байт
    enc2 = encrypt_ecb(txt, KEY, use_padding=True)
    dec2 = decrypt_ecb(enc2, KEY, use_padding=True)
    ok2  = dec2 == txt
    print(f"  Длина текста    : {len(txt)} байт ")
    print(f"  Зашифровано     : {len(enc2)} байт ")
    print(f"  Результат       : {'[Успех] Совпадает' if ok2 else '[Ошибка] Не совпадает'} ")
    print(f"  Шифртекст (hex) : {enc2.hex()[:64]}... ")
    print( "\n " +  "= " * 60)

def input_hex(prompt, required_length=None):
    s = input(prompt).strip().replace(' ', '')
    if s.startswith('0x') or s.startswith('0X'):
        s = s[2:]
    if required_length is not None and len(s) != required_length:
        raise ValueError(f"Должно быть ровно {required_length} hex-символов")
    return s

def main():
    print("=" * 60)
    print("МАГМА — ГОСТ Р 34.12-2015")
    print("=" * 60)
    print("\nБлочный шифр: 64 бита блок, 256 бит ключ")
    print("Режим: ECB")
    while True:
        print( "\n " +  "-" * 40)
        print( "МЕНЮ ")
        print( "-" * 40)
        print( "1 - Запустить тест ГОСТ Р 34.12-2015 ")
        print( "2 - Зашифровать текст (UTF-8) ")
        print( "3 - Расшифровать текст (из файла) ")
        print( "4 - Зашифровать hex-данные (без padding) ")
        print( "5 - Расшифровать hex-данные (без padding) ")
        print( "0 - Выход ")
        print( "-" * 40)

        ch = input( "Ваш выбор:  ").strip()

        if ch ==  "0 ":
            print( "\n[Инфо] Программа завершена ")
            print( "= " * 60)
            sys.exit(0)

        elif ch ==  "1 ":
            run_test()

        elif ch ==  "2 ":
            kh = input( "Ключ (64 hex, Enter=тестовый):  ").strip() or \
                  "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff "
            txt = input( "Текст:  ").encode('utf-8')
            key = bytes.fromhex(kh)
            enc = encrypt_ecb(txt, key, use_padding=True)
            print( "\n " +  "-" * 40)
            print( "РЕЗУЛЬТАТ ШИФРОВАНИЯ ")
            print( "-" * 40)
            print(f"Шифртекст (hex): {enc.hex()} ")
            save = input( "\nСохранить в файл? (д/н):  ").strip().lower()
            if save in ['д', 'y', 'yes']:
                fname = input( "Имя файла (magma.bin):  ").strip() or  "magma.bin "
                with open(fname, 'wb') as f:
                    f.write(enc)
                print(f"[Инфо] Сохранено в {fname} ")

        elif ch ==  "3 ":
            fname = input( "Имя файла:  ").strip()
            kh = input( "Ключ (64 hex):  ").strip()
            try:
                with open(fname, 'rb') as f:
                    enc = f.read()
                dec = decrypt_ecb(enc, bytes.fromhex(kh), use_padding=True)
                print( "\n " +  "-" * 40)
                print( "РЕЗУЛЬТАТ РАСШИФРОВАНИЯ ")
                print( "-" * 40)
                print(f"Расшифровано: {dec.decode('utf-8')} ")
                print( "-" * 40)
            except Exception as e:
                print(f"[Ошибка] {e} ")

        elif ch ==  "4 ":
            try:
                kh = input( "Ключ (64 hex, Enter=тестовый):  ").strip() or \
                      "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff "
                plain_hex = input_hex( "Открытый текст (hex):  ")
                plain_bytes = bytes.fromhex(plain_hex)
                key = bytes.fromhex(kh)
                if len(plain_bytes) % 8 != 0:
                    raise ValueError( "Длина открытого текста должна быть кратна 8 байтам ")
                cipher_bytes = encrypt_ecb(plain_bytes, key, use_padding=False)
                print( "\n " +  "-" * 40)
                print( "РЕЗУЛЬТАТ ШИФРОВАНИЯ ")
                print( "-" * 40)
                print(f"Шифртекст (hex): {cipher_bytes.hex().lower()} ")
                print( "-" * 40)
            except Exception as e:
                print(f"[Ошибка] {e} ")

        elif ch ==  "5 ":
            try:
                kh = input( "Ключ (64 hex, Enter=тестовый):  ").strip() or \
                      "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff "
                cipher_hex = input_hex( "Шифртекст (hex):  ")
                cipher_bytes = bytes.fromhex(cipher_hex)
                key = bytes.fromhex(kh)
                if len(cipher_bytes) % 8 != 0:
                    raise ValueError( "Длина шифртекста должна быть кратна 8 байтам ")
                plain_bytes = decrypt_ecb(cipher_bytes, key, use_padding=False)
                print( "\n " +  "-" * 40)
                print( "РЕЗУЛЬТАТ РАСШИФРОВАНИЯ ")
                print( "-" * 40)
                print(f"Открытый текст (hex): {plain_bytes.hex().lower()} ")
                print( "-" * 40)
            except Exception as e:
                print(f"[Ошибка] {e} ")

        else:
            print( "[Ошибка] Неверный выбор ")

if __name__ == "__main__":
    main()