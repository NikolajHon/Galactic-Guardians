import os
from http.client import responses
from io import BytesIO

from fastapi.encoders import jsonable_encoder
from openai import OpenAI
from fastapi import FastAPI, HTTPException, UploadFile, File
from dotenv import load_dotenv
import pandas as pd

from data import DataFrameSQLProcessor
from models import ChatRequest

# Initialize FastAPI app
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Разрешить запросы с указанного порта
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

load_dotenv()

client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
)

SQProcessor = DataFrameSQLProcessor(client)

@app.post("/chat")
async def get_SQL_request(request: ChatRequest):
    SQProcessor.load_csv("datasets/Cleaned_Students_Performance.csv")
    return SQProcessor.generate_query(request.message)


@app.post("/get_answer")
async def get_answer(request: ChatRequest):
    try:
        # Загружаем CSV-файл
        SQProcessor.load_csv("datasets/Cleaned_Students_Performance.csv")

        # Генерируем SQL-запрос
        sql_query = SQProcessor.generate_query(request.message)

        # Выполняем SQL-запрос и получаем результат
        result = SQProcessor.retrieve_data(sql_query)

        # Если результат пустой, возвращаем ошибку
        if result is None or result.empty:
            raise HTTPException(status_code=404, detail="No data found for the given query.")

        # Преобразуем DataFrame в сериализуемый формат
        response_data = result.to_dict(orient="records")
        return jsonable_encoder(response_data)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Общий обработчик ошибок
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/get_analyse")
async def get_analyse(request: ChatRequest):
    dataset_dir = "datasets"
    dataset_files = sorted(os.listdir(dataset_dir))

    dataset = SQProcessor.choose_dataset(request.message)

    # Проверяем валидность выбранного номера
    if dataset <= 0 or dataset > len(dataset_files):
        print(f"Invalid dataset number: {dataset}")
        return

    selected_file = os.path.join(dataset_dir, dataset_files[dataset - 1])
    print(f"We choose dataset {dataset}: {selected_file}")

    SQProcessor.load_csv(selected_file)

    sql_query = SQProcessor.generate_query(request.message)

    result = SQProcessor.retrieve_data(sql_query)
    if result.empty:
        return {"error": "No data retrieved for the query."}

    # Анализируем данные и вопрос
    analyses = SQProcessor.get_analyze(result.to_dict(orient="records"), request.message)  # Убрали await
    return {"analysis": analyses}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != "multipart/form-data":
        raise HTTPException( status_code=400, detail="Unsupported Media Type" )

    contents = await file.read()

    # Convert the content to a file-like object (BytesIO)
    file_like_object = BytesIO(contents)\

    try:
        # Load the CSV data into a pandas DataFrame
        df = pd.read_csv(file_like_object)

        # Return a summary of the CSV data (e.g., first 5 rows)
        return {"filename": file.filename, "first_rows": df.head().to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {e}")