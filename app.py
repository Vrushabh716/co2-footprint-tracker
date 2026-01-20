# app.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px

# ---------- CONFIG ----------
DB_PATH = "co2_tracker.db"
APP_TITLE = "Individual CO₂ Footprint Tracker"
# Simple emission factors (kg CO2 per unit). Edit these to match your sources.
EMISSION_FACTORS = {
    "transport_km_car": 0.192,   # kg CO2 per km (car, average petrol) — change if needed
    "transport_km_bus": 0.089,   # kg CO2 per km per passenger (bus)
    "transport_km_bike_walk": 0.0,
    "electricity_kwh": 0.82,     # kg CO2 per kWh (example grid factor) — adjust regionally
    "meat_meal": 5.0,            # kg CO2 per meat meal (average)
    "veg_meal": 2.0,             # kg CO2 per vegetarian meal (average)
    "plastic_item": 0.1          # kg CO2 per single-use plastic item avoided (example)
}
# Baseline assumptions used to compute "savings" (you can change these)
BASELINE = {
    "car_km_per_day": 10,    # baseline km by car per day
    "electricity_kwh_per_day": 4,
    "meat_meals_per_day": 1,
    "plastic_items_per_day": 2
}
# ---------- DB HELPERS ----------
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            user TEXT,
            date TEXT,
            car_km REAL,
            bus_km REAL,
            bike_walk_km REAL,
            electricity_kwh REAL,
            meat_meals INTEGER,
            veg_meals INTEGER,
            plastic_items_avoided INTEGER,
            co2_kg REAL,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn

def insert_log(conn, data: dict):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (user, date, car_km, bus_km, bike_walk_km, electricity_kwh,
                          meat_meals, veg_meals, plastic_items_avoided, co2_kg, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["user"],
        data["date"],
        data["car_km"],
        data["bus_km"],
        data["bike_walk_km"],
        data["electricity_kwh"],
        data["meat_meals"],
        data["veg_meals"],
        data["plastic_items_avoided"],
        data["co2_kg"],
        data["created_at"]
    ))
    conn.commit()

def fetch_logs(conn, user=None):
    cur = conn.cursor()
    if user:
        cur.execute("SELECT * FROM logs WHERE user = ? ORDER BY date ASC", (user,))
    else:
        cur.execute("SELECT * FROM logs ORDER BY date ASC")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)

# ---------- CALCULATION ----------
def calculate_co2(car_km, bus_km, bike_walk_km, electricity_kwh, meat_meals, veg_meals, plastic_items_avoided):
    e = EMISSION_FACTORS
    co2 = 0.0
    co2 += car_km * e["transport_km_car"]
    co2 += bus_km * e["transport_km_bus"]
    co2 += bike_walk_km * e["transport_km_bike_walk"]
    co2 += electricity_kwh * e["electricity_kwh"]
    co2 += meat_meals * e["meat_meal"]
    co2 += veg_meals * e["veg_meal"]
    # plastic_items_avoided reduces emissions vs baseline (we'll treat avoided as negative emissions effect)
    co2 -= plastic_items_avoided * e["plastic_item"]
    return round(co2, 3)

def baseline_daily_co2():
    b = BASELINE
    e = EMISSION_FACTORS
    base = 0.0
    base += b["car_km_per_day"] * e["transport_km_car"]
    base += b["electricity_kwh_per_day"] * e["electricity_kwh"]
    base += b["meat_meals_per_day"] * e["meat_meal"]
    base += b["plastic_items_per_day"] * e["plastic_item"]
    return round(base, 3)

