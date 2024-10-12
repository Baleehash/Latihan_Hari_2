import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import pandas as pd

# Load dataset harga rumah
data = pd.read_csv("housing.csv")

# One-hot encode the "ocean_proximity" feature
encoder = OneHotEncoder(sparse_output=False)
encoded_proximity = encoder.fit_transform(data[["ocean_proximity"]])

# Pilih kolom yang sesuai dengan dataset
X = data[["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms", "population", "households", "median_income"]]

# Add encoded "ocean_proximity" to the features
X = np.concatenate([X, encoded_proximity], axis=1)
y = data["median_house_value"]

# Preprocessing
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

# Model
model = LinearRegression()
model.fit(X_train, y_train)

# Fungsi untuk prediksi berdasarkan input fitur
def predict(longitude, latitude, housing_median_age, total_rooms, total_bedrooms, population, households, median_income, ocean_proximity):
    # Encode the "ocean_proximity" feature
    encoded_proximity = encoder.transform([[ocean_proximity]])
    # Concatenate the input features with encoded proximity
    X_new = np.concatenate([[longitude, latitude, housing_median_age, total_rooms, total_bedrooms, population, households, median_income], encoded_proximity[0]])
    X_new_scaled = scaler.transform([X_new])
    return model.predict(X_new_scaled)[0]

# Fungsi untuk mendapatkan statistik
def get_statistics():
    return {
        "mean": np.mean(y),
        "median": np.median(y),
        "std_dev": np.std(y)
    }

# Contoh penggunaan prediksi
result = predict(-122.23, 37.88, 41.0, 880.0, 129.0, 322.0, 126.0, 8.3252, "NEAR BAY")
print("Predicted house price:", result)
