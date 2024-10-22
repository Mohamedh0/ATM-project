import tkinter as tk
from tkinter import messagebox
import csv
import os
import random

# Define the User class
class User:
    def __init__(self, name, pwd, card_number, pin, initial_balance=0):
        self.name = name
        self.pwd = pwd
        self.card_number = card_number
        self.pin = pin
        self.balance = initial_balance
        self.transaction_history = []
    
    def checkPassword(self, pwd):
        return self.pwd == pwd
    
    def checkPin(self, entered_pin):
        return self.pin == entered_pin
    
    def updateBalance(self, amount, login_system):
        """Update balance and save changes to CSV."""
        self.balance += amount
        login_system.saveAllAccounts()  # Save to CSV after updating balance
        return self.balance
    
    def getBalance(self):
        return self.balance
    
    def addTransaction(self, transaction, login_system):
        """Add a transaction to the history and save changes to CSV."""
        self.transaction_history.append(transaction)
        login_system.saveAllAccounts()  # Save to CSV after adding transaction
    
    def getTransactionHistory(self):
        return self.transaction_history

# Define the Login class
class Login:
    def __init__(self, csv_file=r'D:\accounts.csv'):
        self.accounts = {}
        self.csv_file = csv_file
        self.loadAccounts()

    def loadAccounts(self):
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 6:
                        continue 

                    name, pwd, card_number, pin, balance, history = row
                    user = User(name, pwd, card_number, pin, float(balance))
                    user.transaction_history = history.split("|")
                    self.accounts[name] = user

    def saveAllAccounts(self):
        """Save all account data back to the CSV file."""
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            for user in self.accounts.values():
                writer.writerow([
                    user.name, user.pwd, user.card_number, user.pin,
                    user.balance, "|".join(user.transaction_history)
                ])

    def addAccount(self, userName, password, balance=0):
        if userName in self.accounts:
            print("Account already exists.")
            return False
        
        # Generate a random card number and PIN
        card_number = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        pin = f"{random.randint(1000, 9999)}"
        
        new_user = User(userName, password, card_number, pin, balance)
        self.accounts[userName] = new_user
        self.saveAllAccounts()  # Save new account to CSV
        print(f"Account created successfully for {userName} with card number {card_number} and PIN {pin}.")
        return True

    def login(self, card_number, pin):
        for user in self.accounts.values():
            if user.card_number == card_number and user.checkPin(pin):
                return user
        return None

# Define the Bank class
class Bank:
    def __init__(self, login_system):
        self.login_system = login_system

    def getBalance(self, card_number, pin):
        user = self.login_system.login(card_number, pin)
        if user:
            return user.getBalance()
        return None

# GUI using Tkinter
class ATM_GUI:
    def __init__(self, root, login_system):
        self.root = root
        self.login_system = login_system
        self.current_user = None
        
        self.root.title("ATM System")
        self.root.geometry("400x300")
        
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_screen()

        tk.Label(self.root, text="ATM Main Menu").pack(pady=10)
        
        tk.Button(self.root, text="Login", command=self.create_login_screen).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.create_registration_screen).pack(pady=5)

    def create_login_screen(self):
        self.clear_screen()
        
        # Create login screen UI
        tk.Label(self.root, text="Enter Card Number").pack(pady=10)
        self.card_number_entry = tk.Entry(self.root)
        self.card_number_entry.pack(pady=5)
        
        tk.Label(self.root, text="Enter PIN").pack(pady=10)
        self.pin_entry = tk.Entry(self.root, show="*")
        self.pin_entry.pack(pady=5)
        
        tk.Button(self.root, text="Login", command=self.login_user).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.create_main_menu).pack(pady=5)

    def create_registration_screen(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Enter your name").pack(pady=10)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)
        
        tk.Label(self.root, text="Enter password").pack(pady=10)
        self.pwd_entry = tk.Entry(self.root, show="*")
        self.pwd_entry.pack(pady=5)
        
        tk.Button(self.root, text="Register", command=self.register_user).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.create_main_menu).pack(pady=5)

    def register_user(self):
        name = self.name_entry.get()
        password = self.pwd_entry.get()

        if name and password:
            if self.login_system.addAccount(name, password):
                user = self.login_system.accounts[name]
                messagebox.showinfo("Account Created", 
                    f"Account created successfully!\nCard Number: {user.card_number}\nPIN: {user.pin}")
                self.create_main_menu()
            else:
                messagebox.showerror("Error", "Account already exists.")
        else:
            messagebox.showwarning("Input Error", "Please enter both name and password.")

    def login_user(self):
        card_number = self.card_number_entry.get()
        pin = self.pin_entry.get()

        if card_number and pin:
            user = self.login_system.login(card_number, pin)
            if user:
                self.current_user = user
                messagebox.showinfo("Success", f"Welcome {user.name}!")
                self.create_user_menu()
            else:
                messagebox.showerror("Error", "Invalid card number or PIN")
        else:
            messagebox.showwarning("Input Error", "Please enter both card number and PIN")

    def create_user_menu(self):
        self.clear_screen()

        # User Menu UI
        tk.Label(self.root, text="ATM User Menu").pack(pady=10)
        
        tk.Button(self.root, text="Deposit", command=self.deposit_screen).pack(pady=5)
        tk.Button(self.root, text="Withdraw", command=self.withdraw_screen).pack(pady=5)
        tk.Button(self.root, text="Check Balance", command=self.check_balance).pack(pady=5)
        tk.Button(self.root, text="Transaction History", command=self.transaction_history).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.create_main_menu).pack(pady=20)

    def deposit_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Enter amount to deposit").pack(pady=10)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack(pady=5)

        tk.Button(self.root, text="Deposit", command=self.deposit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.create_user_menu).pack(pady=5)

    def deposit(self):
        amount = self.amount_entry.get()
        if amount.isdigit():
            amount = float(amount)
            self.current_user.updateBalance(amount, self.login_system)  # Pass login_system
            self.current_user.addTransaction(f"Deposited: {amount}", self.login_system)  # Pass login_system
            messagebox.showinfo("Success", f"Deposited {amount}. New balance: {self.current_user.getBalance()}")
        else:
            messagebox.showerror("Error", "Invalid amount")

        self.create_user_menu()

    def withdraw_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Enter amount to withdraw").pack(pady=10)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack(pady=5)

        tk.Button(self.root, text="Withdraw", command=self.withdraw).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.create_user_menu).pack(pady=5)

    def withdraw(self):
        amount = self.amount_entry.get()
        if amount.isdigit():
            amount = float(amount)
            if self.current_user.getBalance() >= amount:
                self.current_user.updateBalance(-amount, self.login_system)  # Pass login_system
                self.current_user.addTransaction(f"Withdrew: {amount}", self.login_system)  # Pass login_system
                messagebox.showinfo("Success", f"Withdrew {amount}. New balance: {self.current_user.getBalance()}")
            else:
                messagebox.showerror("Error", "Insufficient balance")
        else:
            messagebox.showerror("Error", "Invalid amount")

        self.create_user_menu()

    def check_balance(self):
        balance = self.current_user.getBalance()
        messagebox.showinfo("Balance", f"Your balance is: {balance}")

    def transaction_history(self):
        history = "\n".join(self.current_user.getTransactionHistory())
        if history:
            messagebox.showinfo("Transaction History", history)
        else:
            messagebox.showinfo("Transaction History", "No transactions found.")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Initialize the application
if __name__ == "__main__":
    root = tk.Tk()
    login_system = Login()
    app = ATM_GUI(root, login_system)
    root.mainloop()
