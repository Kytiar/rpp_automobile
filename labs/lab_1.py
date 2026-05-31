import random

def input_list(prompt):
    while True:
        try:
            user_input = input(prompt)
            numbers = [int(x) for x in user_input.split()]
            return numbers
        except ValueError:
            print("Некорректный ввод. Пожалуйста, введите целые числа через пробел.")

def generate(size, lower, upper):
    return [random.randint(lower, upper) for _ in range(size)]

def remove_even(A, B):
    result = []
    current = []
    for num in A:
        if num % 2 == 0:
            current.append(num)
        else:
            if current and not any(x in B for x in current):
                result.extend(current)
            result.append(num)
            current = []
    if current and not any(x in B for x in current):
        result.extend(current)
    return result

def remove_even_alt(A, B):
    result = []
    current = []
    for num in A:
        if num % 2 == 0:
            current.append(num)
        else:
            if current:
                has_element_from_B = False
                for elem in current:
                    for b in B:
                        if elem == b:
                            has_element_from_B = True
                            break
                    if has_element_from_B:
                        break
                if not has_element_from_B:
                    result.extend(current)
            result.append(num)
            current = []
    if current:
        has_element_from_B = False
        for elem in current:
            for b in B:
                if elem == b:
                    has_element_from_B = True
                    break
            if has_element_from_B:
                break
        if not has_element_from_B:
            result.extend(current)
    return result

def main():
    print("Выберите, хотите ли вы ввести список A вручную или сгенерировать его автоматически.")
    print("1. Ввести список A вручную")
    print("2. Сгенерировать список A автоматически")
    choice = input("Введите ваш выбор: ")
    if choice == "1":
        A = input_list("Введите список A через пробел: ")
    elif choice == "2":
        size = int(input("Введите размер списка A: "))
        lower = int(input("Введите нижнюю границу значений: "))
        upper = int(input("Введите верхнюю границу значений: "))
        A = generate(size, lower, upper)
        print("Сгенерированный список A:", A)
    else:
        print("Некорректный выбор. Выход из программы.")
        return

    B = input_list("Введите список B через пробел: ")

    result_with_std_func = remove_even(A, B)
    result_without_std_func = remove_even_alt(A, B)

    print("Результат с использованием стандартных функций:", result_with_std_func)
    print("Результат без использования стандартных функций:", result_without_std_func)

main()
