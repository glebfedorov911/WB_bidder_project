import torch
import numpy as np
from sklearn.preprocessing import StandardScaler
import sqlite3
import torch.nn as nn

# Подключаемся к базе данных SQLite
conn = sqlite3.connect("jeans2.db")  # Поменяйте на имя вашего файла базы данных
cursor = conn.cursor()

# Извлекаем данные для тестирования (например, с 1000 строки)
cursor.execute(
    "SELECT from_value, price, query,  marks, count_marks, fbo,num_of_the_rating  FROM parser_data ORDER BY marks LIMIT 1000000 OFFSET 15208"
)
test_data = cursor.fetchall()

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

for row in test_data:
    from_value = row[0]  # from_value
    price = row[1]  # price (это наш CPM)
    query = row[2]  # query
    mark = clean_number_string(row[3])  # marks
    count_mark = row[4]  # count_marks
    fbo_value = row[5]  # fbo
    num_of_the_rating_value = row[6]  # num_of_the_rating

    try:
        from_values.append(float(from_value))
        prices.append(float(price))  # Целевая переменная (CPM)
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

# Создаем словарь для One-Hot Encoding
unique_queries = list(set(queries))  # Находим уникальные значения в 'query'
query_to_index = {
    query: idx for idx, query in enumerate(unique_queries)
}  # Словарь для индексации

# Преобразуем 'query' в индексы для слоя Embedding
query_indices = np.array([query_to_index[query] for query in queries])

# Нормализация данных
scaler = StandardScaler()
from_values = scaler.fit_transform(
    from_values.reshape(-1, 1)
)  # Нормализация from_value
num_of_the_rating = scaler.fit_transform(
    num_of_the_rating.reshape(-1, 1)
)  # Нормализация num_of_the_rating
marks = scaler.fit_transform(marks.reshape(-1, 1))  # Нормализация marks
count_marks = scaler.fit_transform(
    count_marks.reshape(-1, 1)
)  # Нормализация count_marks
fbo = fbo.reshape(-1, 1)  # fbo не требует нормализации

# Строим матрицу признаков X и вектор целевых значений y
X = np.concatenate(
    [from_values, num_of_the_rating, marks, count_marks, fbo], axis=1
)  # Добавляем все признаки
y = prices  # Целевая переменная - CPM

# Преобразуем в тензоры PyTorch
X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32)
query_tensor = torch.tensor(query_indices, dtype=torch.long)  # Индексы для embedding


class NeuralNetworkModel(nn.Module):
    def __init__(self, num_queries, input_dim):
        super(NeuralNetworkModel, self).__init__()
        self.embedding = nn.Embedding(num_queries, 10)
        self.fc1 = nn.Linear(input_dim + 10, 128)  # Увеличиваем число узлов
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)

    def forward(self, x, query):
        embedded_query = self.embedding(query)
        x = torch.cat((x, embedded_query), dim=1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

import numpy as np
correlation = np.corrcoef(X.T, y)  # X - матрица признаков, y - целевая переменная
print(correlation)
# Загружаем модель
model = NeuralNetworkModel(num_queries=len(unique_queries), input_dim=X_tensor.shape[1])
model.load_state_dict(torch.load("model.pth"))
model.eval()

# Оценка модели
model.eval()
with torch.no_grad():
    predicted = model(X_tensor, query_tensor).squeeze()

# Печать нескольких предсказанных значений
print("Пример предсказаний (предсказанный CPM):")
for i in range(6):
    print(
        f"Предсказание: {predicted[i].item():.4f}, Реальное значение: {y_tensor[i].item():.4f}"
    )

# Тест на точность (например, MSE на тестовых данных)
from sklearn.metrics import mean_squared_error

mse = mean_squared_error(y_tensor.cpu().numpy(), predicted.cpu().numpy())
print(f"Mean Squared Error (MSE) на тестовых данных: {mse:.4f}")
