import sys

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

def input_with_constraints(prompt: str, min_val: int = None, max_val: int = None,
                           is_prime_needed: bool = False, exclude: list = None) -> int:
    constraints = []
    if min_val is not None:
        constraints.append(f">= {min_val}")
    if max_val is not None:
        constraints.append(f"<= {max_val}")
    if is_prime_needed:
        constraints.append("простое")
    if exclude:
        constraints.append(f"не в {exclude}")
    constraint_str = f" ({', '.join(constraints)})" if constraints else ""

    while True:
        try:
            val = int(input(f"{prompt}{constraint_str}:").strip())
            
            if min_val is not None and val < min_val:
                print(f"[Ошибка] Значение должно быть >= {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"[Ошибка] Значение должно быть <= {max_val}")
                continue
            if is_prime_needed and not is_prime(val):
                print("[Ошибка] Значение должно быть простым числом")
                continue
            if exclude and val in exclude:
                print(f"[Ошибка] Значение не должно быть в {exclude}")
                continue
            
            return val
        except ValueError:
            print("[Ошибка] Введите целое число")

def demo_diffie_hellman():
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРОТОКОЛА ДИФФИ-ХЕЛЛМАНА")
    print("=" * 60)
    n_demo = 23
    a_demo = 5
    Ka_demo = 6
    Kb_demo = 15

    print(f"\nПараметры протокола:")
    print(f"  Простой модуль n = {n_demo}")
    print(f"  Генератор (база) a = {a_demo}")

    print(f"\n[Алиса] Секретный ключ Ka = {Ka_demo}")
    Ya_demo = pow(a_demo, Ka_demo, n_demo)
    print(f"  Открытый ключ Ya = a^Ka mod n = {Ya_demo}")

    print(f"\n[Боб] Секретный ключ Kb = {Kb_demo}")
    Yb_demo = pow(a_demo, Kb_demo, n_demo)
    print(f"  Открытый ключ Yb = a^Kb mod n = {Yb_demo}")

    print(f"\nОбмен открытыми ключами:")
    print(f"  Алиса получает Yb = {Yb_demo}")
    print(f"  Боб получает Ya = {Ya_demo}")

    print(f"\nВычисление общего секрета:")
    # [КРИПТО] Алиса возводит открытый ключ Боба в свой секретный ключ по модулю n
    A_demo = pow(Yb_demo, Ka_demo, n_demo)
    # [КРИПТО] Боб возводит открытый ключ Алисы в свой секретный ключ по модулю n
    B_demo = pow(Ya_demo, Kb_demo, n_demo)
    print(f"  Алиса: S = Yb^Ka mod n = {A_demo}")
    print(f"  Боб:   S = Ya^Kb mod n = {B_demo}")

    print(f"\n[Результат]: {'[Успех] Общие секреты совпадают' if A_demo == B_demo else '[Ошибка] Несовпадение секретов'}")
    print(f"Общий секретный ключ: {A_demo}")
    print("=" * 60)

def diffie_hellman():
    print("\n" + "-" * 60)
    print("ОБМЕН КЛЮЧАМИ ПО ДИФФИ-ХЕЛЛМАНУ")
    print("-" * 60)
    print("\nПротокол позволяет двум сторонам выработать общий секретный ключ")
    print("по открытому каналу связи, не передавая сам ключ.")
    print("\nФормулы:")
    print("  Ya = a^Ka mod n  (открытый ключ Алисы)")
    print("  Yb = a^Kb mod n  (открытый ключ Боба)")
    print("  S  = Yb^Ka mod n = Ya^Kb mod n  (общий секрет)")
    
    print("\n" + "-" * 40)
    print("ПАРАМЕТРЫ ПРОТОКОЛА")
    print("-" * 40)

    n = input_with_constraints(
         "Введите простой модуль n", 
        min_val=3, 
        is_prime_needed=True
    )
    print(f"[Инфо] Принято: n = {n}")

    a = input_with_constraints(
        "Введите генератор (базу) a", 
        min_val=2, 
        max_val=n-1
    )
    print(f"[Инфо] Принято: a = {a}")

    print("\n" + "-" * 40)
    print("[АЛИСА]")
    print("-" * 40)

    Ka = input_with_constraints(
        "Введите секретный ключ Алисы Ka", 
        min_val=2, 
        max_val=n-1
    )
    Ya = pow(a, Ka, n)

    if Ya == 1:
        print("[Ошибка] Открытый ключ Алисы не должен быть равен 1")
        return
    print(f"[Инфо] Открытый ключ Алисы: Ya = a^Ka mod n = {Ya}")

    print("\n" + "-" * 40)
    print("[БОБ]")
    print("-" * 40)

    Kb = input_with_constraints(
        "Введите секретный ключ Боба Kb", 
        min_val=2, 
        max_val=n-1
    )
    Yb = pow(a, Kb, n)

    if Yb == 1:
        print("[Ошибка] Открытый ключ Боба не должен быть равен 1")
        return
    print(f"[Инфо] Открытый ключ Боба: Yb = a^Kb mod n = {Yb}")

    print("\n" + "-" * 40)
    print("ВЫЧИСЛЕНИЕ ОБЩЕГО СЕКРЕТА")
    print("-" * 40)

    print(f"[Алиса] Вычисляет: S = Yb^Ka mod n")
    A = pow(Yb, Ka, n)
    print(f"  Результат: {A}")

    print(f"[Боб] Вычисляет: S = Ya^Kb mod n")
    B = pow(Ya, Kb, n)
    print(f"  Результат: {B}")

    dangerous_values = [1, Ka, Kb, Ya, Yb]
    if A in dangerous_values or B in dangerous_values:
        print("\n[Внимание] Общий секрет совпадает с одним из ключей!")
        print("[Внимание] Рекомендуется выбрать другие параметры.")

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ")
    print("=" * 60)

    if A == B:
        print("[Успех] Общие секреты совпадают!")
        print(f"Общий секретный ключ: {A}")
        print("\n[Инфо] Этот ключ можно использовать для симметричного шифрования.")
    else:
        print("[Ошибка] Общие секреты НЕ совпадают!")
        print("  Проверьте корректность введённых параметров.")

    print("=" * 60)

def main():
    print("=" * 60)
    print("ОБМЕН КЛЮЧАМИ ПО ДИФФИ-ХЕЛЛМАНУ")
    print("=" * 60)
    demo = input("\nПоказать демонстрацию работы? (д/н):").strip().lower()
    if demo in ['д', 'y', 'yes', '']:
        demo_diffie_hellman()

    while True:
        print("\n" + "-" * 40)
        print("МЕНЮ")
        print("-" * 40)
        print("1 - Выполнить обмен ключами")
        print("0 - Выход")
        print("-" * 40)
        
        choice = input("\nВаш выбор:").strip()
        
        if choice == '0':
            print("\n[Инфо] Программа завершена")
            print("=" * 60)
            break
        elif choice == '1':
            diffie_hellman()
        else:
            print("[Ошибка] Неверный выбор, попробуйте снова")

if __name__ == "__main__":
    main()