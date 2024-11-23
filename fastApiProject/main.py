import os
from http.client import responses
from io import BytesIO

from openai import OpenAI
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd

from data import Data

# Initialize FastAPI app
app = FastAPI()
load_dotenv()

# Define request body schema
class ChatRequest(BaseModel):
    message: str

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.post("/chat")
async def chat_with_gpt(request: ChatRequest):
    try:

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": request.message,
                }
            ],
            model="gpt-3.5-turbo",
        )

        return {"response": chat_completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

data = Data()
data.open_csv("datasets/Cleaned_Students_Performance.csv")

