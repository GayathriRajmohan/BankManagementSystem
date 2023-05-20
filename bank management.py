import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Establish database connection
connection = sqlite3.connect('bank.db')
cursor = connection.cursor()

# Create table if it doesn't exist
cursor.execute("DROP TABLE IF EXISTS accounts")
cursor.execute("DROP TABLE IF EXISTS transactions")
cursor.execute("CREATE TABLE IF NOT EXISTS accounts(account_number INTEGER PRIMARY KEY,customer_name TEXT NOT NULL,balance REAL NOT NULL,password TEXT NOT NULL)")

cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                  (transaction_id INTEGER PRIMARY KEY,
                   account_number INTEGER,
                   transaction_type TEXT NOT NULL,
                   amount REAL NOT NULL,
                   date_time TEXT NOT NULL,
                   FOREIGN KEY (account_number) REFERENCES accounts(account_number))''')
connection.commit()

# Create the main window
window = tk.Tk()
window.title("Bank Management System")

# Function to create a new account
def create_account():
    account_number = int(account_number_entry.get())
    customer_name = customer_name_entry.get()
    password = password_entry.get()
    balance = float(balance_entry.get())

    cursor.execute("SELECT * FROM accounts WHERE account_number=?", (account_number,))
    existing_account = cursor.fetchone()
    if existing_account:
        messagebox.showerror("Error", "Account already exists.")
    else:
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)",(account_number, customer_name, balance, password))
        connection.commit()
        messagebox.showinfo("Success", "Account created successfully.")

    account_number_entry.delete(0,tk.END)
    customer_name_entry.delete(0,tk.END)
    password_entry.delete(0,tk.END)
    balance_entry.delete(0,tk.END)

# Function to login to an account
def login():
    account_number = int(login_account_number_entry.get())
    password = login_password_entry.get()

    cursor.execute("SELECT * FROM accounts WHERE account_number=? AND password=?", (account_number, password))
    account=cursor.fetchone()

    if account:
        messagebox.showinfo("Success", "Login successful.")
        open_account_dashboard(account_number,account)
    else:
        messagebox.showerror("Error", "Invalid account number or password.")

    login_account_number_entry.delete(0,tk.END)
    login_password_entry.delete(0,tk.END)

# Function to open the account dashboard
def open_account_dashboard(account_number,account):
    account_dashboard = tk.Toplevel(window)
    account_dashboard.title("Account Dashboard")

    # Function to credit the account
    def credit_account():
        credit_amount = float(credit_entry.get())
        new_balance = account[2] + credit_amount

        cursor.execute("UPDATE accounts SET balance=? WHERE account_number=?", (new_balance, account_number))
        connection.commit()

        # Save transaction history
        save_transaction(account_number, "Credit", credit_amount)

        messagebox.showinfo("Success", "Account credited successfully.")
        update_balance_label()

        credit_entry.delete(0,tk.END)

    # Function to debit the account
    def debit_account():
        debit_amount = float(debit_entry.get())
        if account[2] >= debit_amount:
            new_balance = account[2] - debit_amount

            cursor.execute("UPDATE accounts SET balance=? WHERE account_number=?", (new_balance, account_number))
            connection.commit()

            # Save transaction history
            save_transaction(account_number, "Debit", debit_amount)

            messagebox.showinfo("Success", "Account debited successfully.")
            update_balance_label()
        else:
            messagebox.showerror("Error", "Insufficient balance.")

        debit_entry.delete(0,tk.END)

    # Function to save transaction history
    def save_transaction(account_number, transaction_type, amount):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount, date_time) VALUES (?, ?, ?, ?)",
                       (account_number, transaction_type, amount, date_time))
        connection.commit()

    # Function to update the balance label
    def update_balance_label():
        cursor.execute("SELECT balance FROM accounts WHERE account_number=?", (account_number,))
        balance = cursor.fetchone()[0]
        balance_label.config(text=f"Balance: {balance}")

    # Function to display transaction history
    def display_transactions():
        transaction_window = tk.Toplevel(account_dashboard)
        transaction_window.title("Transaction History")

        transaction_label = tk.Label(transaction_window, text="Transaction History")
        transaction_label.pack(pady=10)

        cursor.execute("SELECT * FROM transactions WHERE account_number=?", (account_number,))
        transactions = cursor.fetchall()

        transactions_text = "Transaction ID\tType\tAmount\tDate & Time\n"
        for transaction in transactions:
            transactions_text += f"{transaction[0]}\t\t{transaction[2]}\t{transaction[3]}\t{transaction[4]}\n"

        transactions_label = tk.Label(transaction_window, text=transactions_text, justify=tk.LEFT)
        transactions_label.pack(padx=10, pady=10)

    # Create labels and entry fields
    welcome_label = tk.Label(account_dashboard, text=f"Welcome, {account[1]}!")
    welcome_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

    balance_label = tk.Label(account_dashboard, text="")
    balance_label.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
    update_balance_label()

    credit_label = tk.Label(account_dashboard, text="Credit Amount")
    credit_label.grid(row=2, column=0, padx=10, pady=10)

    credit_entry = tk.Entry(account_dashboard)
    credit_entry.grid(row=2, column=1, padx=10, pady=10)

    credit_button = tk.Button(account_dashboard, text="Credit", command=credit_account)
    credit_button.grid(row=2, column=2, padx=10, pady=10)

    debit_label = tk.Label(account_dashboard, text="Debit Amount")
    debit_label.grid(row=3, column=0, padx=10, pady=10)

    debit_entry = tk.Entry(account_dashboard)
    debit_entry.grid(row=3, column=1, padx=10, pady=10)

    debit_button = tk.Button(account_dashboard, text="Debit", command=debit_account)
    debit_button.grid(row=3, column=2, padx=10, pady=10)

    transaction_button = tk.Button(account_dashboard, text="Transaction History", command=display_transactions)
    transaction_button.grid(row=4, column=0, padx=10, pady=10, columnspan=3)

# Create labels and entry fields for account creation
account_number_label = tk.Label(window, text="Account Number")
account_number_label.grid(row=0, column=0, padx=10, pady=10)

account_number_entry = tk.Entry(window)
account_number_entry.grid(row=0, column=1, padx=10, pady=10)

customer_name_label = tk.Label(window, text="Customer Name")
customer_name_label.grid(row=1, column=0, padx=10, pady=10)

customer_name_entry = tk.Entry(window)
customer_name_entry.grid(row=1, column=1, padx=10, pady=10)

password_label = tk.Label(window, text="Password")
password_label.grid(row=2, column=0, padx=10, pady=10)

password_entry = tk.Entry(window, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=10)

balance_label = tk.Label(window, text="Balance")
balance_label.grid(row=3, column=0, padx=10, pady=10)

balance_entry = tk.Entry(window)
balance_entry.grid(row=3, column=1, padx=10, pady=10)

create_button = tk.Button(window, text="Create Account", command=create_account)
create_button.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

# Create labels and entry fields for login
login_account_number_label = tk.Label(window, text="Account Number")
login_account_number_label.grid(row=5, column=0, padx=10, pady=10)

login_account_number_entry = tk.Entry(window)
login_account_number_entry.grid(row=5, column=1, padx=10, pady=10)

login_password_label = tk.Label(window, text="Password")
login_password_label.grid(row=6, column=0, padx=10, pady=10)

login_password_entry = tk.Entry(window, show="*")
login_password_entry.grid(row=6, column=1, padx=10, pady=10)

login_button = tk.Button(window, text="Login", command=login)
login_button.grid(row=7, column=0, padx=10, pady=10, columnspan=2)

# Start the main loop
window.mainloop()

# Close the database connection
connection.close()
