import sys

# ══════════════════════════════════════════════════════════════
# КУЗНЕЧИК (ГОСТ Р 34.12-2015)
# ══════════════════════════════════════════════════════════════

# Нелинейная подстановка π (раздел 4.1.1)
PI = [
    252,238,221, 17,207,110, 49, 22,251,196,250,218, 35,197,  4, 77,
    233,119,240,219,147, 46,153,186, 23, 54,241,187, 20,205, 95,193,
    249, 24,101, 90,226, 92,239, 33,129, 28, 60, 66,139,  1,142, 79,
      5,132,  2,174,227,106,143,160,  6, 11,237,152,127,212,211, 31,
    235, 52, 44, 81,234,200, 72,171,242, 42,104,162,253, 58,206,204,
    181,112, 14, 86,  8, 12,118, 18,191,114, 19, 71,156,183, 93,135,
     21,161,150, 41, 16,123,154,199,243,145,120,111,157,158,178,177,
     50,117, 25, 61,255, 53,138,126,109, 84,198,128,195,189, 13, 87,
    223,245, 36,169, 62,168, 67,201,215,121,214,246,124, 34,185,  3,
    224, 15,236,222,122,148,176,188,220,232, 40, 80, 78, 51, 10, 74,
    167,151, 96,115, 30,  0, 98, 68, 26,184, 56,130,100,159, 38, 65,
    173, 69, 70,146, 39, 94, 85, 47,140,163,165,125,105,213,149, 59,
      7, 88,179, 64,134,172, 29,247, 48, 55,107,228,136,217,231,137,
    225, 27,131, 73, 76, 63,248,254,141, 83,170,144,202,216,133, 97,
     32,113,103,164, 45, 43,  9, 91,203,155, 37,208,190,229,108, 82,
     89,166,116,210,230,244,180,192,209,102,175,194, 57, 75, 99,182,
]

PI_INV = [0] * 256
for i, v in enumerate(PI):
    PI_INV[v] = i

# Поле GF(2^8) с неприводимым многочленом p(x) = x^8+x^7+x^6+x+1 (0x1C3)
GF_MOD = 0x1C3

def gf_mul(a, b):
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 0x100:
            a ^= GF_MOD
    return result

# Коэффициенты линейного преобразования ℓ (формула 1)
L_COEFFS = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]

def l_func(a):
    result = 0
    for i in range(16):
        result ^= gf_mul(L_COEFFS[i], a[i])
    return result

def X(k, a):
    return [k[i] ^ a[i] for i in range(16)]

def S(a):
    return [PI[b] for b in a]

def S_inv(a):
    return [PI_INV[b] for b in a]

# Циклический сдвиг вправо R (формула 5)
def R(a):
    new_byte = l_func(a)
    return [new_byte] + a[:-1]

# Обратный сдвиг R⁻¹ (формула 7)
def R_inv(a):
    tail = a[1:] + [a[0]]
    new_byte = l_func(tail)
    return a[1:] + [new_byte]

def L(a):
    for _ in range(16):
        a = R(a)
    return a

def L_inv(a):
    for _ in range(16):
        a = R_inv(a)
    return a

# Итерационные константы Ci = L(Vec128(i)), i=1..32 (формула 10)
def _gen_constants():
    consts = []
    for i in range(1, 33):
        consts.append(L([0] * 15 + [i]))
    return consts

ITER_CONSTS = _gen_constants()

# Раундовая функция F[k](a1, a0) = (LSX[k](a1) ⊕ a0, a1) (формула 9)
def F(k, a1, a0):
    lsx = L(S(X(k, a1)))
    return X(lsx, a0), a1

# Алгоритм развертывания ключа (раздел 4.3)
def key_schedule(key_bytes):
    k1 = list(key_bytes[:16])
    k2 = list(key_bytes[16:])
    keys = [k1, k2]
    a, b = k1[:], k2[:]
    for i in range(4):
        for j in range(8):
            a, b = F(ITER_CONSTS[8 * i + j], a, b)
        keys.append(a[:])
        keys.append(b[:])
    return keys

