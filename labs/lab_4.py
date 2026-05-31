import os
import csv
from datetime import datetime

class VehicleDataError(Exception):
    """Пользовательское исключение для ошибок в данных об автомобилях."""
    pass

class Vehicle:
    """Базовый класс для представления автомобиля."""
    def __init__(self, number, date_time, plate, car_make):
        self.number = number
        self.date_time = date_time
        self.plate = plate
        self.car_make = car_make

    def __repr__(self):
        return f"{self.__class__.__name__}(№={self.number}, Дата={self.date_time}, Номер={self.plate}, Марка={self.car_make})"

    def __str__(self):
        return f"Автомобиль: Номер - {self.number}, Дата и время - {self.date_time}, Номерной знак - {self.plate}, Марка - {self.car_make}"

    def __setattr__(self, name, value):
        """Запись значений в свойства только через эту функцию."""
        if name == 'number' and not isinstance(value, (int, str)):
            raise ValueError("Номер должен быть числом или строкой.")
        if name == 'date_time':
            try:
                datetime.strptime(value, "%d.%m.%Y %H:%M")  # Валидация формата даты
            except ValueError:
                raise ValueError("Неверный формат даты и времени. Используйте dd.mm.yyyy HH:MM")
        super().__setattr__(name, value)  # Вызываем метод родительского класса для фактической записи

    @staticmethod
    def is_valid_plate(plate):
        """Статический метод для проверки формата номерного знака (простой пример)."""
        return len(plate) >= 6  # Простая проверка длины

class VehicleCollection:
    """Класс для хранения коллекции автомобилей."""
    def __init__(self, filename="data.csv"):
        self.filename = filename
        self.vehicles = self.load_data()  # Загрузка данных при инициализации

    def load_data(self):
        """Загружает данные из CSV-файла и создает объекты Vehicle."""
        vehicles = []
        try:
            with open(self.filename, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        number = row['№']
                        date_time = row['Дата и время']
                        plate = row['Номерной знак']
                        car_make = row['Марка автомобиля']

                        # Проверка данных (можно усложнить)
                        if not number or not date_time or not plate or not car_make:
                            raise VehicleDataError("Некорректные данные в CSV файле.")

                        vehicle = Vehicle(number, date_time, plate, car_make)
                        vehicles.append(vehicle)
                    except VehicleDataError as e:
                        print(f"Ошибка при загрузке данных: {e}") #Обработка исключения VehicleDataError
                    except Exception as e:
                        print(f"Неизвестная ошибка при обработке строки CSV: {e}")
        except FileNotFoundError:
            print("Файл не найден.")
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
        return vehicles

    def save_data(self):
        """Сохраняет данные в CSV-файл."""
        try:
            with open(self.filename, "w", newline="", encoding="utf-8") as file:
                fieldnames = ["№", "Дата и время", "Номерной знак", "Марка автомобиля"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for vehicle in self.vehicles:
                    writer.writerow({
                        "№": vehicle.number,
                        "Дата и время": vehicle.date_time,
                        "Номерной знак": vehicle.plate,
                        "Марка автомобиля": vehicle.car_make
                    })
            print(f"Данные успешно сохранены в {self.filename}")
        except Exception as e:
            print(f"Ошибка записи файла: {e}")

    def add_vehicle(self, number, date_time, plate, car_make):
        """Добавляет автомобиль в коллекцию."""
        try:
            vehicle = Vehicle(number, date_time, plate, car_make)
            self.vehicles.append(vehicle)
        except ValueError as e:
            print(f"Ошибка при создании автомобиля: {e}")
            return False
        return True

    def __iter__(self):
        """Итератор для перебора автомобилей."""
        self.index = 0
        return self

    def __next__(self):
        """Метод для итератора."""
        if self.index < len(self.vehicles):
            vehicle = self.vehicles[self.index]
            self.index += 1
            return vehicle
        else:
            raise StopIteration

    def __getitem__(self, index):
        """Возвращает автомобиль по индексу."""
        if 0 <= index < len(self.vehicles):
            return self.vehicles[index]
        else:
            raise IndexError("Неверный индекс")

    def __len__(self):
        return len(self.vehicles)

    def sort_by_make(self, reverse=False):
      """Сортирует автомобили по марке."""
      self.vehicles.sort(key=lambda vehicle: vehicle.car_make, reverse=reverse)

    def filter_by_plate_start(self, start_char='А'):
        """Фильтрует автомобили по начальной букве номерного знака."""
        return [vehicle for vehicle in self.vehicles if vehicle.plate.startswith(start_char)]

    @staticmethod
    def generate_report(vehicles):
        """Генератор для создания отчета (простой пример)."""
        for vehicle in vehicles:
            yield f"Отчет: {vehicle.car_make} - {vehicle.plate}"


collection = VehicleCollection()

while True:
    print("\nВыберите действие:")
    print("1. Вывод всех данных")
    print("2. Сортировка по марке автомобиля")
    print("3. Фильтрация по номерному знаку (начинается с 'А')")
    print("4. Добавить новый автомобиль")
    print("5. Сгенерировать отчет")
    print("6. Выход")

    choice = input("Введите номер действия: ")

    if choice == "1":
        for vehicle in collection:
            print(vehicle)
        print(f"Всего автомобилей: {len(collection)}")
    elif choice == "2":
        collection.sort_by_make()
        print("Отсортировано по марке.")
    elif choice == "3":
        filtered = collection.filter_by_plate_start()
        for vehicle in filtered:
            print(vehicle)
    elif choice == "4":
        number = input("Введите номер: ")
        date_time = input("Введите дату и время (формат: dd.mm.yyyy HH:MM): ")
        plate = input("Введите номерной знак: ")
        car_make = input("Введите марку автомобиля: ")
        if collection.add_vehicle(number, date_time, plate, car_make):
            collection.save_data()
    elif choice == "5":
        for report_line in VehicleCollection.generate_report(collection.vehicles):  # Используем статический метод
            print(report_line)
    elif choice == "6":
        print("Выход.")
        break
    else:
        print("Неверный ввод.")
