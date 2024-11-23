import os

import pandas as pd
import pandasql as psql
import openai
from openai import OpenAI

class DataFrameSQLProcessor:
    def __init__(self, client: OpenAI):
        self.client = client
        self.df = None

    def load_csv(self, file_path):

        self.df = pd.read_csv(file_path)
        print(f"CSV-file uploaded: {', '.join(self.df.columns)}")

    def generate_query(self, question):
        """
        Отправляет вопрос и список колонок с их уникальными значениями в ChatGPT,
        получает чистый SQL-запрос и возвращает его.
        :param question: Вопрос пользователя.
        :return: Сгенерированный SQL-запрос.
        """
        if self.df is None:
            raise ValueError("Сначала загрузите CSV-файл с помощью load_csv().")

        # Создаем список колонок и уникальных значений
        column_values = {col: self.df[col].unique().tolist() for col in self.df.columns}
        column_info = "\n".join([f"Колонка '{col}': {values}" for col, values in column_values.items()])

        # Формируем подсказку
        prompt = (
            f"У меня есть pandas DataFrame с именем 'df', содержащий следующие колонки и уникальные значения:\n"
            f"{column_info}\n\n"
            f"Пользователь спрашивает: '{question}'.\n"
            f"Пожалуйста, сгенерируйте SQL-запрос, который будет выполнен с помощью pandasql. "
            f"Верните только SQL-запрос без лишнего текста."
        )

        try:
            # Отправка запроса к модели
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            # Извлечение SQL-запроса
            sql_query = response["choices"][0]["message"]["content"].strip()

            # Убираем лишний текст, если присутствует
            if "```" in sql_query:
                sql_query = sql_query.split("```")[1].strip()
            return sql_query
        except Exception as e:
            return f"Произошла ошибка: {e}"

    def retrieve_data(self, sql_query):
        try:
            result = psql.sqldf(sql_query, {"df": self.df})
            return result
        except Exception as e:
            print("Ошибка при выполнении SQL-запроса:", e)
            return None