# Алгоритм зашифрования (формула 12)
def encrypt_block(plain_bytes, round_keys):
    a = list(plain_bytes)
    for i in range(9):
        a = L(S(X(round_keys[i], a)))
    return bytes(X(round_keys[9], a))

# Алгоритм расшифрования (формула 13)
def decrypt_block(cipher_bytes, round_keys):
    a = list(cipher_bytes)
    a = X(round_keys[9], a)
    for i in range(8, -1, -1):
        a = X(round_keys[i], S_inv(L_inv(a)))
    return bytes(a)

def _pkcs7_pad(data, block=16):
    n = block - len(data) % block
    return data + bytes([n] * n)

def _pkcs7_unpad(data):
    n = data[-1]
    if n < 1 or n > 16:
        raise ValueError("Некорректный padding")
    return data[:-n]

def encrypt_ecb(data, key_bytes, use_padding=True):
    rk = key_schedule(key_bytes)
    if use_padding:
        data = _pkcs7_pad(data)
    else:
        if len(data) % 16 != 0:
            raise ValueError("Длина данных должна быть кратна 16 байтам")
    return b''.join(encrypt_block(data[i:i+16], rk) for i in range(0, len(data), 16))

def decrypt_ecb(data, key_bytes, use_padding=True):
    if len(data) % 16 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 16 байтам")
    rk = key_schedule(key_bytes)
    dec = b''.join(decrypt_block(data[i:i+16], rk) for i in range(0, len(data), 16))
    return _pkcs7_unpad(dec) if use_padding else dec

# ══════════════════════════════════════════════════════════════
# РАБОТА С РУССКИМ ТЕКСТОМ
# ══════════════════════════════════════════════════════════════
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
L2N = {c: i+1 for i, c in enumerate(ALPHABET)}
N2L = {i+1: c for i, c in enumerate(ALPHABET)}

def preprocess(text):
    """Заменяет пробелы, запятые и точки на маркеры. Остальные символы игнорируются."""
    res = []
    for ch in text.lower():
        if ch == ' ':
            res.append('прб')
        elif ch == ',':
            res.append('зпт')
        elif ch == '.':
            res.append('тчк')
        elif ch in ALPHABET:
            res.append(ch)
    return ''.join(res)

def postprocess(text):
    """Восстанавливает пробелы, запятые и точки из маркеров."""
    text = text.replace('прб', ' ')
    text = text.replace('зпт', ',')
    text = text.replace('тчк', '.')
    return text

def text_to_bytes_ru(text):
    return bytes([L2N[c] for c in text])

def bytes_to_text_ru(data):
    result = []
    for b in data:
        if 1 <= b <= 32:
            result.append(N2L[b])
    return ''.join(result)

def encrypt_russian(plain, key_hex):
    processed = preprocess(plain)
    if not processed:
        raise ValueError("Текст пуст после предобработки")
    data = text_to_bytes_ru(processed)
    key = bytes.fromhex(key_hex)
    enc = encrypt_ecb(data, key, use_padding=True)
    return enc.hex().upper()

def decrypt_russian(cipher_hex, key_hex):
    """Расшифрование с автоматическим восстановлением пробелов и пунктуации"""
    key = bytes.fromhex(key_hex)
    enc = bytes.fromhex(cipher_hex)
    dec = decrypt_ecb(enc, key, use_padding=True)
    return postprocess(bytes_to_text_ru(dec))

