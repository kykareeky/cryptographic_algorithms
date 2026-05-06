import subprocess
import sys
import os

# Папка, где лежат все файлы шифров (относительно расположения этого скрипта)
SCRIPTS_FOLDER = ""
FILE_MAP = {
    1: "atbash.py",
    2: "caesar.py",
    3: "polybiy.py",
    4: "tritemius.py",
    5: "belazo.py",
    6: "vigenere_selfkey.py",
    7: "vigenere_autokey.py",
    8: "magma.py",
    9: "matrix.py",
    10: "playfair.py",
    11: "verticalpermut.py",
    12: "cardano.py",
    13: "feistel.py",
    14: "lab5.py",
    15: "magmagammir.py",
    16: "a5_1.py",
    17: "a5_2.py",
    18: "magma 2.py",
    19: "aes.py",
    20: "kuznechik.py",
    21: "rsa.py",
    22: "elgamal.py",
    23: "ecc.py",
    24: "rsadigitalsign.py",
    25: "elgamaldigitasign.py",
    26: "gost94.py",
    27: "gost2012.py",
    28: "hell_lab11.py",
}

def get_scripts_dir():
    """Возвращает путь к папке с файлами шифров"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_path = os.path.join(script_dir, SCRIPTS_FOLDER)
    return scripts_path

def run_script(file_name):
    scripts_dir = get_scripts_dir()
    file_path = os.path.join(scripts_dir, file_name)
    
    if not os.path.exists(file_path):
        print(f"Файл {file_name} не найден в папке: {scripts_dir}")
        print(f"Проверьте, что папка '{SCRIPTS_FOLDER}' существует и файлы внутри неё.")
        input("Нажмите Enter, чтобы вернуться...")
        return
    
    try:
        print(f"\n▶ Запуск {file_name}...")
        print("=" * 60)
        subprocess.run([sys.executable, file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении {file_name}: {e}")
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

def main():
    print("\n" + "=" * 60)
    print("ЗАГРУЗКА МЕНЮ...")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = get_scripts_dir()
    
    print(f" Директория интерфейса: {script_dir}")
    print(f" Директория с шифрами: {scripts_dir}")
    print(f" Папка с шифрами существует: {' Да' if os.path.exists(scripts_dir) else ' Нет'}")
    
    if not os.path.exists(scripts_dir):
        print(f"\n ВНИМАНИЕ: Папка '{SCRIPTS_FOLDER}' не найдена!")
        print(f"   Создайте папку с именем '{SCRIPTS_FOLDER}' и поместите в неё все файлы шифров.")
        input("\nНажмите Enter для продолжения...")
    
    while True:
        print("\n" + "=" * 60)
        print("ГЛАВНОЕ МЕНЮ – ВСЕ ШИФРЫ ПО БЛОКАМ")
        print("=" * 60)
        print("Блок A (однозначная замена):")
        print("  1. Атбаш")
        print("  2. Цезарь")
        print("  3. Квадрат Полибия")
        print("Блок B (многозначная замена):")
        print("  4. Тритемий")
        print("  5. Белазо")
        print("  6. Виженер (самоключ)")
        print("  7. Виженер (автоключ по шифртексту)")
        print("  8. S-блок МАГМА")
        print("Блок C (блочная замена):")
        print("  9. Матричный шифр")
        print(" 10. Плэйфер")
        print("Блок D (перестановка):")
        print(" 11. Вертикальная перестановка")
        print(" 12. Решетка Кардано")
        print(" 13. Сеть Фейстеля")
        print("Блок E (гаммирование):")
        print(" 14. Одноразовый блокнот Шеннона")
        print(" 15. Гаммирование ГОСТ (CTR)")
        print("Блок F (поточные):")
        print(" 16. A5/1")
        print(" 17. A5/2")
        print("Блок G (комбинационные):")
        print(" 18. МАГМА (ECB)")
        print(" 19. AES")
        print(" 20. КУЗНЕЧИК")
        print("Блок H (асимметричные):")
        print(" 21. RSA (шифрование)")
        print(" 22. ElGamal (шифрование)")
        print(" 23. ECC")
        print("Блок I (цифровые подписи):")
        print(" 24. RSA подпись")
        print(" 25. ElGamal подпись")
        print("Блок J (стандарты подписей):")
        print(" 26. ГОСТ Р 34.10-94")
        print(" 27. ГОСТ Р 34.10-2012")
        print("Блок K (обмен ключами):")
        print(" 28. Диффи-Хеллман")
        print("  0. Выход")
        
        choice = input("\nВаш выбор: ").strip()
        if choice == '0':
            print("До свидания!")
            break
        if choice.isdigit():
            choice_num = int(choice)
            if choice_num in FILE_MAP:
                file_name = FILE_MAP[choice_num]
                run_script(file_name)
            else:
                print(" Неверный номер. Попробуйте снова.")
        else:
            print(" Введите число.")

if __name__ == "__main__":
    main()