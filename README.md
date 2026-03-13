# AirCom Final Project (WIP) 🌬️

This project predicts Air Quality Insights and Health Risks using machine learning models and live data from OpenAQ.

## 🛠️ Setup Instructions

### 1. Prerequisites
* **Python 3.10+**
* **MongoDB** (Running on Atlas)

### 2. Installation
1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

## 🚀 Key Features
- **Live Global Data:** Pulls real-time environmental metrics from the OpenAQ API for over 50 global cities.
- **AI-Driven Insights:** Uses three custom-trained ML models to predict AQI, general health risk, and Ultrafine Particle (UFP) levels.
- **Personalization Engine:** Calculates unique risk scores based on user profiles (e.g., Asthmatic, Child, Elderly) and activities (Resting vs. Running).
- **Disease Mapping:** Predicts the likelihood of Asthma elevation, COPD complications, and Cardiovascular strain.
- **PDF Reports:** Generate and download a side-by-side comparison of two cities for health-conscious travel planning.

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Database:** MongoDB Atlas (NoSQL)
- **Machine Learning:** Scikit-Learn, Joblib, Pandas, NumPy
- **Frontend:** HTML5, CSS3 (Animate.css), JavaScript (Fetch API, html2pdf.js)