# ══════════════════════════════════════════════════════════════
# ТЕСТ ПО ГОСТ Р 34.12-2015 (Приложение А.1)
# ══════════════════════════════════════════════════════════════
def run_gost_test():
    print("\n" + "=" * 60)
    print("ТЕСТ — ГОСТ Р 34.12-2015, Приложение А.1 (КУЗНЕЧИК)")
    print("=" * 60)

    KEY = bytes.fromhex(
        "8899aabbccddeeff0011223344556677"
        "fedcba98765432100123456789abcdef"
    )
    PLAIN = bytes.fromhex("1122334455667700ffeeddccbbaa9988")
    EXPECTED_CIPHER = "7f679d90bebc24305a468d42b9d4edcd"

    EXP_KEYS = [
        "8899aabbccddeeff0011223344556677",
        "fedcba98765432100123456789abcdef",
        "db31485315694343228d6aef8cc78c44",
        "3d4553d8e9cfec6815ebadc40a9ffd04",
        "57646468c44a5e28d3e59246f429f1ac",
        "bd079435165c6432b532e82834da581b",
        "51e640757e8745de705727265a0098b1",
        "5a7925017b9fdd3ed72a91a22286f984",
        "bb44e25378c73123a5f32f73cdb6e517",
        "72e9dd7416bcf45b755dbaa88e4a4043",
    ]

    rk = key_schedule(KEY)

    print("\n[Инфо] Раундовые ключи K1..K10 (сравнение с ГОСТ А.1.4)")
    print("-" * 40)
    all_keys_ok = True
    for i in range(10):
        kh = bytes(rk[i]).hex()
        exp = EXP_KEYS[i]
        ok = kh == exp
        all_keys_ok = all_keys_ok and ok
        print(f"  K{i+1:2d}: {kh}  {'[Успех]' if ok else '[Ошибка]'}")

    print("\n[Инфо] Промежуточные шаги (А.1.5)")
    print("-" * 40)
    a = list(PLAIN)
    xk = X(rk[0], a)
    sx = S(xk)
    lsx = L(sx)
    
    steps_ok = True
    for name, exp, got in [
        ("X[K1](a)",    "99bb99ff99bb99ffffffffffffffffff", bytes(xk).hex()),
        ("S(X[K1](a))", "e87de8b6e87de8b6b6b6b6b6b6b6b6b6", bytes(sx).hex()),
        ("LSX[K1](a)",  "e297b686e355b0a1cf4a2f9249140830", bytes(lsx).hex()),
    ]:
        ok = got == exp
        steps_ok = steps_ok and ok
        print(f"  {name:<18}: {got}  {'[Успех]' if ok else '[Ошибка]'}")

    enc = encrypt_block(PLAIN, rk)
    dec = decrypt_block(enc, rk)

    print(f"\n[Инфо] Шифрование блока")
    print("-" * 40)
    print(f"  Открытый : {PLAIN.hex()}")
    print(f"  Ожидается: {EXPECTED_CIPHER}")
    print(f"  Получено : {enc.hex()}")
    enc_ok = enc.hex() == EXPECTED_CIPHER
    print(f"  Результат: {'[Успех] ВЕРНО' if enc_ok else '[Ошибка] НЕВЕРНО'}")
    
    print(f"\n[Инфо] Расшифрование блока")
    print("-" * 40)
    print(f"  Шифртекст: {enc.hex()}")
    print(f"  Получено : {dec.hex()}")
    dec_ok = dec == PLAIN
    print(f"  Результат: {'[Успех] ВЕРНО' if dec_ok else '[Ошибка] НЕВЕРНО'}")

    long_text = b"Kuznyechik GOST R 34.12-2015 block cipher test data. " * 20
    enc2 = encrypt_ecb(long_text, KEY, use_padding=True)
    dec2 = decrypt_ecb(enc2, KEY, use_padding=True)
    ecb_ok = dec2 == long_text
    print(f"\n[Инфо] Тест на тексте >1000 байт")
    print("-" * 40)
    print(f"  Длина       : {len(long_text)} байт")
    print(f"  Расшифровано: {'[Успех] Совпадает' if ecb_ok else '[Ошибка] Не совпадает'}")
    
    final_status = all_keys_ok and steps_ok and enc_ok and dec_ok and ecb_ok
    print("\n" + "=" * 60)
    print(f"ИТОГ: {'[Успех] ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ' if final_status else '[Внимание] ЕСТЬ ОШИБКИ'}")
    print("=" * 60)

# ══════════════════════════════════════════════════════════════
# МЕНЮ И ВВОД
# ══════════════════════════════════════════════════════════════
def get_key(prompt="Ключ (64 hex, Enter=тестовый): "):
    kh = input(prompt).strip().replace(' ', '')
    if not kh:
        kh = "8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"
        print(f"  [Инфо] Используется тестовый ключ")
    if len(kh) != 64 or not all(c in '0123456789abcdefABCDEF' for c in kh):
        raise ValueError("Ключ должен содержать ровно 64 hex-символа")
    return kh

