import os
from collections import OrderedDict

# [КРИПТО] Алфавит для 5x6 матрицы (30 символов): Ё→Е, Й→И, Ь→Ъ для устранения дубликатов и укладывания в размеры сетки
ALPHABET = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЭЮЯ"

def clearCrypte(text):
    """Подготовка текста: верхний регистр, замена знаков и пробелов на маркеры"""
    # [КРИПТО] Нормализация входного потока под алфавит Playfair: замена эквивалентных букв и пунктуации на маркеры
    text = text.upper()
    text = text.replace('Ё', 'Е').replace('Й', 'И').replace('Ь', 'Ъ')
    text = text.replace('.', 'ТЧК')
    text = text.replace(',', 'ЗПТ')
    text = text.replace(' ', 'ПРБ')  # Пробелы всегда заменяются, без проверки длины
    return text

def clearEncypte(text):
    """Восстановление исходного формата из маркеров"""
    # [КРИПТО] Обратное преобразование маркеров в читаемые символы после расшифровки
    text = text.replace('ПРБ', ' ')
    text = text.replace('ТЧК', '.')
    text = text.replace('ЗПТ', ',')
    return text

def findIndex(table, text):
    # [КРИПТО] Поиск координат (row, col) символа в матрице Playfair
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j] == text:
                return (i, j)
    return None

def PlayfairCrypt(text, key):
    # [КРИПТО] Функция шифрования биграммами по правилам Playfair
    text = clearCrypte(text)
    key = key.upper().replace('Ё', 'Е').replace('Й', 'И').replace('Ь', 'Ъ')
    count = 0
    shifrText = ""

    # [КРИПТО] Формирование ключевой перестановки алфавита: сначала уникальные символы ключа, затем остаток алфавита
    newAlf = "".join(OrderedDict.fromkeys(key + ALPHABET))
    # [КРИПТО] Инициализация 5x6 матрицы шифра
    playfTable = [[0] * 6 for _ in range(5)]

    # [КРИПТО] Заполнение матрицы символами ключевого алфавита построчно (row-major order)
    for i in range(5):
        for j in range(6):
            playfTable[i][j] = newAlf[count]
            count += 1

    new_text = list(text)
    i = 0
    # [КРИПТО] Padding биграмм: если в паре одинаковые буквы, вставляем разделитель 'Ф' для нарушения паттерна
    while i < len(new_text) - 1:
        if new_text[i] == new_text[i + 1]:
            new_text.insert(i + 1, "Ф")
        i += 1

    # [КРИПТО] Если длина нечётная, добавляем финальный заполнитель для замыкания последней биграммы
    if len(new_text) % 2 != 0:
        new_text.append("Ф")

    text = new_text

    # [КРИПТО] Цикл обработки текста биграммами (по 2 символа)
    for i in range(0, len(text), 2):
        f_let = text[i]
        s_let = text[i + 1]

        posF = findIndex(playfTable, f_let)
        posS = findIndex(playfTable, s_let)
        
        if posF is None or posS is None:
            shifrText += f_let + s_let
            continue
            
        f_let_i, f_let_j = posF
        s_let_i, s_let_j = posS

        # [КРИПТО] Правило 1: символы в одной строке -> сдвиг вправо на 1 (по модулю ширины 6)
        if f_let_i == s_let_i:
            shifrText += playfTable[f_let_i][(f_let_j + 1) % 6]
            shifrText += playfTable[s_let_i][(s_let_j + 1) % 6]
        # [КРИПТО] Правило 2: символы в одном столбце -> сдвиг вниз на 1 (по модулю высоты 5)
        elif f_let_j == s_let_j:
            shifrText += playfTable[(f_let_i + 1) % 5][f_let_j]
            shifrText += playfTable[(s_let_i + 1) % 5][s_let_j]
        # [КРИПТО] Правило 3: прямоугольник -> замена столбцов (сохранение строк, перестановка координат j)
        else:
            shifrText += playfTable[f_let_i][s_let_j]
            shifrText += playfTable[s_let_i][f_let_j]

    return shifrText

def PlayfairEncrypt(text, key):
    # [КРИПТО] Функция расшифрования (обратное применение правил Playfair)
    text = text.upper()
    key = key.upper().replace('Ё', 'Е').replace('Й', 'И').replace('Ь', 'Ъ')
    count = 0
    result = ""

    # [КРИПТО] Идентичная генерация матрицы ключа, как при шифровании
    newAlf = "".join(OrderedDict.fromkeys(key + ALPHABET))
    playfTable = [[0] * 6 for _ in range(5)]

    for i in range(5):
        for j in range(6):
            playfTable[i][j] = newAlf[count]
            count += 1

    # [КРИПТО] Цикл побиграммного восстановления
    for i in range(0, len(text), 2):
        f_let = text[i]
        s_let = text[i + 1]

        posF = findIndex(playfTable, f_let)
        posS = findIndex(playfTable, s_let)
        
        if posF is None or posS is None:
            result += f_let + s_let
            continue
            
        f_let_i, f_let_j = posF
        s_let_i, s_let_j = posS

        # [КРИПТО] Инверсия правила 1: сдвиг влево на 1 (по модулю 6)
        if f_let_i == s_let_i:
            result += playfTable[f_let_i][(f_let_j - 1) % 6]
            result += playfTable[s_let_i][(s_let_j - 1) % 6]
        # [КРИПТО] Инверсия правила 2: сдвиг вверх на 1 (по модулю 5)
        elif f_let_j == s_let_j:
            result += playfTable[(f_let_i - 1) % 5][f_let_j]
            result += playfTable[(s_let_i - 1) % 5][s_let_j]
        # [КРИПТО] Правило 3 симметрично: замена столбцов остаётся идентичной
        else:
            result += playfTable[f_let_i][s_let_j]
            result += playfTable[s_let_i][f_let_j]

    # [КРИПТО] Удаление добавленных при шифровании символов-заполнителей 'Ф'
    result = result.replace('Ф', '')
    result = clearEncypte(result)
    return result

def main():
    print("=" * 60)
    print("ШИФР ПЛЕЙФЕЙРА")
    print("=" * 60)
    action = input( "\nВыберите действие \n1 - Шифрование \n2 - Расшифрование  ").strip()

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
            print( "[Ошибка] Текст не введен! ")
            return
    elif choice == '2':
        if not os.path.exists('input.txt'):
            print( "[Ошибка] Файл input.txt не найден! ")
            return
        with open('input.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print( "[Ошибка] Неверный выбор! ")
        return

    key = input( "\nВведите ключевое слово:  ")

    print( "\n " +  "-" * 40)
    print( "РЕЗУЛЬТАТ ")
    print( "-" * 40)

    if action == '1':
        result = PlayfairCrypt(text, key)
        print( "\n " +  "= " * 60)
        print( "ЗАШИФРОВАННЫЙ ТЕКСТ: ")
        print(result)
        print( "= " * 60)
    else:
        result = PlayfairEncrypt(text, key)
        print( "\n " +  "= " * 60)
        print( "РАСШИФРОВАННЫЙ ТЕКСТ: ")
        print(result)
        print( "= " * 60)

if __name__ == "__main__":
    main()