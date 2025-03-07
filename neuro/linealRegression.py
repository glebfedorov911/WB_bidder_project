import sqlite3
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb

# Подключаемся к базе данных SQLite
conn = sqlite3.connect("neuro/jeans2.db")
cursor = conn.cursor()

# Извлекаем данные для обучения
cursor.execute(
    "SELECT from_value, price, query, marks, count_marks, fbo, num_of_the_rating FROM parser_data ORDER BY marks"
)
data = cursor.fetchall()

# Закрываем соединение с БД
conn.close()


# Функция для очистки строк от неразрывных пробелов и других нецифровых символов
def clean_number_string(value):
    if value:
        return value.replace("\xa0", "").replace(" ", "").replace(",", ".")
    return value


# Преобразуем данные в numpy массивы
from_values = []
prices = []
queries = []
num_of_the_rating = []
marks = []
count_marks = []
fbo = []

for row in data:
    from_value = row[0]
    price = row[1]  # Целевая переменная
    query = row[2]
    mark = clean_number_string(row[3])
    count_mark = row[4]
    fbo_value = row[5]
    num_of_the_rating_value = row[6]

    try:
        from_values.append(float(from_value))
        prices.append(float(price))
        queries.append(query)
        num_of_the_rating.append(float(num_of_the_rating_value))
        marks.append(float(mark))
        count_marks.append(float(count_mark))
        fbo.append(int(fbo_value))
    except ValueError:
        print(f"Ошибка преобразования: {row}")

from_values = np.array(from_values)
prices = np.array(prices)
queries = np.array(queries)
num_of_the_rating = np.array(num_of_the_rating)
marks = np.array(marks)
count_marks = np.array(count_marks)
fbo = np.array(fbo)

# Создаем словарь для One-Hot Encoding или просто индексируем категории
unique_queries = list(set(queries))
query_to_index = {query: idx for idx, query in enumerate(unique_queries)}
query_indices = np.array([query_to_index[query] for query in queries])

# Нормализация данных
scaler = StandardScaler()
from_values = scaler.fit_transform(from_values.reshape(-1, 1))
num_of_the_rating = scaler.fit_transform(num_of_the_rating.reshape(-1, 1))
marks = scaler.fit_transform(marks.reshape(-1, 1))
count_marks = scaler.fit_transform(count_marks.reshape(-1, 1))
fbo = fbo.reshape(-1, 1)

# Объединяем признаки
X = np.concatenate([from_values, num_of_the_rating, marks, count_marks, fbo], axis=1)
y = prices

# Делим данные на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Преобразуем данные в формат DMatrix для XGBoost
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# Параметры модели XGBoost
params = {
    "objective": "reg:squarederror",  # Регрессия с MSE
    "max_depth": 6,  # Максимальная глубина дерева
    "eta": 0.1,  # Скорость обучения
    "eval_metric": "rmse",  # Метрика оценки
}

# Обучение модели
num_rounds = 100  # Количество итераций
evals = [(dtrain, "train"), (dtest, "eval")]
model = xgb.train(params, dtrain, num_rounds, evals, early_stopping_rounds=10)

# Предсказания
y_pred = model.predict(dtest)

# Оценка модели
from sklearn.metrics import mean_squared_error

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"RMSE на тестовой выборке: {rmse:.4f}")

# Сохранение модели
model.save_model("xgboost_model.json")
print("Модель сохранена!")

# Пример предсказаний
print("Пример предсказаний (первые 5):")
print("Предсказания:", y_pred[:5])
print("Реальные значения:", y_test[:5])