def main():
    print("=" * 60)
    print("КУЗНЕЧИК — ГОСТ Р 34.12-2015")
    print("=" * 60)

    while True:
        print("\n" + "-" * 40)
        print("МЕНЮ:")
        print("  1. Тест по ГОСТ Р 34.12-2015 (А.1)")
        print("  2. Шифрование (русский текст)")
        print("  3. Расшифрование (русский текст)")
        print("  4. Шифрование (hex данные)")
        print("  5. Расшифрование (hex данные)")
        print("  0. Выход")
        print("-" * 40)

        ch = input("Выбор: ").strip()

        if ch == "0":
            print("\n[Инфо] Программа завершена")
            print("=" * 60)
            sys.exit(0)

        elif ch == "1":
            run_gost_test()
            input("\nНажмите Enter для возврата в меню...")

        elif ch == "2":
            try:
                kh = get_key()
                txt = input("Текст (русские буквы, пробелы, . ,): ").strip()
                enc = encrypt_russian(txt, kh)
                print("\n" + "-" * 40)
                print("РЕЗУЛЬТАТ ШИФРОВАНИЯ")
                print("-" * 40)
                print(f"Шифртекст (hex): {enc}")
                print("-" * 40)
                save = input("Сохранить в файл? (д/н): ").strip().lower()
                if save in ['д', 'y', 'yes']:
                    fn = input("Имя файла (kuz_cipher.bin): ").strip() or "kuz_cipher.bin"
                    with open(fn, 'wb') as f:
                        f.write(bytes.fromhex(enc))
                    print(f"[Инфо] Сохранено в '{fn}'")
            except Exception as e:
                print(f"[Ошибка] {e}")

        elif ch == "3":
            try:
                kh = get_key()
                chex = input("Шифртекст (hex): ").strip().replace(' ', '')
                # Функция уже возвращает готовый текст с пробелами и знаками
                dec = decrypt_russian(chex, kh)
                print("\n" + "-" * 40)
                print("РЕЗУЛЬТАТ РАСШИФРОВАНИЯ")
                print("-" * 40)
                print(f"Расшифрованный текст: {dec}")
                print("-" * 40)
            except Exception as e:
                print(f"[Ошибка] {e}")

        elif ch == "4":
            try:
                kh = get_key()
                phex = input("Открытый текст (hex): ").strip().replace(' ', '')
                pb = bytes.fromhex(phex)
                if len(pb) % 16 == 0:
                    enc = encrypt_ecb(pb, bytes.fromhex(kh), use_padding=False)
                else:
                    print("  [Инфо] Длина не кратна 16 — будет применён PKCS#7 padding")
                    enc = encrypt_ecb(pb, bytes.fromhex(kh), use_padding=True)
                print("\n" + "-" * 40)
                print("РЕЗУЛЬТАТ ШИФРОВАНИЯ")
                print("-" * 40)
                print(f"Шифртекст (hex): {enc.hex().upper()}")
                print("-" * 40)
            except Exception as e:
                print(f"[Ошибка] {e}")

        elif ch == "5":
            try:
                kh = get_key()
                chex = input("Шифртекст (hex): ").strip().replace(' ', '')
                cb = bytes.fromhex(chex)
                p = input("При шифровании использовался padding? (д/н): ").strip().lower()
                use_p = (p in ['д', 'y', 'yes'])
                dec = decrypt_ecb(cb, bytes.fromhex(kh), use_padding=use_p)
                print("\n" + "-" * 40)
                print("РЕЗУЛЬТАТ РАСШИФРОВАНИЯ")
                print("-" * 40)
                print(f"Открытый текст (hex): {dec.hex().upper()}")
                print("-" * 40)
            except Exception as e:
                print(f"[Ошибка] {e}")

        else:
            print("[Ошибка] Неверный выбор!")

if __name__ == "__main__":
    main()