from pydantic import BaseModel

# Define request body schema
class ChatRequest(BaseModel):
    message: str