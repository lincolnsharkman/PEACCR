import streamlit as st
import os
import json
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import requests


# Function to generate a unique code
def generate_unique_code():
    return str(uuid.uuid4())


# Function to create a new user file
def create_user_file(username, unique_code):
    user_data = {
        "username": username,
        "income": 0,
        "expenses": []
    }
    with open(f"{unique_code}.json", "w") as file:
        json.dump(user_data, file)


# Function to load user data
def load_user_data(unique_code):
    if os.path.exists(f"{unique_code}.json"):
        with open(f"{unique_code}.json", "r") as file:
            return json.load(file)
    else:
        return None


# Function to save user data
def save_user_data(unique_code, user_data):
    with open(f"{unique_code}.json", "w") as file:
        json.dump(user_data, file)


# Function to get current prices
def get_current_prices():
    btc_usd = requests.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json").json()["bpi"]["USD"]["rate"]

    gold_response = requests.get("https://www.goldapi.io/api/XAU/USD").json()
    gold_price = gold_response["price"] if "price" in gold_response else "N/A"

    irr_usd = requests.get("https://api.exchangerate-api.com/v4/latest/IRR").json()["rates"]["USD"]
    return btc_usd, gold_price, irr_usd


# Streamlit app
st.title("Personal Accountant App")

# User registration
if "unique_code" not in st.session_state:
    username = st.text_input("Enter your username:")
    if st.button("Register"):
        unique_code = generate_unique_code()
        create_user_file(username, unique_code)
        st.session_state.unique_code = unique_code
        st.write(f"Your unique code is: {unique_code}")

# User login
unique_code = st.text_input("Enter your unique code:")
if st.button("Login"):
    user_data = load_user_data(unique_code)
    if user_data:
        st.session_state.unique_code = unique_code
        st.write(f"Welcome back, {user_data['username']}!")
    else:
        st.write("User not found")

# User actions
if "unique_code" in st.session_state:
    user_data = load_user_data(st.session_state.unique_code)

    # Add income
    income = st.number_input("Enter your income:", min_value=0)
    if st.button("Add Income"):
        user_data["income"] += income
        save_user_data(st.session_state.unique_code, user_data)
        st.write("Income added successfully")

    # Add expense
    expense = st.number_input("Enter your expense:", min_value=0)
    explanation = st.text_input("Enter explanation for expense (optional):")
    if st.button("Add Expense"):
        user_data["expenses"].append({"amount": expense, "explanation": explanation})
        user_data["income"] -= expense
        save_user_data(st.session_state.unique_code, user_data)
        st.write("Expense added successfully")

    # Display table of incomes, expenses, explanations, and current balance
    st.write("### Income and Expenses Table")
    expenses_df = pd.DataFrame(user_data["expenses"])
    st.write(expenses_df)
    st.write(f"Current Balance: {user_data['income']}")

    # Plot income and expenses
    st.write("### Income and Expenses Graph")
    fig, ax = plt.subplots()
    ax.bar(["Income"], [user_data["income"]], label="Income")
    ax.bar(["Expenses"], [sum(exp["amount"] for exp in user_data["expenses"])], label="Expenses")
    ax.legend()
    st.pyplot(fig)

    # Predict future income and expenses (simple example)
    st.write("### Future Income and Expenses Prediction")
    future_income = user_data["income"] * 1.1  # Example prediction
    future_expenses = sum(exp["amount"] for exp in user_data["expenses"]) * 1.1  # Example prediction
    st.write(f"Predicted future income: {future_income}")
    st.write(f"Predicted future expenses: {future_expenses}")

    # Plot future income and expenses
    st.write("### Future Income and Expenses Graph")
    fig, ax = plt.subplots()
    ax.bar(["Future Income"], [future_income], label="Future Income")
    ax.bar(["Future Expenses"], [future_expenses], label="Future Expenses")
    ax.legend()
    st.pyplot(fig)

    # Reset user data
    if st.button("Reset"):
        create_user_file(user_data["username"], st.session_state.unique_code)
        st.write("User data reset successfully")

# Display current prices and graphs
st.sidebar.title("Current Prices")
btc_usd, gold_price, irr_usd = get_current_prices()
st.sidebar.write(f"BTC to USD: {btc_usd}")
st.sidebar.write(f"Gold Price (USD): {gold_price}")
st.sidebar.write(f"IRR to USD: {irr_usd}")

# Plot current prices
st.sidebar.write("### Current Prices Graph")
fig, ax = plt.subplots()
ax.bar(["BTC to USD", "Gold Price (USD)", "IRR to USD"], [btc_usd, gold_price, irr_usd])
st.sidebar.pyplot(fig)
