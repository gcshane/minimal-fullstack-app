import streamlit as st
import pandas as pd
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection settings
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Hardcoded password
PASSWORD = os.getenv("PASSWORD")

# Function to load and display items
def load_items():
    try:
        items = list(collection.find({"quantity": {"$gt": 0}}, {'_id': 0}))  # Exclude the MongoDB ID field and filter out items with quantity <= 0
        if items:
            df = pd.DataFrame(items)
            if 'name' in df.columns:
                df.set_index('name', inplace=True)  # Set 'name' as the index
            return df
        else:
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to show the login page
def login():
    st.subheader("Jemma's Second Wardrobe")
    password = st.text_input("winkwonk?", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.success("Login successful")
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Invalid password")

# Function to show the main page after login
def main_page():

    # Inputs for updating or adding items
    st.subheader("Update or Add Item")
    item_name = st.text_input("Item Name")
    quantity = st.number_input("Increment or Decrement", step=1)

    if st.button("Submit"):
        if item_name:
            if quantity == 0:
                st.error("Quantity cannot be zero")
            else:
                try:
                    item = collection.find_one({"name": item_name})
                    if item:
                        # Update existing item
                        new_quantity = item['quantity'] + quantity
                        if new_quantity < 0:
                            new_quantity = 0
                        collection.update_one({"name": item_name}, {"$set": {"quantity": new_quantity}})
                        st.success(f"Item {'incremented' if quantity > 0 else 'decremented'} successfully.")
                    else:
                        # Add new item
                        collection.insert_one({"name": item_name, "quantity": max(0, quantity)})
                        st.success("Item added successfully.")
                    load_items()  # Refresh the item list after adding/updating
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.error("Item name is required")
    
    df = load_items()
    if df is not None:
        st.write("**Inventory List**")
        st.dataframe(df)  # Display as a table
    else:
        st.write("No items found.")

# Function to handle the logout
def logout():
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

# Main application logic
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    st.sidebar.button("Logout", on_click=logout)
    main_page()
else:
    login()