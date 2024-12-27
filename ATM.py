import streamlit as st
import random
import pandas as pd
import os
import csv
from datetime import datetime

# Denomination Manager for handling ATM denominations
class DenominationManager:
    def __init__(self, denominations, file_path="denominations.csv"):
        self.denominations = denominations
        self.file_path = file_path
        self.availability = self.load_denominations()

    def load_denominations(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                reader = csv.reader(file)
                return {int(row[0]): int(row[1]) for row in reader}
        else:
            return {denom: 50 for denom in self.denominations}

    def save_denominations(self):
        with open(self.file_path, "w", newline="") as file:
            writer = csv.writer(file)
            for denom, count in self.availability.items():
                writer.writerow([denom, count])

    def coins_system(self, amount):
        result = {}
        for coin in self.denominations:
            if amount == 0:
                break
            if coin <= amount and self.availability.get(coin, 0) > 0:
                max_coins = min(amount // coin, self.availability[coin])
                if max_coins > 0:
                    result[coin] = max_coins
                    amount -= max_coins * coin
                    self.availability[coin] -= max_coins
        self.save_denominations()
        if amount > 0:
            return result, amount
        return result

    def reset_denominations(self):
        self.availability = {denom: 50 for denom in self.denominations}
        self.save_denominations()

# User Class with withdrawal limits
class User:
    def __init__(self, name, pin, card_number, password, email, balance):
        self.name = name
        self.pin = pin
        self.card_number = card_number
        self.password = password
        self.email = email
        self.balance = balance
        self.transaction_history = []
        self.locked = False
        self.daily_withdrawn = 0
        self.monthly_withdrawn = 0
        self.daily_limit = 4000
        self.monthly_limit = 100000
        self.last_withdraw_date = None

    def update_balance(self, amount):
        self.balance += amount

    def reset_withdraw_limits(self):
        """Reset daily and monthly withdrawal limits using datetime."""
        now = datetime.now()
        if not self.last_withdraw_date or self.last_withdraw_date.date() != now.date():
            self.daily_withdrawn = 0
        if not self.last_withdraw_date or self.last_withdraw_date.month != now.month:
            self.monthly_withdrawn = 0
        self.last_withdraw_date = now

    def can_withdraw(self, amount):
        """Check if the user can withdraw the requested amount."""
        self.reset_withdraw_limits()
        if self.locked:
            return False, "Account is locked."
        if amount > self.balance:
            return False, "Insufficient balance."
        if self.daily_withdrawn + amount > self.daily_limit:
            return False, f"Daily withdrawal limit exceeded. You can withdraw up to ${self.daily_limit - self.daily_withdrawn} today."
        if self.monthly_withdrawn + amount > self.monthly_limit:
            return False, f"Monthly withdrawal limit exceeded. You can withdraw up to ${self.monthly_limit - self.monthly_withdrawn} this month."
        return True, ""

    def record_transaction(self, message):
        """Record the transaction and update withdrawal limits."""
        now = datetime.now()
        self.reset_withdraw_limits()
        self.transaction_history.append(f"{message} at {now}")
        self.last_withdraw_date = now

    def withdraw(self, amount):
        """Perform the withdrawal if possible."""
        can_withdraw, message = self.can_withdraw(amount)
        if can_withdraw:
            self.update_balance(-amount)
            self.daily_withdrawn += amount
            self.monthly_withdrawn += amount
            self.record_transaction(f"Withdrew ${amount}")
            return True, f"Successfully withdrew ${amount}."
        return False, message

    def get_transaction_history(self):
        return self.transaction_history

    def check_password(self, password):
        return self.password == password

# Admin Class
class Admin:
    def __init__(self, email, password, csv_file="users.csv"):
        self.email = email
        self.password = password
        self.csv_file = csv_file
        self.users = self.load_users()

    def load_users(self):
        users = {}
        if os.path.exists(self.csv_file):
            with open(self.csv_file, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 7:
                        row.append("")
                    name, pin, password, email, card_number, balance, history = row
                    user = User(name, pin, card_number, password, email, float(balance))
                    user.transaction_history = history.split("|") if history else []
                    users[card_number] = user
        return users

    def save_users(self):
        with open(self.csv_file, "w", newline="") as file:
            writer = csv.writer(file)
            for user in self.users.values():
                writer.writerow([user.name, user.pin, user.password, user.email, user.card_number, user.balance, "|".join(user.transaction_history)])

    def add_user(self, name, password, email, balance=0):
        pin = str(random.randint(1000, 9999))
        card_number = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        new_user = User(name, pin, card_number, password, email, balance)
        self.users[card_number] = new_user
        self.save_users()
        return new_user

    def delete_user(self, email):
        self.users = {card_number: user for card_number, user in self.users.items() if user.email != email}
        self.save_users()

    def lock_user(self, email):
        for user in self.users.values():
            if user.email == email:
                user.locked = True

    def unlock_user(self, email):
        for user in self.users.values():
            if user.email == email:
                user.locked = False

    def get_all_users(self):
        return self.users

    def check_password(self, password):
        return self.password == password

# Streamlit Pages
st.session_state.setdefault("user", None)
st.session_state.setdefault("admin", None)

def welcome_page():
    st.title("Welcome to DXMH Bank")
    st.write("A trusted bank for all your financial needs.")
    if st.button("Proceed to Login"):
        st.session_state["page"] = "login"

def login_page():
    st.title("Login to DXMH Bank")
    login_option = st.radio("Login as", ["User", "Admin"])

    if login_option == "User":
        card_number = st.text_input("Enter your card number")
        pin = st.text_input("Enter your PIN", type="password")
        if st.button("Login"):
            user = admin.users.get(card_number)
            if user and user.pin == pin:
                st.session_state["user"] = user
                st.success(f"Welcome {user.name}!")
                st.session_state["page"] = "user_dashboard"
            else:
                st.error("Invalid card number or PIN.")

    elif login_option == "Admin":
        email = st.text_input("Enter admin email")
        password = st.text_input("Enter admin password", type="password")
        if st.button("Login"):
            if email == admin.email and admin.check_password(password):
                st.session_state["admin"] = admin
                st.success("Admin login successful!")
                st.session_state["page"] = "admin_dashboard"
            else:
                st.error("Invalid admin credentials.")

def user_dashboard():
    user = st.session_state["user"]
    st.sidebar.title(f"Welcome, {user.name}")
    action = st.sidebar.radio("Actions", ["Check Balance", "Withdraw Money", "Deposit Money", "Transaction History", "Logout"])

    if action == "Check Balance":
        st.write(f"Your current balance: ${user.balance:.2f}")

    elif action == "Withdraw Money":
        amount = st.number_input("Enter amount to withdraw", min_value=1)
        if st.button("Withdraw"):
            success, message = user.withdraw(amount)
            if success:
                st.success(message)
            else:
                st.error(message)

    elif action == "Deposit Money":
        amount = st.number_input("Enter amount to deposit", min_value=1)
        if st.button("Deposit"):
            user.update_balance(amount)
            user.record_transaction(f"Deposited ${amount}")
            st.success(f"Successfully deposited ${amount}.")

    elif action == "Transaction History":
        st.write("Transaction History:")
        for transaction in user.get_transaction_history():
            st.write(transaction)

    elif action == "Logout":
        st.session_state["user"] = None
        st.session_state["page"] = "welcome"

def admin_dashboard():
    st.sidebar.title("Admin Actions")
    action = st.sidebar.radio("Actions", ["Add User", "Delete User", "Lock/Unlock User", "View Users", "Manage Denominations", "Logout"])

    if action == "Add User":
        name = st.text_input("User's name")
        email = st.text_input("User's email")
        password = st.text_input("User's password")
        balance = st.number_input("Initial balance", min_value=0.0)
        if st.button("Add User"):
            user = admin.add_user(name, password, email, balance)
            st.success(f"User added: {user.name} (Card: {user.card_number}, PIN: {user.pin})")

    elif action == "Delete User":
        email = st.text_input("Email of user to delete")
        if st.button("Delete User"):
            admin.delete_user(email)
            st.success(f"User with email {email} deleted.")

    elif action == "Lock/Unlock User":
        email = st.text_input("User's email")
        lock_action = st.selectbox("Action", ["Lock", "Unlock"])
        if st.button("Apply"):
            if lock_action == "Lock":
                admin.lock_user(email)
                st.success(f"User with email {email} locked.")
            elif lock_action == "Unlock":
                admin.unlock_user(email)
                st.success(f"User with email {email} unlocked.")

    elif action == "View Users":
        st.write("All Users:")
        users_df = pd.DataFrame([user.__dict__ for user in admin.get_all_users().values()])
        st.dataframe(users_df)

    elif action == "Manage Denominations":
        st.write("Current Denomination Status:")
        st.write(denomination_manager.availability)

        denomination = st.selectbox("Select Denomination to Update", denomination_manager.denominations)
        count = st.number_input("Enter New Count", min_value=0)

        if st.button("Update Denomination"):
            denomination_manager.availability[denomination] = count
            denomination_manager.save_denominations()
            st.success(f"Updated {denomination} denomination count to {count}.")

    elif action == "Logout":
        st.session_state["admin"] = None
        st.session_state["page"] = "welcome"

# App Navigation
admin = Admin("admin@dxmh.com", "admin123")
denominations = [100, 50, 20, 10, 5, 1]
denomination_manager = DenominationManager(denominations)

if "page" not in st.session_state:
    st.session_state["page"] = "welcome"

if st.session_state["page"] == "welcome":
    welcome_page()
elif st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "user_dashboard":
    user_dashboard()
elif st.session_state["page"] == "admin_dashboard":
    admin_dashboard()
