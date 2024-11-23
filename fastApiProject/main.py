import os
from http.client import responses
from io import BytesIO

from openai import OpenAI
from fastapi import FastAPI, HTTPException, UploadFile, File
from dotenv import load_dotenv
import pandas as pd

from data import DataFrameSQLProcessor
from models import ChatRequest

# Initialize FastAPI app
app = FastAPI()
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
    SQProcessor.load_csv("datasets/Cleaned_Students_Performance.csv")
    return SQProcessor.retrieve_data( SQProcessor.generate_query(request.message) )

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