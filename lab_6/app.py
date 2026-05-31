import cherrypy
import sqlite3
import csv
import re
from datetime import datetime
from models import create_db, csv_to_db, is_db_empty

print("Запуск app.py...")


class CarsApp:
    @cherrypy.expose
    def index(self, sort_by='id', order='asc'):
        """Отображает список проездов автомобилей."""

        if sort_by not in ['id', 'date_time', 'license_plate', 'car_brand']:
            sort_by = 'id'
        if order not in ['asc', 'desc']:
            order = 'asc'

        try:
            conn = sqlite3.connect('cars.db')
            cursor = conn.cursor()
            sql = "SELECT * FROM car_passes ORDER BY {} {}".format(sort_by, order.upper())
            cursor.execute(sql)
            passes = cursor.fetchall()
            conn.close()
        except Exception as e:
            return f"Ошибка при получении данных из базы данных: {e}"

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='UTF-8'>
            <title>Список проездов автомобилей</title>
            <style>
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
        <h1>Список проездов автомобилей</h1>
        <a href='/add'>Добавить проезд</a>
        <form method='GET'>
            Сортировать по:
            <select name='sort_by'>
                <option value='id'>ID</option>
                <option value='date_time'>Дата и время</option>
                <option value='license_plate'>Номерной знак</option>
                <option value='car_brand'>Марка автомобиля</option>
            </select>
            Направление сортировки:
            <select name='order'>
                <option value='asc'>По возрастанию</option>
                <option value='desc'>По убыванию</option>
            </select>
            <button type='submit'>Сортировать</button>
        </form>
        <table>
            <tr>
                <th>ID</th>
                <th>Дата и время</th>
                <th>Номерной знак</th>
                <th>Марка автомобиля</th>
                <th>Действия</th>
            </tr>
        """

        for car_pass in passes:
            # Форматируем дату в российский формат (дд.мм.гггг чч:мм)
            date_time = datetime.strptime(car_pass[1], '%Y-%m-%d %H:%M:%S')
            formatted_date = date_time.strftime('%d.%m.%Y %H:%M')

            html += f"""
            <tr>
                <td>{car_pass[0]}</td>
                <td>{formatted_date}</td>
                <td>{car_pass[2]}</td>
                <td>{car_pass[3]}</td>
                <td>
                    <a href='/edit/{car_pass[0]}'>Редактировать</a>
                    <a href='/delete/{car_pass[0]}'>Удалить</a>
                </td>
            </tr>
            """
        html += """
        </table>
        </body>
        </html>
        """
        return html

    @cherrypy.expose
    def add(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='UTF-8'>
            <title>Добавить проезд</title>
        </head>
        <body>
        <h1>Добавить проезд</h1>
        <form method='POST' action='save'>
            Дата и время: <input type='datetime-local' name='date_time'><br>
            Номерной знак (формат: А123БВ45 или А123БВ456): <input type='text' name='license_plate'><br>
            Марка автомобиля: <input type='text' name='car_brand'><br>
            <button type='submit'>Сохранить</button>
        </form>
        </body>
        </html>
        """

    @cherrypy.expose
    def save(self, date_time, license_plate, car_brand):
        # Валидация номерного знака (российский формат)
        if not self.validate_russian_license_plate(license_plate):
            return "Ошибка: Номерной знак должен соответствовать российскому формату (например: А123БВ45 или А123БВ456)."

        # Преобразуем дату в формат БД (гггг-мм-дд чч:мм:сс)
        try:
            dt = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')
            db_date_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return "Ошибка: Неверный формат даты и времени."

        try:
            conn = sqlite3.connect('cars.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO car_passes (date_time, license_plate, car_brand) VALUES (?, ?, ?)",
                           (db_date_time, license_plate.upper(), car_brand))
            conn.commit()
            conn.close()
        except Exception as e:
            return f"Ошибка при сохранении проезда: {e}"
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def edit(self, id):
        try:
            conn = sqlite3.connect('cars.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM car_passes WHERE id = ?", (id,))
            car_pass = cursor.fetchone()
            conn.close()
        except Exception as e:
            return f"Ошибка при получении данных проезда для редактирования: {e}"

        if not car_pass:
            return "Проезд не найден"

        # Преобразуем дату из БД в формат для input[type=datetime-local]
        db_date = datetime.strptime(car_pass[1], '%Y-%m-%d %H:%M:%S')
        input_date = db_date.strftime('%Y-%m-%dT%H:%M')

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='UTF-8'>
            <title>Редактировать проезд</title>
        </head>
        <body>
        <h1>Редактировать проезд</h1>
        <form method='POST' action='/update/{id}'>
            Дата и время: <input type='datetime-local' name='date_time' value='{input_date}'><br>
            Номерной знак: <input type='text' name='license_plate' value='{car_pass[2]}'><br>
            Марка автомобиля: <input type='text' name='car_brand' value='{car_pass[3]}'><br>
            <button type='submit'>Обновить</button>
        </form>
        </body>
        </html>
        """

    @cherrypy.expose
    def update(self, id, date_time, license_plate, car_brand):
        if not self.validate_russian_license_plate(license_plate):
            return "Ошибка: Номерной знак должен соответствовать российскому формату (например: А123БВ45 или А123БВ456)."

        try:
            dt = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')
            db_date_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return "Ошибка: Неверный формат даты и времени."

        try:
            conn = sqlite3.connect('cars.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE car_passes SET date_time=?, license_plate=?, car_brand=? WHERE id=?",
                           (db_date_time, license_plate.upper(), car_brand, id))
            conn.commit()
            conn.close()
        except Exception as e:
            return f"Ошибка при обновлении проезда: {e}"
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def delete(self, id):
        try:
            conn = sqlite3.connect('cars.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM car_passes WHERE id=?", (id,))
            conn.commit()
            conn.close()
        except Exception as e:
            return f"Ошибка при удалении проезда: {e}"
        raise cherrypy.HTTPRedirect("/")

    def validate_russian_license_plate(self, plate):
        """Проверяет российский номерной знак."""
        # Российские форматы: А123БВ45 или А123БВ456
        pattern = r'^[АВЕКМНОРСТУХавекмнорстух]{1}\d{3}[АВЕКМНОРСТУХавекмнорстух]{2}\d{2,3}$'
        return re.match(pattern, plate) is not None


if __name__ == '__main__':
    cherrypy.config.update({
        'environment': 'embedded',
        'tools.encode.on': True,
        'tools.encode.encoding': 'utf-8',
        'server.socket_host': '127.0.0.1',  # Или '0.0.0.0' для доступа извне
        'server.socket_port': 8082,
    })
    print("Конфигурация CherryPy обновлена.")
    try:
        cherrypy.quickstart(CarsApp())
        print("CherryPy запущена!")
    except Exception as e:
        print(f"Произошла ошибка при запуске CherryPy: {e}")