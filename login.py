#Login
import mysql.connector
import random

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
        card_number = ''.join(random.choices('0123456789', k=16))
        pin = ''.join(random.choices('0123456789', k=4))
        cvv = ''.join(random.choices('0123456789', k=3))
        return {"type": card_type, "number": card_number, "pin": pin, "cvv": cvv}

    def generate_account_number(self):
        account_number = ''.join(random.choices('0123456789', k=random.randint(11, 14)))
        return account_number



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
            database="Banking_App"
        )
        cursor = connection.cursor(dictionary=True)

        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, password))
        user_data = cursor.fetchone()

        if user_data:
            user = User(user_data['username'], user_data['address'], user_data['aadhar'], user_data['mobile'], user_data['balance'])
            user.account_number = user_data['account_number'] 
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

def initial_deposit(user):
    try:
        deposit_amount = int(input("Enter initial deposit amount: "))
        if deposit_amount < 0:
            print("Deposit amount cannot be negative.")
            return

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking_App"
        )
        cursor = connection.cursor()

        # Update the user's balance in the database
        cursor.execute("UPDATE users SET balance = balance + %s WHERE username = %s", (deposit_amount, user.username))
        connection.commit()
        print(f"Your account has been credited with {deposit_amount}. New balance is {user.balance + deposit_amount}.")

        # Update the user object's balance attribute
        user.balance += deposit_amount

    except mysql.connector.Error as error:
        print("Error while making the initial deposit:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_account_info(user):
    print("Account Information:")
    print("Account Number:", user.account_number)
    print("Balance:", user.balance)

    if user.balance == 0:
        print("It looks like your account balance is 0. Would you like to make an initial deposit? (yes/no)")
        decision = input().lower()
        if decision == 'yes':
            initial_deposit(user)

    show_options(user)

def show_updated_account_info(user):
    print("Updated Account Information:")
    print("Address:", user.address)
    print("Mobile Number:", user.mobile)
    show_options(user)

def list_beneficiaries(user):
    print("List of Beneficiaries:")
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking_App"
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
    
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking_App"
        )
        cursor = connection.cursor()

        # Fetch credit card details for the user
        print("Credit Card:")
        print("Card Number:", user.credit_card["number"])
        print("PIN:", user.credit_card["pin"])
        print("CVV:", user.credit_card["cvv"])
        print()

        # Fetch debit card details for the user
        print("Debit Card:")
        print("Card Type: Debit")
        print("Card Number:", user.debit_card["number"])
        print("PIN:", user.debit_card["pin"])
        print("CVV:", user.debit_card["cvv"])
        #print("Cardholder Name:", user.username)
        print()

        # Fetch other registered cards for the user from the cards table
        cursor.execute("SELECT card_type, card_number, pin, cvv FROM cards WHERE username = %s", (user.username,))
        other_cards = cursor.fetchall()

        if other_cards:
            print("Newly Registered Card Details:")
            for card in other_cards:
                print("Card Type:", card[0])
                print("Card Number:", card[1])
                print("PIN:", card[2])
                print("CVV:", card[3])
                print("Cardholder Name:", user.username)
                print()
        else:
            print("No additional cards found for this user.")

    except mysql.connector.Error as error:
        print("Error while fetching card details:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_options(user)

def add_beneficiary(user):
    print("Add Beneficiary:")
    while True:
        name = input("Enter beneficiary name: ")
        beneficiary_account_number = input("Enter beneficiary account number: ")

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshi@526",
                database="Banking_App"
            )
            cursor = connection.cursor()

            # Check if the beneficiary account number and name match in the users table
            cursor.execute("SELECT * FROM users WHERE account_number = %s AND username = %s", (beneficiary_account_number, name))
            beneficiary_data = cursor.fetchone()
            if beneficiary_data is None:
                print("Beneficiary account number does not match the provided name.")
                retry = input("Do you want to retry? (yes/no): ").lower()
                if retry != 'yes':
                    break
                continue

            # Insert the beneficiary into the beneficiaries table
            sql = "INSERT INTO beneficiaries (name, account_number, username) VALUES (%s, %s, %s)"
            val = (name, beneficiary_account_number, user.username)
            cursor.execute(sql, val)
            connection.commit()
            print("Beneficiary added successfully!")
            break

        except mysql.connector.Error as error:
            print("Error while adding beneficiary:", error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    list_beneficiaries(user)

def update_account_info(user):
    print("Update Account Information:")
    new_address = input("Enter new address: ")
    new_mobile = input("Enter new mobile number: ")

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking_App"
        )
        cursor = connection.cursor()

        # Update the address and mobile number in the database
        cursor.execute("UPDATE users SET address = %s, mobile = %s WHERE username = %s", (new_address, new_mobile, user.username))
        connection.commit()
        print("Account information updated successfully!")

        # Update the attributes of the User object
        user.address = new_address
        user.mobile = new_mobile

    except mysql.connector.Error as error:
        print("Error while updating account information:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_updated_account_info(user)  # Show updated user info

def transfer_funds(user):
    print("Transfer Funds:")
    while True:
        recipient_username = input("Enter recipient's username: ")
        amount = int(input("Enter amount to transfer: "))

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshi@526",
                database="Banking_App"
            )
            cursor = connection.cursor()

            # Check if recipient exists and is a beneficiary of the sender
            cursor.execute("SELECT * FROM beneficiaries WHERE username = %s AND name = %s", (user.username, recipient_username))
            recipient_data = cursor.fetchone()
            if recipient_data is None:
                print("Recipient not found or not a beneficiary.")
                retry = input("Do you want to retry? (yes/no): ").lower()
                if retry != 'yes':
                    break
                continue

            # Check if sender has sufficient balance
            if user.balance < amount:
                print("Insufficient funds.")
                retry = input("Do you want to retry? (yes/no): ").lower()
                if retry != 'yes':
                    break
                continue

            # Update sender's balance
            cursor.execute("UPDATE users SET balance = balance - %s WHERE username = %s", (amount, user.username))

            # Update recipient's balance
            cursor.execute("UPDATE users SET balance = balance + %s WHERE username = %s", (amount, recipient_username))

            # Commit the transaction
            connection.commit()

            # Update user object balance
            user.balance -= amount

            print(f"{amount} funds transferred successfully to {recipient_username}")
            break

        except mysql.connector.Error as error:
            print("Error transferring funds:", error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    show_options(user)

def change_card_pins(user):
    old_pin = input("Enter your current PIN for Credit Card: ")

    # Fetch the current PIN from the database
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking_App"
        )
        cursor = connection.cursor()

        sql = "SELECT credit_card_pin FROM users WHERE username = %s"
        cursor.execute(sql, (user.username,))
        result = cursor.fetchone()
        current_pin = result[0]

        # Convert the old_pin to integer for comparison
        old_pin = int(old_pin)

        if old_pin != current_pin:
            print("Invalid PIN. Please enter your current PIN.")
            return

    except mysql.connector.Error as error:
        print("Error while fetching credit card PIN:", error)
        return
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    # Loop for PIN confirmation
    while True:
        confirm_pin = input("Please confirm your current PIN: ")
        confirm_pin = int(confirm_pin)  # Convert to integer for comparison

        if confirm_pin != current_pin:
            print("PIN confirmation failed.")
            retry = input("Do you want to retry? (yes/no): ").lower()
            if retry != 'yes':
                return
        else:
            break  # Break out of the loop if confirmation succeeds

    new_pin = input("Enter new PIN for Credit Card: ")

    try:
        # Convert the new_pin to integer before updating the database
        new_pin = int(new_pin)

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking_App"
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
    print("Register New Credit Card:")
    card_type = input("Enter card type (Credit/Debit): ")
    
    while True:
        card_number = input("Enter 16-digit card number: ")
        if len(card_number) != 16:
            print("Invalid card number. Please enter a 16-digit card number.")
        else:
            break
    
    while True:
        pin = input("Enter 4-digit PIN: ")
        if len(pin) != 4:
            print("Invalid PIN. Please enter a 4-digit PIN.")
        else:
            break
    
    while True:
        cvv = input("Enter 3-digit CVV: ")
        if len(cvv) != 3:
            print("Invalid CVV. Please enter a 3-digit CVV.")
        else:
            break

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking_App"
        )
        cursor = connection.cursor()

        sql = "INSERT INTO cards (username, card_type, card_number, pin, cvv) VALUES (%s, %s, %s, %s, %s)"
        val = (user.username, card_type, card_number, pin, cvv)
        cursor.execute(sql, val)
        connection.commit()
        print("New credit card registered successfully!")

    except mysql.connector.Error as error:
        print("Error while registering new credit card:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_options(user)


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
        show_account_info(user)
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

def main():
    print("Welcome to Login System")
    login_user()

if __name__ == "__main__":
    main()
    
