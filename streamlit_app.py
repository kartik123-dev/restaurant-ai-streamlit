import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Vaishnavi Restaurant AI",
    layout="wide"
)

# ---------------- PAGE HEADER ----------------

st.title("Vaishnavi Restaurant AI")
st.caption("Sales Forecasting and Inventory Management")

# ---------------- DEFAULT DATA ----------------

DEFAULT_SALES = pd.DataFrame({
    "Date": ["2026-10-20", "2026-10-21", "2026-10-22",
             "2026-10-23", "2026-10-24"],
    "Customers": [40, 50, 60, 45, 70],
    "Sales": [4000, 5200, 6300, 4700, 7500]
})

DEFAULT_INVENTORY = pd.DataFrame({
    "Item": ["Rice (kg)", "Paneer (kg)", "Buns (pcs)",
             "Tomatoes (kg)", "Drinks (bottles)"],
    "Stock": [25.0, 12.0, 100.0, 15.0, 80.0],
    "Usage per Customer": [0.08, 0.05, 1.0, 0.06, 0.5],
    "Minimum Stock": [5.0, 3.0, 20.0, 3.0, 15.0]
})

if "sales_data" not in st.session_state:
    st.session_state.sales_data = DEFAULT_SALES.copy()

if "inventory_data" not in st.session_state:
    st.session_state.inventory_data = DEFAULT_INVENTORY.copy()

# ---------------- SIDEBAR ----------------

st.sidebar.header("Restaurant Settings")

forecast_days = st.sidebar.number_input(
    "Forecast period (days)",
    min_value=1,
    max_value=30,
    value=1
)

expected_customers = st.sidebar.number_input(
    "Expected customers per day",
    min_value=0,
    max_value=10000,
    value=70
)

st.sidebar.caption(
    "Initial sales records are sample data. "
    "Upload your own records for a more relevant estimate."
)

# ---------------- DAILY SALES ENTRY ----------------

st.header("Daily Sales Entry")

with st.form("sales_entry", clear_on_submit=True):
    sales_date = st.date_input("Sales date", value=date.today())

    customers = st.number_input(
        "Number of customers",
        min_value=0,
        max_value=100000,
        value=50
    )

    sales_amount = st.number_input(
        "Total sales (Rs.)",
        min_value=0.0,
        value=5000.0,
        step=100.0
    )

    submitted = st.form_submit_button("Add Sales Record")

if submitted:
    new_row = pd.DataFrame([{
        "Date": str(sales_date),
        "Customers": customers,
        "Sales": sales_amount
    }])

    st.session_state.sales_data = pd.concat(
        [st.session_state.sales_data, new_row],
        ignore_index=True
    )

    st.success("Sales record added.")
    st.rerun()

# ---------------- SALES CSV ----------------

st.header("Sales Data Management")

uploaded_file = st.file_uploader(
    "Upload sales CSV",
    type=["csv"],
    key="sales_upload"
)

if uploaded_file is not None:
    try:
        uploaded = pd.read_csv(uploaded_file)
        required = {"Date", "Customers", "Sales"}

        if not required.issubset(uploaded.columns):
            st.error(
                "CSV needs these columns: Date, Customers, Sales."
            )
        else:
            clean = uploaded[["Date", "Customers", "Sales"]].copy()
            clean["Customers"] = pd.to_numeric(
                clean["Customers"], errors="raise"
            )
            clean["Sales"] = pd.to_numeric(
                clean["Sales"], errors="raise"
            )
            clean["Date"] = pd.to_datetime(
                clean["Date"], errors="raise"
            ).dt.strftime("%Y-%m-%d")

            if clean[["Customers", "Sales"]].isna().any().any():
                st.error("CSV contains missing numeric values.")
            elif (clean[["Customers", "Sales"]] < 0).any().any():
                st.error("Customers and sales cannot be negative.")
            else:
                st.session_state.sales_data = clean
                st.success("Sales data loaded.")
                st.rerun()

    except Exception:
        st.error(
            "Could not read the CSV. Check its dates and numeric values."
        )

sales = st.session_state.sales_data.copy()
sales["Customers"] = pd.to_numeric(
    sales["Customers"], errors="coerce"
)
sales["Sales"] = pd.to_numeric(
    sales["Sales"], errors="coerce"
)
sales["Date"] = pd.to_datetime(
    sales["Date"], errors="coerce"
)
sales = sales.dropna(subset=["Date", "Customers", "Sales"])
sales = sales[(sales["Customers"] >= 0) & (sales["Sales"] >= 0)]

st.session_state.sales_data = sales.assign(
    Date=sales["Date"].dt.strftime("%Y-%m-%d")
)

sales_download = st.session_state.sales_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Sales CSV",
    data=sales_download,
    file_name="restaurant_sales.csv",
    mime="text/csv"
)

