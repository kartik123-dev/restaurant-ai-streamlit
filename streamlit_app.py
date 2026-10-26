import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Vaishnavi Restaurant AI",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Vaishnavi Restaurant AI")
st.caption("Sales Prediction | Smart Inventory Management")
st.divider()

# Sample data for sales prediction
data = pd.DataFrame({
    "Customers": [20, 30, 40, 50, 60, 70, 80, 90, 100],
    "Sales": [2000, 3100, 4000, 5200, 6100, 7300, 8200, 9400, 10300]
})

# Simple linear prediction using sample data
slope = (
    (data["Sales"].iloc[-1] - data["Sales"].iloc[0]) /
    (data["Customers"].iloc[-1] - data["Customers"].iloc[0])
)
intercept = data["Sales"].iloc[0] - slope * data["Customers"].iloc[0]

st.sidebar.header("⚙️ Restaurant Settings")
customers = st.sidebar.number_input(
    "Expected customers", min_value=0, max_value=10000, value=70
)
days = st.sidebar.number_input(
    "Forecast days", min_value=1, max_value=30, value=1
)

sales = max(0, slope * customers + intercept)

st.subheader("📊 Dashboard")
a, b, c = st.columns(3)
a.metric("Expected Customers", f"{customers:,}")
b.metric("Predicted Sales", f"₹{sales:,.0f}")
c.metric("Forecast Period", f"{days} day(s)")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("📈 Sales Prediction")
    st.line_chart(data.set_index("Customers"))
    st.success(f"Estimated sales: ₹{sales:,.0f}")
    st.caption("Estimate based on sample sales records.")

with right:
    st.subheader("📦 Smart Inventory")
    st.write("Edit stock and usage per customer.")

    inventory = pd.DataFrame({
        "Item": ["Rice (kg)", "Paneer (kg)", "Buns (pcs)",
                 "Tomatoes (kg)", "Drinks (bottles)"],
        "Stock": [25, 12, 100, 15, 80],
        "Usage per Customer": [0.08, 0.05, 1.0, 0.06, 0.5]
    })

    inventory = st.data_editor(
        inventory,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Stock": st.column_config.NumberColumn(min_value=0),
            "Usage per Customer": st.column_config.NumberColumn(min_value=0)
        }
    )

    inventory["Required"] = (
        inventory["Usage per Customer"] * customers * days
    ).round(2)
    inventory["Remaining"] = (
        inventory["Stock"] - inventory["Required"]
    ).round(2)
    inventory["Status"] = inventory["Remaining"].apply(
        lambda x: "⚠️ Refill" if x < 0 else "✅ Sufficient"
    )

    st.dataframe(
        inventory,
        hide_index=True,
        use_container_width=True
    )

    if (inventory["Remaining"] < 0).any():
        st.warning("Some items need restocking!")
    else:
        st.success("Stock is sufficient for this forecast.")

st.divider()
st.subheader("📋 Sample Sales Records")
st.dataframe(data, hide_index=True, use_container_width=True)

st.caption("Class XII CBSE AI Project | Python + Streamlit")
