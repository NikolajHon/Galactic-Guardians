import os
from http.client import responses

from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Define request body schema
class ChatRequest(BaseModel):
    message: str

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")  # This is the default and can be omitted
)


@app.post("/chat")
async def chat_with_gpt(request: ChatRequest):
    try:

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-4",
        )

        return {"response": chat_completion.choices[0].message['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))