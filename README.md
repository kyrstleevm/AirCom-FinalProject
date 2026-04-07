# AirCom Final Project (WIP) 🌬️

AirCom is a full-stack web application that predicts air quality insights and health risks using machine learning models and live data from OpenAQ API.

## 🛠️ Setup locally Instructions

### 1. Prerequisites
* **Python 3.10+**
* **MongoDB** (Running on Atlas)

### 2. Installation
1. Clone the repository.
2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Initialize Frontend Dependencies:
   npm install
4. Create an .env file in the root directory:
   MONGO_URI=your_mongodb_atlas_connection_string
   OPENAQ_API_KEY=your_openaq_api_here
5. Run locally:
   python src/aircomApp.py

## 🚀 Key Features
- **Live Global Data:** Pulls real-time environmental metrics from the OpenAQ API for over 50 global cities, that automatically re-syncs every 6 hours.
- **AI-Driven Insights:** Uses two custom-trained ML models to predict general health risk, and Ultrafine Particle (UFP) levels. Calculation of AQI is a plus.
- **Personalization Engine:** Calculates unique risk scores based on user profiles (e.g., Asthmatic, Child, Elderly) and activities (Resting vs. Running).
- **Disease Mapping:** Predicts the likelihood of Asthma elevation, COPD complications, and Cardiovascular strain.
- **Automated Background Sync:** Features a multi-threaded background worker that ensures the database remains fresh without interrupting user sessions.
- **PDF Reports:** Generate and download a side-by-side comparison of two cities for health-conscious travel planning.

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Database:** MongoDB Atlas (NoSQL)
- **Server Management:** Gunicorn (Production WSGI Server)
- **Machine Learning:** Scikit-Learn, Joblib, Pandas, NumPy, Matplotlib, Seaborn
- **Frontend:** HTML5, CSS3 (Animate.css), JavaScript (Fetch API, html2pdf.js)
- **Deployment:** Render Cloud Infrastracture