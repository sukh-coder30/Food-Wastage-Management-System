# Food-Wastage-Management-System

This project is a Streamlit web application connected to a MySQL database.
It helps to:

Manage Providers & Food Listings (CRUD operations)
Track Claims (update status)
Analyze Food Distribution with auto-generated charts

# Features
# Analytics Dashboard

Runs predefined SQL queries.

Shows results in interactive tables.

Auto-generates charts (Pie or Bar) depending on query.

# Example insights:

Food type distribution (vegetarian/non-vegetarian).

Provider popularity (how many listings each provider offers).

Claim status breakdown.

# CRUD Operations

Manage data directly from the app:

Add Provider → Add new food provider with Name, City, Contact.

Add Food Listing → Add food items (linked to provider).

Update Claim → Change claim status (e.g., Pending → Completed).

Delete Listing → Remove expired or incorrect food listing.

# Project Structure
project/
│── app.py              # Streamlit application
│── create_db.py        # Database schema setup (tables with AUTO_INCREMENT PKs)
│── requirements.txt     # Python dependencies
│── README.md            # Project documentation

# Explainatory Video:https://www.loom.com/share/902014d81480474f931ede4613859a16?sid=341569d7-b8ae-4191-a05e-b644e29dd56a

