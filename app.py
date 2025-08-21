import sys
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
import pymysql
import plotly.express as px
import datetime

# Database connection
engine = create_engine("mysql+pymysql://root:pass123@localhost/food_analysis")

st.set_page_config(page_title="Food Donation Analytics", layout="wide")
st.title("🍲 Food Donation Platform")

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.header("Filters")
city = st.sidebar.text_input("City")
provider = st.sidebar.text_input("Provider")
food_type = st.sidebar.text_input("Food Type")
meal_type = st.sidebar.text_input("Meal Type")

# ------------------ TABS ------------------
tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Analytics", "🛠️ CRUD"])

# ---------------- HOME TAB ----------------
with tab1:
    st.subheader("Food Listings")

    query = """
        SELECT f.Food_ID, f.Food_Name, f.Food_Type, f.Meal_Type, f.Expiry_Date, 
               p.Name AS Provider, p.City, p.Contact
        FROM food_listings f
        JOIN providers p ON f.Provider_ID = p.Provider_ID
        WHERE 1=1
    """
    if city:
        query += f" AND p.City='{city}'"
    if provider:
        query += f" AND p.Name='{provider}'"
    if food_type:
        query += f" AND f.Food_Type='{food_type}'"
    if meal_type:
        query += f" AND f.Meal_Type='{meal_type}'"

    try:
        df = pd.read_sql(query, engine)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# ---------------- ANALYTICS TAB ----------------
with tab2:
    st.subheader("📊 Analytics Dashboard")

    queries = {
        "Providers & Food Listings": """
            SELECT p.Name, COUNT(f.Food_ID) AS Total_Items
            FROM providers p
            JOIN food_listings f ON p.Provider_ID=f.Provider_ID
            GROUP BY p.Name ORDER BY Total_Items DESC LIMIT 5
        """,

        "Expiring Soon": """
            SELECT Food_Name, Expiry_Date FROM food_listings
            WHERE Expiry_Date <= CURDATE() + INTERVAL 7 DAY
            ORDER BY Expiry_Date
        """,

        "Claims by Month": """
            SELECT DATE_FORMAT(Timestamp, '%%Y-%%m') AS Month, COUNT(*) AS Total_Claims
            FROM claims GROUP BY Month ORDER BY Month
        """,

        "Most Claimed Food Items": """
            SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c
            JOIN food_listings f ON c.Food_ID=f.Food_ID
            GROUP BY f.Food_Name ORDER BY Total_Claims DESC LIMIT 10
        """,

        "Top Cities with Donations": """
            SELECT p.City, COUNT(f.Food_ID) AS Total_Donations
            FROM providers p
            JOIN food_listings f ON p.Provider_ID=f.Provider_ID
            GROUP BY p.City ORDER BY Total_Donations DESC LIMIT 5
        """,

        "Claims by Status": """
            SELECT Status, COUNT(*) AS Total
            FROM claims GROUP BY Status
        """,

        "Average Shelf Life of Food": """
            SELECT Food_Type, AVG(DATEDIFF(Expiry_Date, CURDATE())) AS Avg_Shelf_Life
            FROM food_listings GROUP BY Food_Type
        """,

        "Active vs Expired Listings": """
            SELECT 
                SUM(CASE WHEN Expiry_Date >= CURDATE() THEN 1 ELSE 0 END) AS Active,
                SUM(CASE WHEN Expiry_Date < CURDATE() THEN 1 ELSE 0 END) AS Expired
            FROM food_listings
        """,

        "Food Type Distribution": """
            SELECT Food_Type, COUNT(*) AS Total
            FROM food_listings GROUP BY Food_Type
        """,

        "Meal Type Popularity": """
            SELECT Meal_Type, COUNT(*) AS Total
            FROM food_listings GROUP BY Meal_Type
        """
    }

    for title, q in queries.items():
        st.markdown(f"### {title}")
        try:
            df_q = pd.read_sql(q, engine)
            st.dataframe(df_q)

            # Auto-visualize with plotly if at least 2 columns
            if len(df_q.columns) >= 2:
                x_col, y_col = df_q.columns[0], df_q.columns[1]

                if "Distribution" in title or "Popularity" in title or "Status" in title:
                    fig = px.pie(df_q, names=x_col, values=y_col, title=title)
                else:
                    fig = px.bar(df_q, x=x_col, y=y_col, title=title)

                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Query failed: {e}")

# ---------------- CRUD TAB ----------------
with tab3:
    st.subheader("🛠️ Manage Data (CRUD)")

    crud_action = st.selectbox("Select Action", ["Add Provider", "Add Food Listing", "Update Claim", "Delete Listing"])

    # Add Provider
    if crud_action == "Add Provider":
        name = st.text_input("Provider Name")
        city = st.text_input("City")
        contact = st.text_input("Contact")
        if st.button("Add"):
            with engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO providers (Name, City, Contact) VALUES (:name, :city, :contact)"),
                    {"name": name, "city": city, "contact": contact}
                )
                conn.commit()
            st.success("✅ Provider Added!")

    # Add Food Listing
    elif crud_action == "Add Food Listing":
        provider_id = st.number_input("Provider ID", min_value=1)
        food_name = st.text_input("Food Name")
        food_type = st.text_input("Food Type")
        meal_type = st.text_input("Meal Type")
        expiry_date = st.date_input("Expiry Date")
        if st.button("Add Listing"):
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO food_listings (Provider_ID, Food_Name, Food_Type, Meal_Type, Expiry_Date)
                        VALUES (:provider_id, :food_name, :food_type, :meal_type, :expiry_date)
                    """),
                    {
                        "provider_id": provider_id,
                        "food_name": food_name,
                        "food_type": food_type,
                        "meal_type": meal_type,
                        "expiry_date": expiry_date
                    }
                )
                conn.commit()
            st.success("✅ Food Listing Added!")

    # Update Claim
    elif crud_action == "Update Claim":
        claim_id = st.number_input("Claim ID", min_value=1)
        status = st.selectbox("New Status", ["Pending", "Approved", "Rejected"])
        if st.button("Update"):
            with engine.connect() as conn:
                conn.execute(
                    text("UPDATE claims SET Status = :status WHERE Claim_ID = :claim_id"),
                    {"status": status, "claim_id": claim_id}
                )
                conn.commit()
            st.success("✅ Claim Updated!")

    # Delete Listing
    elif crud_action == "Delete Listing":
        food_id = st.number_input("Food ID", min_value=1)
        if st.button("Delete"):
            with engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM food_listings WHERE Food_ID = :food_id"),
                    {"food_id": food_id}
                )
                conn.commit()
            st.success("🗑️ Listing Deleted!")
