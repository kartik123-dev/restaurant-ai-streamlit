
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Restaurant AI", page_icon="🍽️", layout="wide")

st.title("🍽️ Restaurant AI Manager")
st.caption("AI Sales Prediction & Smart Inventory")

data = pd.DataFrame({
    "Customers": [20, 30, 40, 50, 60, 70, 80, 90, 100],
    "Sales": [2000, 3100, 4000, 5200, 6100, 7300, 8200, 9400, 10300]
})

model = LinearRegression()
model.fit(data[["Customers"]], data["Sales"])

st.sidebar.header("Restaurant Settings")
customers = st.sidebar.number_input("Expected customers", 0, 10000, 70)
days = st.sidebar.number_input("Forecast days", 1, 30, 1)

sales = max(0, model.predict(pd.DataFrame({"Customers": [customers]}))[0])

a, b, c = st.columns(3)
a.metric("Customers", f"{customers:,}")
b.metric("Predicted Sales", f"₹{sales:,.0f}")
c.metric("Forecast", f"{days} day(s)")

st.subheader("📈 Sales Prediction")
st.line_chart(data.set_index("Customers"))
st.info(f"AI predicts sales of ₹{sales:,.0f} for {customers} customers.")

st.divider()
st.subheader("📦 Smart Inventory")

stock = pd.DataFrame({
    "Item": ["Rice (kg)", "Paneer (kg)", "Buns (pcs)", "Tomatoes (kg)", "Drinks (bottles)"],
    "Available Stock": [25, 12, 100, 15, 80],
    "Usage per Customer": [0.08, 0.05, 1.0, 0.06, 0.5]
})

stock = st.data_editor(stock, hide_index=True, use_container_width=True)
stock["Required Stock"] = (stock["Usage per Customer"] * customers * days).round(2)
stock["Remaining"] = (stock["Available Stock"] - stock["Required Stock"]).round(2)
stock["Status"] = stock["Remaining"].apply(lambda x: "⚠️ Refill" if x < 0 else "✅ Enough")

st.dataframe(stock, hide_index=True, use_container_width=True)

if (stock["Remaining"] < 0).any():
    st.warning("Some items need restocking!")
else:
    st.success("Inventory is sufficient for this forecast.")

st.subheader("📋 Sample Sales Data")
st.dataframe(data, hide_index=True, use_container_width=True)
st.caption("Class XII CBSE AI Project | Python + Streamlit + Linear Regression")

