import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('jeans2.db')  # Замените 'data.db' на название вашего файла базы данных
cursor = conn.cursor()

# Пример: вывод текущих данных
cursor.execute("SELECT from_value, price, query FROM parser_data")  # Замените 'parsed_data' на название вашей таблицы
rows = cursor.fetchall()
print("Данные до обработки:")
for row in rows:
    print(row)

# Функция очистки значений
def clean_data():
    # Обновить from_value: удалить "с "
    cursor.execute("""
        UPDATE parser_data
        SET from_value = TRIM(REPLACE(from_value, 'c ', ''))
        WHERE from_value LIKE 'с %'
    """)
    
    # Обновить price: удалить "CPM " и "₽"
    cursor.execute("""
        UPDATE parser_data
        SET price = REPLACE(REPLACE(price, 'CPM ', ''), ' ₽', '')
        WHERE price LIKE 'CPM %'
    """)

    # Обновить query: оставить только текст после знака "="
    cursor.execute("""
        UPDATE parser_data
        SET query = SUBSTR(query, INSTR(query, '=') + 1)
        WHERE query LIKE '%=%'
    """)

    conn.commit()

# Очистка данных
clean_data()

# Проверка изменений
cursor.execute("SELECT from_value, price, query FROM parser_data")
rows = cursor.fetchall()
print("Данные после обработки:")
for row in rows:
    print(row)

# Закрытие подключения
conn.close()