# ---------------- SALES PREDICTION ----------------

st.divider()
st.header("Sales Prediction")

if not sales.empty:
    total_sales = sales["Sales"].sum()
    total_customers = sales["Customers"].sum()

    if total_customers > 0:
        average_sales_per_customer = total_sales / total_customers
    else:
        average_sales_per_customer = 0.0

    predicted_daily_sales = (
        average_sales_per_customer * expected_customers
    )
    predicted_period_sales = predicted_daily_sales * forecast_days

    a, b, c = st.columns(3)
    a.metric("Recorded Sales", f"Rs. {total_sales:,.0f}")
    b.metric("Average Sales per Customer",
             f"Rs. {average_sales_per_customer:,.2f}")
    c.metric("Estimated Sales",
             f"Rs. {predicted_period_sales:,.0f}")

    st.caption(
        "Method: total recorded sales divided by total recorded "
        "customers, multiplied by expected customers. "
        "This is a basic estimate, not a trained ML model."
    )

    st.subheader("Sales History")
    chart_sales = sales.sort_values("Date").copy()
    chart_sales["Date"] = chart_sales["Date"].astype(str)

    st.line_chart(
        chart_sales.set_index("Date")["Sales"]
    )

    st.subheader("Sales Records")
    st.dataframe(
        st.session_state.sales_data,
        use_container_width=True,
        hide_index=True
    )
else:
    average_sales_per_customer = 0.0
    st.info("Add or upload sales records to view predictions.")

# ---------------- CUSTOMIZABLE INVENTORY ----------------

st.divider()
st.header("Customizable Inventory")

st.write(
    "Edit the item name, current stock, usage per customer "
    "and minimum stock. You can also add or remove items."
)

inventory = st.data_editor(
    st.session_state.inventory_data,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    key="inventory_editor",
    column_config={
        "Item": st.column_config.TextColumn("Item name"),
        "Stock": st.column_config.NumberColumn(
            "Current stock",
            min_value=0,
            format="%.2f"
        ),
        "Usage per Customer": st.column_config.NumberColumn(
            "Usage per customer",
            min_value=0,
            format="%.3f"
        ),
        "Minimum Stock": st.column_config.NumberColumn(
            "Minimum stock",
            min_value=0,
            format="%.2f"
        )
    }
)

st.session_state.inventory_data = inventory

# ---------------- INVENTORY PREDICTION ----------------

st.header("Sales-Based Inventory Prediction")

st.write(
    "Required quantity is calculated from expected customers "
    "and each item's usage per customer."
)

inventory_result = inventory.copy()

for col in ["Stock", "Usage per Customer", "Minimum Stock"]:
    inventory_result[col] = pd.to_numeric(
        inventory_result[col], errors="coerce"
    )

inventory_result = inventory_result.dropna(
    subset=["Item", "Stock", "Usage per Customer", "Minimum Stock"]
)

inventory_result = inventory_result[
    (inventory_result["Stock"] >= 0)
    & (inventory_result["Usage per Customer"] >= 0)
    & (inventory_result["Minimum Stock"] >= 0)
]

inventory_result["Required Quantity"] = (
    inventory_result["Usage per Customer"]
    * expected_customers
    * forecast_days
).round(2)

inventory_result["Stock After Forecast"] = (
    inventory_result["Stock"]
    - inventory_result["Required Quantity"]
).round(2)

inventory_result["Refill Quantity"] = (
    inventory_result["Required Quantity"]
    + inventory_result["Minimum Stock"]
    - inventory_result["Stock"]
).clip(lower=0).round(2)

inventory_result["Status"] = inventory_result.apply(
    lambda row: (
        "Refill Required"
        if row["Stock After Forecast"] < row["Minimum Stock"]
        else "Sufficient"
    ),
    axis=1
)

st.dataframe(
    inventory_result,
    use_container_width=True,
    hide_index=True
)

low_stock = inventory_result[
    inventory_result["Status"] == "Refill Required"
]

if not low_stock.empty:
    st.warning(
        f"{len(low_stock)} inventory item(s) need attention."
    )
    st.dataframe(
        low_stock[["Item", "Stock", "Required Quantity",
                   "Stock After Forecast", "Refill Quantity"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("Stock is sufficient for the selected forecast.")

# ---------------- INVENTORY CHART ----------------

st.subheader("Inventory Requirement Chart")

if not inventory_result.empty:
    chart_inventory = inventory_result.set_index("Item")[
        ["Stock", "Required Quantity"]
    ]
    st.bar_chart(chart_inventory)

# ---------------- INVENTORY DOWNLOAD ----------------

inventory_csv = inventory_result.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Inventory Report",
    data=inventory_csv,
    file_name="inventory_report.csv",
    mime="text/csv"
)

st.divider()
st.caption(
    "Class XII CBSE AI Project | Python, Pandas and Streamlit"
                )
