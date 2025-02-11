import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Добавление столбца position, если его ещё нет
try:
    cursor.execute("ALTER TABLE parsed_data ADD COLUMN position INTEGER")
except sqlite3.OperationalError:
    print("Столбец 'position' уже существует.")

# Получение всех уникальных категорий (query) в порядке их появления
cursor.execute("SELECT DISTINCT query FROM parsed_data ORDER BY rowid")
categories = [row[0] for row in cursor.fetchall()]

# Начальное смещение
offset = 0

# Обновляем позиции для каждой категории
for category in categories:
    # Обновляем позицию с учётом текущего смещения
    cursor.execute("""
        UPDATE parsed_data
        SET position = rowid - ?
        WHERE query = ?
    """, (offset, category))
    
    # Считаем количество строк в текущей категории
    cursor.execute("SELECT COUNT(*) FROM parsed_data WHERE query = ?", (category,))
    count = cursor.fetchone()[0]
    
    # Увеличиваем смещение
    offset += count

# Сохранение изменений
conn.commit()

# Проверка результатов
cursor.execute("SELECT query, rowid, position FROM parsed_data ORDER BY rowid")
rows = cursor.fetchall()
print("Данные с обновлёнными позициями:")
for row in rows:
    print(row)

# Закрытие подключения
conn.close()