# ---------- UI ----------
def main():
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    st.title(APP_TITLE)
    st.write("A simple web app to log daily actions and compute estimated CO₂ (kg) footprint. Built with Streamlit.")

    conn = init_db()

    # Sidebar: user and quick stats
    st.sidebar.header("User & Quick Stats")
    user = st.sidebar.text_input("Your name / user id", value="user1")
    if st.sidebar.button("Show my logs"):
        df_user = fetch_logs(conn, user=user)
        st.sidebar.write(f"Total records: {len(df_user)}")
    st.sidebar.markdown("---")
    st.sidebar.write("Baseline daily CO₂ (editable in code):")
    st.sidebar.write(f"**{baseline_daily_co2()} kg CO₂ / day**")

    # Input form
    st.header("Log today's activities")
    with st.form("log_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date", value=date.today())
            car_km = st.number_input("Car kilometres (km)", min_value=0.0, value=0.0, step=0.5)
            bus_km = st.number_input("Bus kilometres (km)", min_value=0.0, value=0.0, step=0.5)
            bike_walk_km = st.number_input("Bike / Walk kilometres (km)", min_value=0.0, value=0.0, step=0.5)
            electricity_kwh = st.number_input("Electricity used (kWh)", min_value=0.0, value=0.0, step=0.1)
        with col2:
            meat_meals = st.number_input("Number of meat meals", min_value=0, value=0, step=1)
            veg_meals = st.number_input("Number of vegetarian meals", min_value=0, value=0, step=1)
            plastic_items_avoided = st.number_input("Single-use plastic items avoided today", min_value=0, value=0, step=1)
            notes = st.text_area("Notes (optional)", value="")
        submitted = st.form_submit_button("Calculate & Save")

    if submitted:
        co2 = calculate_co2(car_km, bus_km, bike_walk_km, electricity_kwh, meat_meals, veg_meals, plastic_items_avoided)
        st.success(f"Estimated CO₂ footprint for {date_input.isoformat()}: **{co2} kg CO₂**")
        # compute baseline and saved
        baseline = baseline_daily_co2()
        saved = round(max(0.0, baseline - co2), 3)
        pct = round((saved / baseline * 100) if baseline > 0 else 0, 2)
        st.info(f"Baseline: {baseline} kg/day → Estimated saved: **{saved} kg CO₂** ({pct}%) compared to baseline assumptions.")
        # Save to DB
        record = {
            "user": user,
            "date": date_input.isoformat(),
            "car_km": car_km,
            "bus_km": bus_km,
            "bike_walk_km": bike_walk_km,
            "electricity_kwh": electricity_kwh,
            "meat_meals": int(meat_meals),
            "veg_meals": int(veg_meals),
            "plastic_items_avoided": int(plastic_items_avoided),
            "co2_kg": co2,
            "created_at": datetime.now().isoformat()
        }
        insert_log(conn, record)
        st.write("Record saved ✅")

    # Dashboard: show aggregated logs for the user
    st.header("Dashboard & History")
    df = fetch_logs(conn, user=user)
    if df.empty:
        st.warning("No logs yet for this user. Add a record above.")
    else:
        st.write("Recent logs (most recent 10):")
        display_df = df[["date","car_km","bus_km","bike_walk_km","electricity_kwh","meat_meals","veg_meals","plastic_items_avoided","co2_kg"]].tail(20)
        display_df = display_df.sort_values("date")
        st.dataframe(display_df.reset_index(drop=True))

        # Time series plot of CO2
        fig = px.line(display_df, x="date", y="co2_kg", markers=True, title="CO₂ per day (kg)")
        st.plotly_chart(fig, use_container_width=True)

        # Aggregate totals & average
        total_co2 = df["co2_kg"].sum()
        avg_co2 = df["co2_kg"].mean()
        st.metric("Total CO₂ logged (kg)", round(total_co2,3))
        st.metric("Average daily CO₂ (kg)", round(avg_co2,3))

        # CSV export
        csv = display_df.to_csv(index=False)
        st.download_button("Download recent logs as CSV", csv, file_name=f"{user}_co2_logs.csv", mime="text/csv")

    # Admin: show all users (simple)
    if st.checkbox("Show all users (admin view)"):
        df_all = fetch_logs(conn)
        if df_all.empty:
            st.write("No records in DB yet.")
        else:
            st.write("All logs (first 100 rows):")
            st.dataframe(df_all.head(100))

if __name__ == "__main__":
    main()
