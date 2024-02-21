#Login
import mysql.connector
import random
import string

class User:
    def __init__(self, username, address, aadhar, mobile, balance):
        self.username = username
        self.address = address
        self.aadhar = aadhar
        self.mobile = mobile
        self.balance = balance
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

def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    user = fetch_user(username, password)
    if user:
        print("Welcome,", user.username)
        show_options(user)
    else:
        print("Invalid username or password.")

def fetch_user(username, password):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor(dictionary=True)

        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, password))
        user_data = cursor.fetchone()

        if user_data:
            user = User(user_data['username'], user_data['address'], user_data['aadhar'], user_data['mobile'], user_data['balance'])
            user.credit_card = {"number": user_data['credit_card_number'], "pin": user_data['credit_card_pin'], "cvv": user_data['credit_card_cvv']}
            user.debit_card = {"number": user_data['debit_card_number'], "pin": user_data['debit_card_pin'], "cvv": user_data['debit_card_cvv']}
            return user
        else:
            return None

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_options(user):
    print("\nOptions:")
    print("1. Display Account Information and Balance")
    print("2. List of Beneficiaries")
    print("3. List of Cards")
    print("4. Add Beneficiary")
    print("5. Update Account Information")
    print("6. Transfer Funds")
    print("7. Change Card PINs")
    print("8. Register New Credit Card")
    print("9. Exit")

    choice = input("Enter your choice: ")
    if choice == '1':
        show_user_info(user)
        show_options(user)
    elif choice == '2':
        list_beneficiaries(user)
    elif choice == '3':
        list_cards(user)
    elif choice == '4':
        add_beneficiary(user)
    elif choice == '5':
        update_account_info(user)
    elif choice == '6':
        transfer_funds(user)
    elif choice == '7':
        change_card_pins(user)
    elif choice == '8':
        register_new_credit_card(user)
    elif choice == '9':
        print("Exiting...")
    else:
        print("Invalid choice. Please try again.")
        show_options(user)

def show_user_info(user):
    print("Account Information:")
    print("Username:", user.username)
    print("Account Number:", user.account_number)
    print("Balance:", user.balance)

def list_beneficiaries(user):
    print("List of Beneficiaries:")
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor()

        sql = "SELECT name, account_number FROM beneficiaries WHERE username = %s"
        cursor.execute(sql, (user.username,))
        beneficiaries = cursor.fetchall()

        if beneficiaries:
            for beneficiary in beneficiaries:
                print(f"Name: {beneficiary[0]}, Account Number: {beneficiary[1]}")
        else:
            print("No beneficiaries found.")

    except mysql.connector.Error as error:
        print("Error while fetching beneficiaries:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_options(user)

def list_cards(user):
    print("List of Cards:")
    print("Credit Card Number:", user.credit_card["number"])
    print("Debit Card Number:", user.debit_card["number"])
    show_options(user)

def add_beneficiary(user):
    print("Add Beneficiary:")
    name = input("Enter beneficiary name: ")
    account_number = input("Enter beneficiary account number: ")

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor()

        sql = "INSERT INTO beneficiaries (name, account_number, username) VALUES (%s, %s, %s)"
        val = (name, account_number, user.username)
        cursor.execute(sql, val)
        connection.commit()
        print("Beneficiary added successfully!")

    except mysql.connector.Error as error:
        print("Error while adding beneficiary:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    list_beneficiaries(user)

def update_account_info(user):
    print("Update Account Information:")
    additional_balance = int(input("Enter additional balance: "))  # Input additional balance to be added

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor()

        # Fetch the current balance from the database
        cursor.execute("SELECT balance FROM users WHERE username = %s", (user.username,))
        current_balance = int(cursor.fetchone()[0])  # Convert fetched balance to int

        # Calculate the updated balance (previous balance + additional balance)
        updated_balance = current_balance + additional_balance

        # Update the balance in the database
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (updated_balance, user.username))
        connection.commit()
        print("Balance updated successfully!")

        # Update the balance attribute of the User object
        user.balance = updated_balance

    except mysql.connector.Error as error:
        print("Error while updating balance:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_user_info(user)  # Show updated user info
    show_options(user)

def transfer_funds(user):
    print("Transfer Funds:")
    recipient_username = input("Enter recipient's username: ")
    amount = int(input("Enter amount to transfer: "))

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor()

        # Check if recipient exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (recipient_username,))
        recipient_data = cursor.fetchone()
        if not recipient_data:
            print("Recipient not found.")
            return

        # Fetch the list of beneficiaries for the sender's account
        cursor.execute("SELECT account_number FROM beneficiaries WHERE username = %s", (user.username,))
        beneficiary_accounts = [row[0] for row in cursor.fetchall()]

        # Check if recipient is a beneficiary
        cursor.execute("SELECT account_number FROM users WHERE username = %s", (recipient_username,))
        recipient_account_number = cursor.fetchone()[0]
        if recipient_account_number not in beneficiary_accounts:
            print("The recipient is not your beneficiary.")
            return

        # Check if sender has sufficient balance
        if user.balance < amount:
            print("Insufficient funds.")
            return

        # Update sender's balance
        cursor.execute("UPDATE users SET balance = balance - %s WHERE username = %s", (amount, user.username))

        # Update recipient's balance
        cursor.execute("UPDATE users SET balance = balance + %s WHERE username = %s", (amount, recipient_username))

        # Commit the transaction
        connection.commit()

        # Update user object balance
        user.balance -= amount

        print(f"{amount} funds transferred successfully to {recipient_username}")

    except mysql.connector.Error as error:
        print("Error transferring funds:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_options(user)


def change_card_pins(user):
    new_pin = input("Enter new PIN for Credit Card: ")
    # Implement change PIN functionality for credit and debit cards
    print("PIN changed successfully!")

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor()

        sql = "UPDATE users SET credit_card_pin = %s WHERE username = %s"
        val = (new_pin, user.username)
        cursor.execute(sql, val)
        connection.commit()
        print("Credit card PIN updated successfully!")

    except mysql.connector.Error as error:
        print("Error while updating credit card PIN:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_options(user)

def register_new_credit_card(user):
    new_credit_card = user.generate_card("Credit")
    # Implement registration of new credit card
    print("New credit card registered successfully!")
    print("Credit Card Number:", new_credit_card["number"])
    print("PIN:", new_credit_card["pin"])
    print("CVV:", new_credit_card["cvv"])
    show_options(user)

def main():
    print("Welcome to Login System")
    login_user()

if __name__ == "__main__":
    main()
