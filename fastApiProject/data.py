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
        Отправляет вопрос и список колонок в ChatGPT, получает SQL-запрос и выполняет его.
        :param question: Вопрос пользователя.
        :return: DataFrame с результатами SQL-запроса.
        """
        if self.df is None:
            raise ValueError("Сначала загрузите CSV-файл с помощью load_csv().")

        # Формируем список колонок
        columns = ", ".join(self.df.columns)

        # Формируем запрос к ChatGPT
        prompt = (
            f"Данный CSV-файл содержит следующие колонки: {columns}.\n"
            f"Пользователь спрашивает: '{question}'.\n"
            f"Пожалуйста, сгенерируйте соответствующий SQL-запрос для ответа на этот вопрос."
        )

        try:
            # Отправка запроса к модели
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            # Извлечение и возврат ответа
            return response.choices[0].message.content
        except Exception as e:
            return f"Произошла ошибка: {e}"

        # Получаем сгенерированный SQL-запрос
        sql_query = response["choices"][0]["message"]["content"].strip()
        print(f"Сгенерированный SQL-запрос:,: {sql_query}")


    def retrieve_data(self, sql_query):
        try:
            result = psql.sqldf(sql_query, {"df": self.df})
            return result
        except Exception as e:
            print("Ошибка при выполнении SQL-запроса:", e)
            return None