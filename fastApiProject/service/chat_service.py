import os

import openai
from openai import OpenAI


import os
import openai
from openai import OpenAI


class ChatGPTService:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def ask_chatgpt(self , question):
        client = OpenAI(api_key="OPENAI_API_KEY")
        try:
            # Отправка запроса к модели
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": question}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Произошла ошибка: {e}"
