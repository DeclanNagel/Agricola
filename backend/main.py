from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot import agricola_chat
from irrRec import get_weather_by_city
from fastapi.middleware.cors import CORSMiddleware
import joblib
import os
import json
import xgboost as xgb
import pandas as pd

app = FastAPI()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_health_model.pkl")
crop_model = joblib.load(MODEL_PATH)

script_dir = os.path.dirname(__file__)
json_path = os.path.join(script_dir, "farm_econ_data.json")

with open(json_path) as f:
    economic_data = json.load(f)

model = xgb.XGBRegressor()
model.load_model("revenue_forecast_model.json")
feature_order = joblib.load("revenue_feature_order.pkl")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CropInput(BaseModel):
    week: int
    yield_kg: float
    price_per_kg: float
    cost: float
    crop: str  

class WeeklyReportInput(BaseModel):
    temp: float
    rainfall: float
    moisture: float
    last_watered: int
    watering_event: bool

class ChatInput(BaseModel):
    message: str

class IrrigationInput(BaseModel):
    crop: str
    temperature: float
    moisture_level: float
    rainful: float
    last_watered_days_ago: int
    location: str

@app.post("/chatbot")
async def chatbot_endpoint(input: ChatInput):
    reply = agricola_chat(input.message)
    return {"response": reply}

@app.post("/irr_rec")
async def irrigation_recommendation(input: IrrigationInput):
    #LLM logic
    weather, temp = get_weather_by_city(input.location)

    if weather is None:
        return {"Error": "could not receive weather data"}
    
    prompt = (
        f"I am growing {input.crop} in {input.location}. "
        f"The weather today is {weather} with a temperature of {temp}°C. "
        f"Soil moisture level is {input.moisture_level}, rainfall is {input.rainful} mm, "
        f"and the crop was last watered {input.last_watered_days_ago} days ago. "
        f"What irrigation advice do you have?"
    )

    advice = agricola_chat(prompt)
    return {"advice": advice}
    
@app.post("/weekly_report")
async def weekly_crop_health_prediction(input: WeeklyReportInput):
    input_data = [[
        input.temp,
        input.rainfall,
        input.moisture,
        input.last_watered,
        int(input.watering_event)
    ]]

    prediction = crop_model.predict(input_data)[0]

    report = (
        f"This week’s crop health is predicted to be: **{prediction}**.\n\n"
        f"Conditions:\n"
        f"🌡 Temperature: {input.temp}°C\n"
        f"🌧 Rainfall: {input.rainfall} mm\n"
        f"💧 Soil Moisture: {input.moisture}%\n"
        f"🚿 Last Watered: {input.last_watered} days ago\n"
        f"🪣 Watering Event Today: {'Yes' if input.watering_event else 'No'}"
    )

    return {
        "prediction": prediction,
        "report": report
    }

@app.get("/econ")
async def get_farm_econ_data():
    total_revenue = 0
    total_cost = 0
    crop_list = []

    for crop in economic_data:
        curr_revenue = crop["yield_kg"] * crop["price_per_kg"]
        curr_cost = crop["cost"]
        profit = curr_revenue - curr_cost
        
        total_revenue += curr_revenue
        total_cost += curr_cost

        crop_list.append({
            "crop": crop["crop"],
            "yield_kg": crop["yield_kg"],
            "price_per_kg": crop["price_per_kg"],
            "revenue": curr_revenue,
            "cost": curr_cost,
            "profit": profit
        })

    return {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_revenue - total_cost,
        "roi": round((total_revenue - total_cost) / total_cost, 2),
        "crops": crop_list
    }

@app.post("/predict-revenue")
def predict_revenue(data: CropInput):
    crops = ["Wheat", "Corn", "Tomatoes", "Lettuce", "Potatoes"]
    crop_encoding = {f"crop_{c}": 1 if c == data.crop else 0 for c in crops}

    features = {
        "week": data.week,
        "yield_kg": data.yield_kg,
        "price_per_kg": data.price_per_kg,
        "cost": data.cost,
        **crop_encoding
    }

    df = pd.DataFrame([features])
    df = df[feature_order]
    prediction = model.predict(df)[0]
    
    return {"predicted_revenue": float(prediction)}