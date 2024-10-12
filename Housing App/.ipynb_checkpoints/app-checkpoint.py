from fastapi import FastAPI
from pydantic import BaseModel
import model
import database
import requests

app = FastAPI()

class PropertyInput(BaseModel):
    bedrooms: int
    bathrooms: int
    sqft: float
    location: str

@app.post("/predict")
def predict_price(property: PropertyInput):
    # Ambil data dari API publik
    user_data = requests.get("https://randomuser.me/api/").json()
    user_id = user_data['results'][0]['login']['uuid']

    # Prediksi harga rumah
    predicted_price = model.predict(property.bedrooms, property.bathrooms,
                                    property.sqft, property.location)

    # Simpan ke MongoDB
    database.save_to_db(user_id, property.dict(), predicted_price)

    return {"user_id": user_id, "predicted_price": predicted_price}

@app.get("/stats")
def get_stats():
    # Ambil statistik dataset
    stats = model.get_statistics()
    return stats
