from pymongo import MongoClient
import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client['housing_db']

def save_to_db(user_id, property_data, predicted_price):
    db.predictions.insert_one({
        "user_id": user_id,
        "property_data": property_data,
        "predicted_price": predicted_price,
        "timestamp": datetime.datetime.now()
    })
