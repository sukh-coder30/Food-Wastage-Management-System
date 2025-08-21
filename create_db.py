import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns 
import warnings
warnings.filterwarnings("ignore")

import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",        # your MySQL username
    password="pass123",  # your MySQL password
    database="food_analysis"
)

cursor= conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS Providers (
    Provider_ID INT PRIMARY KEY,
    Name VARCHAR(255),
    Type VARCHAR(100),
    Address VARCHAR(255),
    City VARCHAR(100),
    Contact VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Receivers (
    Receiver_ID INT PRIMARY KEY,
    Name VARCHAR(255),
    Type VARCHAR(100),
    City VARCHAR(100),
    Contact VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Food_Listings (
    Food_ID INT PRIMARY KEY,
    Food_Name VARCHAR(255),
    Quantity INT,
    Expiry_Date DATE,
    Provider_ID INT,
    Provider_Type VARCHAR(100),
    Location VARCHAR(255),
    Food_Type VARCHAR(100),
    Meal_Type VARCHAR(100),
    FOREIGN KEY (Provider_ID) REFERENCES Providers(Provider_ID)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Claims (
    Claim_ID INT PRIMARY KEY,
    Food_ID INT,
    Receiver_ID INT,
    Status VARCHAR(100),
    Timestamp DATETIME,
    FOREIGN KEY (Food_ID) REFERENCES Food_Listings(Food_ID),
    FOREIGN KEY (Receiver_
    ID) REFERENCES Receivers(Receiver_ID)
)
""")
import pandas as pd
from sqlalchemy import create_engine, text

# DB connection
engine = create_engine("mysql+pymysql://root:pass123@localhost/food_analysis")

# Read CSVs
providers = pd.read_csv("providers_data.csv")
receivers = pd.read_csv("receivers_data.csv")
food_listings = pd.read_csv("food_listings_data.csv")
claims = pd.read_csv("claims_data.csv")

# Convert dates
claims["Timestamp"] = pd.to_datetime(claims["Timestamp"], format="%m/%d/%Y %H:%M", errors="coerce")
claims["Timestamp"] = claims["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

if "Expiry_Date" in food_listings.columns:
    food_listings["Expiry_Date"] = pd.to_datetime(
        food_listings["Expiry_Date"], format="%m/%d/%Y", errors="coerce"
    ).dt.strftime("%Y-%m-%d")

with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    conn.execute(text("DELETE FROM claims;"))
    conn.execute(text("DELETE FROM food_listings;"))
    conn.execute(text("DELETE FROM receivers;"))
    conn.execute(text("DELETE FROM providers;"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

# Insert in correct order
with engine.begin() as conn:
    providers.to_sql("providers", conn, if_exists="append", index=False, method="multi", chunksize=100)
    receivers.to_sql("receivers", conn, if_exists="append", index=False, method="multi", chunksize=100)
    food_listings.to_sql("food_listings", conn, if_exists="append", index=False, method="multi", chunksize=100)
    claims.to_sql("claims", conn, if_exists="append", index=False, method="multi", chunksize=100)

print(" Data loaded successfully")
