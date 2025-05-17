from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class ChatInput(BaseModel):
    message: str

class IrrigationInput(BaseModel):
    crop: str
    soil_moisture: float
    weather: str
    temp: float

@app.post("/chatbot")
async def chatbot_endpoint(input: ChatInput):
    user_prompt = input.message
    #chat bot LLM function
    return {"response": f"User said {user_prompt}"}

@app.post("/irr_rec")
async def irrigation_recommendation(input: IrrigationInput):
    #LLM logic
    return {"advice": f"Water your {input.crop} lightly due to {input.weather}"}