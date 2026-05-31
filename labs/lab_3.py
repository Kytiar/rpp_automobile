import os
import csv
from datetime import datetime

def count_files(directory):
    """Подсчитывает количество файлов в указанной директории."""
    try:
        return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])
    except FileNotFoundError:
        print(f"Директория '{directory}' не найдена.")
        return 0
    except Exception as e:
        print(f"Ошибка при подсчете файлов в директории: {e}")
        return 0

def read_csv(filename):
    """Читает данные из CSV-файла."""
    try:
        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            data = list(reader)
            return data
    except FileNotFoundError:
        print("Файл не найден.")
        return []
    except Exception as e:
        print("Ошибка чтения файла:", e)
        return []

def sort_data(data, key, reverse=False):
    """Сортирует данные по указанному ключу."""
    return sorted(data, key=lambda x: x[key], reverse=reverse)

def filter_by_plate(data):
    """Фильтрует данные по номерному знаку, начинающемуся с 'А'."""
    return [entry for entry in data if entry['Номерной знак'].startswith('А')]

def save_csv(data, filename):
    """Сохраняет данные в CSV-файл."""
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            fieldnames = ["№", "Дата и время", "Номерной знак", "Марка автомобиля"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Данные успешно сохранены в {filename}")
    except Exception as e:
        print("Ошибка записи файла:", e)

def print_data(data):
    """Выводит данные в консоль."""
    for entry in data:
        print(entry)

def get_valid_date_time():
    """Получает валидную дату и время от пользователя."""
    while True:
        date_time_str = input("Введите дату и время (формат: dd.mm.yyyy HH:MM): ")
        try:
            datetime.strptime(date_time_str, "%d.%m.%Y %H:%M")
            return date_time_str
        except ValueError:
            print("Неверный формат даты и времени. Пожалуйста, используйте формат dd.mm.yyyy HH:MM")

def get_valid_number():
    """Получает валидный номер от пользователя (только цифры)."""
    while True:
        number_str = input("Введите номер: ")
        if number_str.isdigit():
            return number_str
        else:
            print("Неверный формат номера. Номер должен содержать только цифры.")

directory = input("Введите путь к директории: ")
file_count = count_files(directory)
print("Количество файлов в директории:", file_count)

filename = "data.csv"
data = read_csv(filename)

while True:
    print("\nВыберите действие:")
    print("1. Сортировка по марке автомобиля")
    print("2. Сортировка по номеру")
    print("3. Фильтрация по номерному знаку (начинается с 'А')")
    print("4. Ввод новых данных")
    print("5. Вывод всех данных")
    print("6. Выход")

    choice = input("Введите номер действия: ")

    if choice == "1":
        sorted_data = sort_data(data, "Марка автомобиля")
        print_data(sorted_data)
    elif choice == "2":
        sorted_data = sort_data(data, "№")
        print_data(sorted_data)
    elif choice == "3":
        filtered_data = filter_by_plate(data)
        print_data(filtered_data)
    elif choice == "4":
        while True:
            number = get_valid_number()
            date_time = get_valid_date_time()
            plate = input("Введите номерной знак: ")
            car_make = input("Введите марку автомобиля: ")

            new_entry = {
                "№": number,
                "Дата и время": date_time,
                "Номерной знак": plate,
                "Марка автомобиля": car_make
            }
            data.append(new_entry)
            save_csv(data, filename)

            another = input("Хотите ввести еще одну запись? (да/нет): ").lower()
            if another != "да":
                break

    elif choice == "5":
        print_data(data)
    elif choice == "6":
        print("Выход из программы.")
        break
    else:
        print("Неверный ввод. Пожалуйста, выберите действие из списка.")
