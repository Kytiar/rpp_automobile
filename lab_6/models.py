import sqlite3
import csv
from datetime import datetime
import os

DATABASE = 'cars.db'


def create_db():
    try:
        # Удаляем старый файл базы данных, если он существует и поврежден
        if os.path.exists(DATABASE):
            os.remove(DATABASE)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_passes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_time TEXT,
                license_plate TEXT,
                car_brand TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("База данных успешно создана.")
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        raise


def csv_to_db(filename="data.csv"):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Проверяем существует ли файл CSV
        if not os.path.exists(filename):
            print(f"Файл {filename} не найден. Пропускаем импорт данных.")
            return

        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'date_time' not in row or 'license_plate' not in row or 'car_brand' not in row:
                    print("Ошибка: Неверный формат CSV. Проверьте заголовки.")
                    continue

                try:
                    # Преобразуем дату из российского формата (дд.мм.гггг чч:мм) в SQL формат
                    date_time = datetime.strptime(row['date_time'], '%d.%m.%Y %H:%M')
                    db_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    print(f"Неверный формат даты и времени: {row['date_time']}. Ошибка: {e}")
                    continue

                cursor.execute("""
                    INSERT INTO car_passes (date_time, license_plate, car_brand)
                    VALUES (?, ?, ?)
                """, (db_date_time, row['license_plate'].upper(), row['car_brand']))

        conn.commit()
        conn.close()
        print("Данные из CSV успешно импортированы.")
    except Exception as e:
        print(f"Ошибка при импорте данных из CSV: {e}")
        raise


def is_db_empty():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM car_passes")
        count = cursor.fetchone()[0]
        conn.close()
        return count == 0
    except Exception as e:
        print(f"Ошибка при проверке базы данных: {e}")
        return True  # Считаем базу пустой в случае ошибки


if __name__ == '__main__':
    try:
        create_db()
        csv_to_db()
    except Exception as e:
        print(f"Критическая ошибка: {e}")