import os
from http.client import responses

from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
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