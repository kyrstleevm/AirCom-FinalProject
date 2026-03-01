# Import Statements
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

# AQI Calculation
def calculate_aqi(pm25):
    if pd.isna(pm25) or pm25 < 0:
        return np.nan
    if pm25 <= 12.0:
        return ((50 - 0) / (12.0 - 0)) * (pm25 - 0) + 0
    elif pm25 <= 35.4:
        return ((100 - 51) / (35.4 - 12.1)) * (pm25 - 12.1) + 51
    elif pm25 <= 55.4:
        return ((150 - 101) / (55.4 - 35.5)) * (pm25 - 35.5) + 101
    elif pm25 <= 150.4:
        return ((200 - 151) / (150.4 - 55.5)) * (pm25 - 55.5) + 151
    elif pm25 <= 250.4:
        return ((300 - 201) / (250.4 - 150.5)) * (pm25 - 150.5) + 201
    elif pm25 <= 500.4:
        return ((500 - 301) / (500.4 - 250.5)) * (pm25 - 250.5) + 301
    else:
        # For values above 500, it's typically just capped at 500 or higher
        return 500

# Knowledge Base Multipliers

# Represents the weights of how much air a person breathes while doing these activities
ACTIVITY_WEIGHTS = {
    "resting": 1.0,     # baseline
    "walking": 2.5,
    "running": 5.0
}

# Biological sensitivity to ultrafine particles (UFP/PM0.1)
STATUS_WEIGHTS = {
    "healthy_adult": 1.0,    # baseline
    "child": 1.5,
    "elderly": 2.0,
    "asthmatic": 2.5
}

# Health Advisory
ADVICES = {
    "low": "Safe level of exposure. The air is fresh—ideal for any outdoor activity!",
    "moderate": "Fair air quality. Sensitive groups should monitor for symptoms during prolonged exertion.",
    "high": "High Risk: Significant particle deposition likely. Move activities indoors if possible.",
    "critical": "CRITICAL STAKE: Severe health risk. Avoid all outdoor exertion; use air filtration indoors."
}

# DATABASE CONNECTION
MONGO_URI = "mongodb+srv://kyrstAircom_db_user:aircompasswd123@cluster0.84anxvx.mongodb.net/"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Trigger a quick connection check
    client.server_info() 
    db = client.aircom_db
    collection = db.live_measurements
    print("Successfully connected to MongoDB Atlas")
except Exception as e:
    print(f"Connection Error: {e}")


# Importing and loading the models and data cleaning tools
try:
    # Regression and Classification Models
    AQI_MODEL = joblib.load("../ml_models/aqi_model.pkl")
    RISK_MODEL = joblib.load("../ml_models/risk_model.pkl")
    UFP_MODEL = joblib.load("../ml_models/ufp_model.pkl")

    # Scaler and Imputer Tools
    SCALER = joblib.load("../ml_models/scaler.pkl")
    IMPUTER = joblib.load("../ml_models/imputer.pkl")

    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    

# Dataset complication (matches the ML Notebook)
MEASUREMENTS = ["pm25", "um003", "pm1", "humidity", "temperature"]


def getCityInsight(city, activity_key, status_key):
    # Fetches live data from MongoDB -> Processes data through ML Models -> Returns the output

    # Fetching latest record from database
    data = collection.find_one({"city": city})
    if not data:
        return None
    
    # Prepare the features
    features = pd.DataFrame([[
        data.get('pm25'),
        data.get('um003'),
        data.get('pm1'),
        data.get('humidity', 60),    # Reserved value if not provided
        data.get('temperature', 28)
    ]], columns=MEASUREMENTS)

    # Preprocessing: Imputer replaces NaN values with trained medians
                #    Scaler normalizes the data for the models
    input = SCALER.transform(IMPUTER.transform(features))

    # UFP model requiring only 1 feature (PM2.5)
    ufp_input = np.array([[data.get('pm25', 0)]])
    
    # AI PREDICTION MODELS
    aqi_prediction = AQI_MODEL.predict(input)[0]
    risk_prediction = RISK_MODEL.predict(input)[0]
    ufp_prediction = UFP_MODEL.predict(ufp_input)[0]

    # Personalized Expert Score
    # Formula: UFP * Activity Weight * Health Status Weight
    p_score = (ufp_prediction / 2) * ACTIVITY_WEIGHTS.get(activity_key, 1.0) * STATUS_WEIGHTS.get(status_key, 1.0)

    aqi_math = calculate_aqi(data.get('pm25', 0))
    # Advices Level Conditions
    if p_score >= 1000 or aqi_math >= 250:
        lvl = "critical"
    elif p_score >= 450 or aqi_math >= 150 or risk_prediction == "Bad":
        lvl = "high"
    elif p_score >= 150 or aqi_math >= 51 or risk_prediction == "Moderate":
        lvl = "moderate"
    else:
        lvl = "low"
    
    # Disease Risk Mapping (Asthma, COPD complication, Cardiovascular strain)
    disease_risks = {
        "Asthma": "Elevated" if risk_prediction in ["Bad"] and p_score > 300 or status_key == "asthmatic" else "Stable",
        "COPD Complication": "High Risk" if p_score > 600 else "Low Risk",
        "Cardiovascular Strain": "Critical" if p_score > 1000 and (status_key == "elderly" or risk_prediction == "Bad") else "Normal"
    }
    # Return statement of all outputs
    return {
        "pm25": float(data.get('pm25', 0)),
        #"aqi_ai": max(0, float(aqi_prediction)),
        "aqi_math": aqi_math,
        "risk": str(risk_prediction),
        "ufp": round(ufp_prediction, 2),
        "personal_score": round(float(p_score), 2),
        "disease_predictions": disease_risks,
        "advice": ADVICES[lvl],
        "last_updated": data.get('lastUpdated')
    }

# Comparison Output Route
@app.route('/', methods=['GET', 'POST'])
def index():
    # Fetch current list of synced cities from database
    synced_cities = sorted(collection.distinct('city'))

    if request.method == 'GET':
        return jsonify({
            "status": "AirCom Engine Online (Live Data)",
            "available_cities": synced_cities,
            "instructions": "Send POST with city_a, city_b, activity, status"
        })
    
    # If it's a POST command, return the raw data results
    city_a = request.form.get('city_a')
    city_b = request.form.get('city_b')
    activity = request.form.get('activity', 'resting')
    status = request.form.get('status', 'healthy_adult')

    res_a = getCityInsight(city_a, activity, status)
    res_b = getCityInsight(city_b, activity, status)

    if res_a and res_b:
        return jsonify({
            "city_a": {"City": city_a, **res_a},
            "city_b": {"City": city_b, **res_b},
            "meta": {"activity": activity, "status": status}
        })
    
    return jsonify({"error": "City data not found in live database"}), 404

if __name__ == "__main__":
    # Initial Test Run
    app.run(debug=True)
