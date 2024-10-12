from fastapi import FastAPI
from pydantic import BaseModel
import model
import database
import requests

app = FastAPI()

class PropertyInput(BaseModel):
    longitude: float
    latitude: float
    housing_median_age: float
    total_rooms: int
    total_bedrooms: int
    population: int
    households: int
    median_income: float
    ocean_proximity: str


@app.post("/predict")
def predict_price(property: PropertyInput):
    # Ambil data dari API publik
    user_data = requests.get("https://randomuser.me/api/").json()
    user_id = user_data['results'][0]['login']['uuid']

    # Prediksi harga rumah
    predicted_price = model.predict(property.longitude, property.latitude,
                                    property.housing_median_age, property.total_rooms,
                                    property.total_bedrooms, property.population,
                                    property.households, property.median_income,
                                    property.ocean_proximity)

    # Simpan ke MongoDB
    database.save_to_db(user_id, property.dict(), predicted_price)

    return {"user_id": user_id, "predicted_price": predicted_price}

@app.get("/stats")
def get_stats():
    # Ambil statistik dataset
    stats = model.get_statistics()
    return stats
