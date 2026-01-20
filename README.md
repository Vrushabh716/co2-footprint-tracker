# 🌍 Individual CO₂ Footprint Tracker

A simple and interactive web application built using **Streamlit** that helps individuals track their daily carbon footprint based on lifestyle activities such as transportation, electricity usage, food habits, and plastic consumption.

---

## 🚀 Features

- Log daily activities:
  - 🚗 Car travel
  - 🚌 Bus travel
  - 🚶 Bike / walking
  - ⚡ Electricity usage
  - 🍖 Meat & 🥗 vegetarian meals
  - ♻️ Plastic items avoided
- Automatically calculates estimated **CO₂ emissions (kg/day)**
- Baseline comparison to show **CO₂ savings**
- Interactive dashboard with:
  - Daily CO₂ trend chart
  - Total & average emissions
- SQLite database for persistent storage
- CSV export of user logs

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **SQLite**
- **Pandas**
- **Plotly**

---

## 📂 Project Structure

co2-footprint-tracker/
│── app.py
│── requirements.txt
│── README.md
│── co2_tracker.db (auto-generated)


---

## ▶️ How to Run the App

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Vrushah716/co2-footprint-tracker.git
cd co2-footprint-tracker

pip install -r requirements.txt
streamlit run app.py


---
📊 Emission Calculation Notes

Emission factors are approximate and configurable inside the code.

Baseline values are used to estimate daily CO₂ savings.

This app is intended for educational and awareness purposes.

✨ Future Improvements

User authentication

Cloud database support

Monthly & yearly analytics

Country-based emission factors

Deployment on Streamlit Cloud

📜 License

This project is open-source and available under the MIT License.

👤 Author

Vrushabh Sontakke
Feel free to connect and contribute!


---

## ⭐ Bonus (Strong Tip)
After uploading:
- Add **screenshots** of the app
- Enable **GitHub Pages / Streamlit Cloud**
- Pin this repo to your profile

If you want, I can:
- ✅ Deploy this on **Streamlit Cloud**
- ✅ Improve README visuals
- ✅ Add license file
- ✅ Convert this into a **resume-ready project**

Just tell me 💙
