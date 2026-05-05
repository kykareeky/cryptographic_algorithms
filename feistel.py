import os

PI = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]

def t_transform(a):
    result = 0
    for i in range(8):
        nibble = (a >> (4 * i)) & 0xF
        result |= PI[i][nibble] << (4 * i)
    return result

def rotate_left_11(value):
    return ((value << 11) | (value >> 21)) & 0xFFFFFFFF

def g(k, a):
    return rotate_left_11(t_transform((a + k) & 0xFFFFFFFF))

def G(k, a1, a0):
    return a0, g(k, a0) ^ a1

def key_schedule(key_hex):
    key_bytes = bytes.fromhex(key_hex)
    K = []
    for i in range(8):
        K.append(int.from_bytes(key_bytes[i*4:(i+1)*4], 'big'))
    return K * 3 + K[::-1]

def magma_encrypt_block(a, round_keys):
    a1 = (a >> 32) & 0xFFFFFFFF
    a0 = a & 0xFFFFFFFF
    for i in range(31):
        a1, a0 = G(round_keys[i], a1, a0)
    return (g(round_keys[31], a0) ^ a1) << 32 | a0

def magma_decrypt_block(b, round_keys):
    b1 = (b >> 32) & 0xFFFFFFFF
    b0 = b & 0xFFFFFFFF
    for i in range(31, 0, -1):
        b1, b0 = G(round_keys[i], b1, b0)
    return (g(round_keys[0], b0) ^ b1) << 32 | b0

def main():
    print("=" * 60)
    print("СЕТЬ ФЕЙСТЕЛЯ (МАГМА / ГОСТ 28147-89)")
    print("=" * 60)
    
    action = input("\nВыберите действие \n1 - Шифрование \n2 - Расшифрование ").strip()
    
    print("\n1 - Ввод HEX строки в консоли")
    print("2 - Чтение HEX из файла (input.txt)")
    choice = input("\nВаш выбор: ").strip()
    
    if choice == '1':
        print("\nВведите HEX строку (16 символов / 64 бита):")
        text = input().strip()
    elif choice == '2':
        if not os.path.exists('input.txt'):
            print("Файл input.txt не найден!")
            return
        with open('input.txt', 'r', encoding='utf-8') as f:
            text = f.read().strip()
    else:
        print("Неверный выбор!")
        return
    
    key = input("\nВведите ключ (64 HEX символа, 256 бит): ").strip()
    if len(key) != 64:
        print("Ключ должен быть 64 HEX символа!")
        return
    
    round_keys = key_schedule(key)
    data_int = int(text, 16)
    
    print("\n" + "-" * 40)
    print("РЕЗУЛЬТАТ")
    print("-" * 40)
    
    if action == '1':
        result = magma_encrypt_block(data_int, round_keys)
        print("\n" + "=" * 60)
        print("ЗАШИФРОВАННЫЙ ТЕКСТ (HEX):")
        print(f"{result:016x}")
        print("=" * 60)
    else:
        result = magma_decrypt_block(data_int, round_keys)
        print("\n" + "=" * 60)
        print("РАСШИФРОВАННЫЙ ТЕКСТ (HEX):")
        print(f"{result:016x}")
        print("=" * 60)

if __name__ == "__main__":
    main()