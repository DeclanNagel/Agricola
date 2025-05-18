import requests

API_KEY = "6acbc3e75c2f449588665656241011"

def get_weather_by_city(city: str):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    res = requests.get(url).json()

    if "error" in res:
        print("Error:", res["error"]["message"])
        return None, None

    weather = res["current"]["condition"]["text"]
    temp = res["current"]["temp_c"]
    return weather, temp

#TEST
weather, temp = get_weather_by_city("Fresno")
print("Weather:", weather)
print("Temp (°C):", temp)