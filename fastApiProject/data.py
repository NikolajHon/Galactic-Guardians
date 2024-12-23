import json
import os
import re

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

    def choose_dataset(self, question):
        datasets_folder = 'datasets'  # Путь к папке с датасетами
        dataframes = {}  # Словарь для хранения DataFrame
        columns_info = {}  # Словарь для хранения информации о колонках

        # Загрузка всех CSV файлов из папки
        for file_name in os.listdir(datasets_folder):
            if file_name.endswith('.csv'):
                file_path = os.path.join(datasets_folder, file_name)
                try:
                    df = pd.read_csv(file_path)
                    # Сохраняем DataFrame и его колонки
                    dataframes[file_name] = df
                    columns_info[file_name] = list(df.columns)
                except Exception as e:
                    print(f"Ошибка при обработке файла {file_name}: {e}")

        # Сбор информации о колонках в одну строку
        result = f"Question: {question}\nAvailable datasets and columns: "
        result += " | ".join([f"File: {file_name}, Columns: {columns}" for file_name, columns in columns_info.items()])
        prompt = (
            f"Hello, customer have this question '{question}'\n"
            f"Here you have list of available datasets and collums of this datasets:\n{result}\n\n"
            f"Analyse this list abd decide which dataset match better then other for our question. but there may be a situation where the question does not apply to any of the dates, then write “0”. in the end write number of dataframe whice we choose .you have to find a clear connection between the question and the dataset. .\n"

        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        print("WE ARE IN FUNCTION")
        content = response.choices[0].message.content.strip()
        if content == 'no':
            return 0
        number = int(re.search(r'\d+', content).group())
        return number

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

            try:
                result = json.loads(content)
                analysis = result.get("analysis", "No analysis provided.")
                chart = result.get("chart", {})
                chart_type = result.get("chartType", "bar")
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

