#Register
import mysql.connector
import random
import string
import re

class User:
    def __init__(self, username, address, aadhar, mobile):
        self.username = username
        self.address = address
        self.aadhar = aadhar
        self.mobile = mobile
        self.balance = 0
        self.credit_card = self.generate_card("Credit")
        self.debit_card = self.generate_card("Debit")
        self.account_number = self.generate_account_number()

    def generate_card(self, card_type):
        # Generate random card details
        card_number = ''.join(random.choices(string.digits, k=16))
        pin = ''.join(random.choices(string.digits, k=4))
        cvv = ''.join(random.choices(string.digits, k=3))
        return {"type": card_type, "number": card_number, "pin": pin, "cvv": cvv}

    def generate_account_number(self):
        first_five = "YESB0"
        last_six = ''.join(random.choices(string.digits[1:], k=6))
        return first_five + last_six

def register_user():
    # Input validation functions
    def validate_username(username):
        return username.isalpha()

    def validate_address(address):
        return address.isalnum()

    def validate_aadhar(aadhar):
        return re.match(r'^[0-9]{12}$', aadhar)

    def validate_mobile(mobile):
        return re.match(r'^[0-9]{10}$', mobile)

    def validate_password(password):
        return bool(re.match(r'^[a-zA-Z0-9]{8,}$', password))

    # Get valid input from user
    while True:
        username = input("Enter username (alphabets only): ")
        if validate_username(username):
            break
        else:
            print("Invalid username. Please enter alphabets only.")

    while True:
        address = input("Enter address (alphanumeric): ")
        if validate_address(address):
            break
        else:
            print("Invalid address. Please enter alphanumeric characters only.")

    while True:
        aadhar = input("Enter Aadhar number (12 digits): ")
        if validate_aadhar(aadhar):
            break
        else:
            print("Invalid Aadhar number. Please enter 12 digits.")

    while True:
        mobile = input("Enter mobile number (10 digits): ")
        if validate_mobile(mobile):
            break
        else:
            print("Invalid mobile number. Please enter 10 digits.")

    while True:
        password = input("Enter password (minimum 8 characters, alphanumeric only): ")
        if validate_password(password):
            break
        else:
            print("Invalid password. Password should be at least 8 characters long and contain only alphanumeric characters.")

    user = User(username, address, aadhar, mobile)  # Initialize balance to 0
    print("Registration successful!")
    print("Your account number:", user.account_number)
    print("Your credit card details:")
    print("Number:", user.credit_card["number"])
    print("PIN:", user.credit_card["pin"])
    print("CVV:", user.credit_card["cvv"])
    print("Your debit card details:")
    print("Number:", user.debit_card["number"])
    print("PIN:", user.debit_card["pin"])
    print("CVV:", user.debit_card["cvv"])

    # Store user data in MySQL
    store_in_mysql(user, password)


def store_in_mysql(user, password):
    # Connect to MySQL database
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )

        cursor = connection.cursor()

        # Insert user data into the table
        sql = "INSERT INTO users (username, address, aadhar, mobile, balance, account_number, password, credit_card_number, credit_card_pin, credit_card_cvv, debit_card_number, debit_card_pin, debit_card_cvv) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (user.username, user.address, user.aadhar, user.mobile, user.balance, user.account_number, password, user.credit_card["number"], user.credit_card["pin"], user.credit_card["cvv"], user.debit_card["number"], user.debit_card["pin"], user.debit_card["cvv"])
        cursor.execute(sql, val)

        # Commit changes and close connection
        connection.commit()
        print("User data stored in MySQL successfully!")

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def main():
    print("Welcome to Registration System")
    print("Options:")
    print("1. Register")
    print("2. Exit")

    while True:
        choice = input("Enter your choice: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

