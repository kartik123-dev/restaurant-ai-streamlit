
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Vaishnavi Restaurant AI",
                   page_icon="🍽️", layout="wide")

st.title("🍽️ Vaishnavi Restaurant AI")
st.caption("Smart Sales Prediction & Inventory Management")
st.divider()

# Sample sales data for AI training
data = pd.DataFrame({
    "Customers": [30, 40, 50, 60, 70, 80, 90, 100],
    "Sales": [3000, 4000, 5200, 6000, 7200, 8300, 9500, 10500]
})

model = LinearRegression()
model.fit(data[["Customers"]], data["Sales"])

# Sidebar inputs
st.sidebar.header("⚙️ Restaurant Settings")
customers = st.sidebar.number_input(
    "Expected customers", min_value=0, max_value=10000, value=70
)
days = st.sidebar.number_input(
    "Forecast days", min_value=1, max_value=30, value=1
)

st.subheader("📊 Dashboard")
prediction = max(0, float(model.predict(
    pd.DataFrame({"Customers": [customers]})
)[0]))

a, b, c = st.columns(3)
a.metric("Expected Customers", f"{customers:,}")
b.metric("Predicted Sales", f"₹{prediction:,.0f}")
c.metric("Forecast Period", f"{days} day(s)")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("🤖 AI Sales Prediction")
    st.write("Model: Linear Regression")
    st.line_chart(data.set_index("Customers"))
    st.success(f"Estimated sales: ₹{prediction:,.0f}")
    st.caption("Prediction is based on sample training data.")

with right:
    st.subheader("📦 Smart Inventory Forecast")
    st.write("Edit the stock and usage per customer below.")

    inventory = pd.DataFrame({
        "Item": ["Rice (kg)", "Paneer (kg)", "Buns (pcs)",
                 "Tomatoes (kg)", "Cold Drinks (bottles)"],
        "Stock": [25, 12, 100, 15, 80],
        "Per Customer": [0.08, 0.05, 1, 0.06, 0.5]
    })

    edited = st.data_editor(
        inventory, hide_index=True, use_container_width=True,
        column_config={
            "Stock": st.column_config.NumberColumn(min_value=0),
            "Per Customer": st.column_config.NumberColumn(
                min_value=0, step=0.01
            )
        }
    )

    edited["Required"] = (
        edited["Per Customer"] * customers * days
    ).round(2)
    edited["After Forecast"] = (
        edited["Stock"] - edited["Required"]
    ).round(2)
    edited["Status"] = edited["After Forecast"].apply(
        lambda x: "⚠️ Refill" if x < 0 else "✅ Sufficient"
    )

    st.dataframe(
        edited[["Item", "Stock", "Required",
                "After Forecast", "Status"]],
        hide_index=True, use_container_width=True
    )

    refill = edited[edited["After Forecast"] < 0]
    if not refill.empty:
        st.warning("Some items need restocking!")
        st.write(", ".join(refill["Item"].tolist()))
    else:
        st.success("Stock is sufficient for this forecast.")

st.divider()
st.subheader("📈 Sample Sales Records")
st.dataframe(data, hide_index=True, use_container_width=True)

st.caption("Class XII CBSE AI Project | Python • Streamlit • Scikit-learn")
