import pandas as pd
import pandasql as psql
import openai
from openai import OpenAI


class DataFrameSQLProcessor:
    def __init__(self, api_key):
        """
        Инициализирует процессор с API-ключом OpenAI.
        :param api_key: API-ключ для доступа к OpenAI.
        """
        openai.api_key = api_key
        self.df = None

    def load_csv(self, file_path):
        """
        Загружает CSV-файл в DataFrame и сохраняет его.
        :param file_path: Путь к CSV-файлу.
        """
        self.df = pd.read_csv(file_path)
        print(f"CSV-файл успешно загружен. Колонки: {', '.join(self.df.columns)}")

    def ask_question(self, question):
        client = OpenAI(api_key="")
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
            response = client.chat.completions.create(
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
        print("Сгенерированный SQL-запрос:", sql_query)

        # Выполняем SQL-запрос
        try:
            result = psql.sqldf(sql_query, {"df": self.df})
            return result
        except Exception as e:
            print("Ошибка при выполнении SQL-запроса:", e)
            return None


if __name__ == "__main__":
    # Инициализируйте класс с вашим API-ключом OpenAI
    processor = DataFrameSQLProcessor(api_key="ваш_api_ключ")

    # Загрузка CSV-файла
    processor.load_csv("example.csv")

    # Задаем вопрос
    question = "Какие страны имеют наибольшую смертность от COVID-19 (по коэффициенту смертности Case_Fatality_Ratio)"
    result = processor.ask_question(question)

    # Выводим результат
    if result is not None:
        print(result)
