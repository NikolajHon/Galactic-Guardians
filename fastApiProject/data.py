import json
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
            sql_query = response.choices[0].message.content.strip()

            # Убираем лишний текст, если присутствует
            if "```" in sql_query:
                sql_query = sql_query.split("```")[1].strip()
            print(f"Сгенерированный SQL-запрос:\n{sql_query}")
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

    def get_analyze(self, dataset_json, question):
        try:
            dataset_str = json.dumps(dataset_json, indent=2)

            prompt = (
                f"You are an expert data analyst.\n"
                f"Here is the dataset (in JSON format):\n{dataset_str}\n\n"
                f"The user asks: '{question}'.\n"
                f"Provide a detailed analysis based on the data, "
                f"and determine the most appropriate chart type for visualizing the data (choose from scatter, line, bar, pie, or doughnut). "
                f"Then generate configuration for a chart.js chart, including the type, labels, datasets, and a legend.\n"
                f"Format the output as a JSON object with three keys: "
                f"'analysis' (textual analysis), 'chart' (chart configuration), and 'chartType' (the suggested chart type)."
                f"The 'chart' configuration should include 'labels', 'datasets', and a 'legend'."
            )

            # Синхронный вызов OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )

            # Извлекаем текст ответа
            content = response.choices[0].message.content.strip()

            # Парсим JSON-ответ
            try:
                result = json.loads(content)
                analysis = result.get("analysis", "No analysis provided.")
                chart = result.get("chart", {})
                chart_type = result.get("chartType", "bar")  # По умолчанию 'bar', если тип не указан
            except json.JSONDecodeError:
                raise ValueError("Failed to parse chart configuration. Check the AI response format.")

            return {
                "analysis": analysis,
                "chartType": chart_type,
                "chart": chart

            }

        except Exception as e:
            print(f"Error in analysis generation: {e}")
            return {
                "analysis": "An error occurred while analyzing the data. Please try again.",
                "chartType": "bar",
                "chart": {}
            }

