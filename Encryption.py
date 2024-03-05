import mysql.connector
import random
import re
import hashlib
import getpass

class User:
    def __init__(self, username, address, aadhar, mobile, balance=0):
        self.username = username
        self.address = address
        self.aadhar = aadhar
        self.mobile = mobile
        self.balance = balance
        self.credit_card = self.generate_card("Credit")
        self.debit_card = self.generate_card("Debit")
        self.account_number = self.generate_account_number()

    def generate_card(self, card_type):
        card_number = ''.join(random.choices('0123456789', k=16))
        pin = ''.join(random.choices('0123456789', k=4))
        cvv = ''.join(random.choices('0123456789', k=3))
        return {"type": card_type, "number": card_number, "pin": hash_pin(pin), "cvv": hash_cvv(cvv)}

    def generate_account_number(self):
        account_number = ''.join(random.choices('0123456789', k=random.randint(11, 14)))
        return account_number

def hash_password(password):
    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def hash_pin(pin):
    # Hash the PIN using SHA-256
    hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
    return hashed_pin

def hash_cvv(cvv):
    # Hash the CVV using SHA-256
    hashed_cvv = hashlib.sha256(cvv.encode()).hexdigest()
    return hashed_cvv

def register_user():
    # Input validation functions
    def validate_username(username):
        return bool(re.match(r'^[a-zA-Z\s]+$', username))

    def validate_address(address):
        return bool(re.match(r'^[a-zA-Z0-9\s,-]+$', address))

    def validate_aadhar(aadhar):
        aadhar = ''.join(filter(str.isdigit, aadhar))
        if len(aadhar) == 12:
            aadhar_with_gaps = ' '.join(aadhar[i:i + 4] for i in range(0, len(aadhar), 4))
            return aadhar_with_gaps
        else:
            return None

    def validate_mobile(mobile):
        return bool(re.match(r'^[7-9][0-9]{9}$', mobile))

    def validate_password(password):
        return bool(re.match(r'^[a-zA-Z0-9!@#$%^&*()-_+=]{8,}$', password))

    # Get valid input from user
    while True:
        username = input("Enter username (alphabets only): ")
        if validate_username(username):
            break
        else:
            print("Invalid username. Please enter alphabets only.")

    while True:
        address = input("Enter address (alphanumeric with special characters): ")
        if validate_address(address):
            break
        else:
            print("Invalid address. Please enter alphanumeric characters with special characters.")

    while True:
        aadhar = input("Enter Aadhar number (12 digits with automatic gaps insertion after every 4 digits): ")
        aadhar_with_gaps = validate_aadhar(aadhar)
        if aadhar_with_gaps:
            print("Aadhar number with automatic gaps insertion:")
            print(aadhar_with_gaps)
            # Check if Aadhar number already exists
            if is_unique("aadhar", aadhar):
                break
            else:
                print("Aadhar number already exists. Please enter a unique Aadhar number.")
        else:
            print("Invalid Aadhar number. Please enter 12 digits.")

    while True:
        mobile = input("Enter mobile number (10 digits): ")
        if validate_mobile(mobile):
            # Check if mobile number already exists
            if is_unique("mobile", mobile):
                break
            else:
                print("Mobile number already exists. Please enter a unique mobile number.")
        else:
            print("Invalid mobile number.")

    while True:
        password = getpass.getpass("Enter password (minimum 8 characters, alphanumeric with special characters): ")
        if validate_password(password):
            break
        else:
            print("Invalid password. Password should be at least 8 characters long and contain alphanumeric characters with special charcters.")

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
    main_menu()

def is_unique(field, value):
    # Check if the given field value is unique in the database
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM users WHERE {field} = %s", (value,))
        result = cursor.fetchone()

        if result:
            return False
        else:
            return True

    except mysql.connector.Error as error:
        print("Error while checking uniqueness:", error)
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

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

        # Insert user data into 'users' table
        insert_user_query = "INSERT INTO users (username, address, aadhar, mobile, password, account_number, balance, credit_card_number, credit_card_pin, credit_card_cvv, debit_card_number, debit_card_pin, debit_card_cvv) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        user_data = (user.username, user.address, user.aadhar, user.mobile, hash_password(password), user.account_number, user.balance, user.credit_card["number"], user.credit_card["pin"], user.credit_card["cvv"], user.debit_card["number"], user.debit_card["pin"], user.debit_card["cvv"])
        cursor.execute(insert_user_query, user_data)

        # Commit changes
        connection.commit()

    except mysql.connector.Error as error:
        print("Error while storing user data in MySQL:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def login_user():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    user = fetch_user(username, password)
    if user:
        print("Welcome,", user.username)
        show_options(user)
    else:
        print("Invalid username or password. Would you like to:")
        print("1. Retry Login")
        print("2. Reset Password")
        choice = input("Enter your choice: ")
        if choice == '1':
            login_user()
        elif choice == '2':
            reset_password_main(username)
        else:
            print("Invalid choice.")
            main_menu()

def reset_password_main(username):
    new_password = getpass.getpass("Enter new password: ")
    confirm_password = getpass.getpass("Confirm new password: ")

    if new_password == confirm_password:
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshi@526",
                database="Banking"
            )
            cursor = connection.cursor()

            # Hash the new password using SHA-256
            hashed_password = hash_password(new_password)

            # Update the password in the database
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, username))
            connection.commit()
            print("Password reset successful!")

        except mysql.connector.Error as error:
            print("Error while resetting password:", error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        print("Passwords do not match. Please try again.")

    main_menu()

def fetch_user(username, password):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor(dictionary=True)

        # Hash the password input for comparison
        hashed_password = hash_password(password)

        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, hashed_password))
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

def initial_deposit(user):
    try:
        while True:
            deposit_amount_str = input("Enter initial deposit amount: ")
            try:
                deposit_amount = int(deposit_amount_str)
                if deposit_amount < 0:
                    print("Deposit amount cannot be negative. Please enter a positive value.")
                else:
                    break  # Exit the loop if a valid positive integer is entered
            except ValueError:
                print("Invalid input. Please enter a valid integer amount.")
        
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor()

        # Update user's balance with the initial deposit
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (deposit_amount, user.username))
        connection.commit()
        print(f"Your account has been credited with {deposit_amount}. New balance is {user.balance + deposit_amount}.")


        # Update user object balance
        user.balance += deposit_amount

    except mysql.connector.Error as error:
        print("Error making the initial deposit:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_options(user)

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
    
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
        )
        cursor = connection.cursor()

        # Fetch credit card details for the user
        print("Credit Card:")
        print("Card Number:", user.credit_card["number"])
        print("PIN:", user.credit_card["pin"])  # Display actual PIN
        print("CVV:", user.credit_card["cvv"])  # Display actual CVV
        print()

        # Fetch debit card details for the user
        print("Debit Card:")
        print("Card Type: Debit")
        print("Card Number:", user.debit_card["number"])
        print("PIN:", user.debit_card["pin"])  # Display actual PIN
        print("CVV:", user.debit_card["cvv"])  # Display actual CVV
        print()
        
        # Fetch other registered cards for the user from the cards table
        cursor.execute("SELECT card_type, card_number, pin, cvv FROM cards WHERE username = %s", (user.username,))
        other_cards = cursor.fetchall()
        if other_cards:
            print("Newly Registered Card Details:")
            for card in other_cards:
                print(f"Card Type: {card[0]}")
                print(f"Card Number: {card[1]}")
                if card[2] != user.credit_card["pin"] and card[3] != user.credit_card["cvv"]:
                    print("PIN:", "*" * len(card[2]))  # Display asterisks for PIN if it's not the same as the current card
                    print("CVV:", "*" * len(card[3]))  # Display asterisks for CVV if it's not the same as the current card
                else:
                    print("PIN:", card[2])  # Display the actual PIN for existing cards
                    print("CVV:", card[3])  # Display the actual CVV for existing cards
                print()

    except mysql.connector.Error as error:
        print("Error while fetching cards:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    show_options(user) 

def reset_password(user):
    new_password = getpass.getpass("Enter new password: ")
    confirm_password = getpass.getpass("Confirm new password: ")

    if new_password == confirm_password:
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshi@526",
                database="Banking"
            )
            cursor = connection.cursor()

            # Hash the new password using SHA-256
            hashed_password = hash_password(new_password)

            # Update the password in the database
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, user.username))
            connection.commit()
            print("Password reset successful!")

        except mysql.connector.Error as error:
            print("Error while resetting password:", error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        print("Passwords do not match. Please try again.")

    show_options(user)

def reset_pin(user):
    card_type = input("Enter card type (Credit/Debit): ")
    new_pin = getpass.getpass("Enter new PIN (4 digits): ")  # Use getpass.getpass for secure input
    confirm_pin = getpass.getpass("Confirm new PIN: ")

    # Validate new PIN length
    if len(new_pin) != 4 or not new_pin.isdigit():
        print("Invalid PIN. Please enter a 4-digit PIN.")
        retry = input("Do you want to retry? (yes/no): ").lower()
        if retry == 'yes':
            reset_pin(user)
        else:
            show_options(user)
        return

    if new_pin == confirm_pin:
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshi@526",
                database="Banking"
            )
            cursor = connection.cursor()

            # Hash the new PIN using SHA-256
            hashed_pin = hash_pin(new_pin)

            # Update the PIN in the database
            if card_type.lower() == "credit":
                cursor.execute("UPDATE users SET credit_card_pin = %s WHERE username = %s AND credit_card_number = %s", (hashed_pin, user.username, user.credit_card["number"]))
            elif card_type.lower() == "debit":
                cursor.execute("UPDATE users SET debit_card_pin = %s WHERE username = %s AND debit_card_number = %s", (hashed_pin, user.username, user.debit_card["number"]))

            connection.commit()
            print("PIN reset successful!")

        except mysql.connector.Error as error:
            print("Error while resetting PIN:", error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        print("PINs do not match. Please try again.")
        retry = input("Do you want to retry? (yes/no): ").lower()
        if retry == 'yes':
            reset_pin(user)
        else:
            show_options(user)

    show_options(user)

def reset_cvv(user):
    card_type = input("Enter card type (Credit/Debit): ")
    new_cvv = getpass.getpass("Enter new CVV (3 digits): ")  # Use getpass.getpass for secure input
    confirm_cvv = getpass.getpass("Confirm new CVV: ")

    # Validate new CVV length
    if len(new_cvv) != 3 or not new_cvv.isdigit():
        print("Invalid CVV. Please enter a 3-digit CVV.")
        retry = input("Do you want to retry? (yes/no): ").lower()
        if retry == 'yes':
            reset_cvv(user)
        else:
            show_options(user)
        return

    if new_cvv == confirm_cvv:
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshi@526",
                database="Banking"
            )
            cursor = connection.cursor()

            # Hash the new CVV using SHA-256
            hashed_cvv = hash_cvv(new_cvv)

            if card_type.lower() == "credit":
                # Update the CVV for credit card in the database
                cursor.execute("UPDATE users SET credit_card_cvv = %s WHERE username = %s AND credit_card_number = %s", (hashed_cvv, user.username, user.credit_card["number"]))
            elif card_type.lower() == "debit":
                # Update the CVV for debit card in the database
                cursor.execute("UPDATE users SET debit_card_cvv = %s WHERE username = %s AND debit_card_number = %s", (hashed_cvv, user.username, user.debit_card["number"]))

            connection.commit()
            print("CVV reset successful!")

        except mysql.connector.Error as error:
            print("Error while resetting CVV:", error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        print("CVVs do not match. Please try again.")
        retry = input("Do you want to retry? (yes/no): ").lower()
        if retry == 'yes':
            reset_cvv(user)
        else:
            show_options(user)

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
                database="Banking"
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

def show_updated_account_info(user):
    print("Update Account Information:")
    new_address = input("Enter new address: ")

    # Loop until a valid mobile number is entered
    while True:
        new_mobile = input("Enter new mobile number: ")
        if len(new_mobile) == 10 and new_mobile.isdigit() and new_mobile[0] in ['7', '8', '9']:
            break
        else:
            print("Invalid mobile number. Mobile number must be 10 digits starting with 7, 8, or 9.")

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
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

    #show_updated_account_info(user)  # Show updated user info

    show_options(user)  # Show options after updating account info

def transfer_funds(user):
    print("Transfer Funds:")
    while True:
        recipient_username = input("Enter recipient's username: ")
        amount = int(input("Enter amount to transfer: "))

        if amount <= 0:
            print("Amount to transfer must be a positive value.")
            continue  # Restart the loop to prompt the user again

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshi@526",
                database="Banking"
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
def change_card_pins(username):
    print("Which PIN would you like to change?")
    print("1. Credit Card PIN")
    print("2. Debit Card PIN")
    choice = input("Enter your choice (1 or 2): ")

    if choice not in ['1', '2']:
        print("Invalid choice. Please enter 1 or 2.")
        return

    pin_type = "credit_card_pin" if choice == '1' else "debit_card_pin"
    pin_prompt = "Credit Card" if choice == '1' else "Debit Card"

    retry = 'yes'  # Initialize retry variable outside of try block
    while True:
        entered_pin = input(f"Enter your current PIN for {pin_prompt}: ")

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshi@526",
                database="Banking"
            )
            cursor = connection.cursor()

            sql = f"SELECT {pin_type} FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()

            if result is None:
                print(f"No {pin_prompt} PIN found for the user.")
                return

            hashed_pin = result[0]

            if hash_pin(entered_pin) != hashed_pin:
                print("Invalid PIN. Please enter your current PIN.")
                retry = input("Do you want to retry? (yes/no): ").lower()
                if retry != 'yes':
                    break  # Exit the loop and function if user chooses not to retry
            else:
                break

        except mysql.connector.Error as error:
            print(f"Error while fetching {pin_prompt} PIN:", error)
            return
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    # Only proceed to the next steps if the loop was exited without breaking
    if retry == 'yes':
        while True:
            confirm_pin = input(f"Please confirm your current PIN for {pin_prompt}: ")

            if hash_pin(confirm_pin) != hashed_pin:
                print(f"{pin_prompt} PIN confirmation failed.")
                retry = input("Do you want to retry? (yes/no): ").lower()
                if retry != 'yes':
                    break
            else:
                break

        if retry == 'yes':
            new_pin = input(f"Enter new PIN for {pin_prompt}: ")

            try:
                hashed_new_pin = hash_pin(new_pin)

                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Harshi@526",
                    database="Banking"
                )
                cursor = connection.cursor()

                sql = f"UPDATE users SET {pin_type} = %s WHERE username = %s"
                val = (hashed_new_pin, username)
                cursor.execute(sql, val)
                connection.commit()
                print(f"{pin_prompt} PIN updated successfully!")

            except mysql.connector.Error as error:
                print(f"Error while updating {pin_prompt} PIN:", error)
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    else:
        print("Returning to the options menu.")

def register_new_credit_card(user):
    print("Register New Credit Card:")
    card_type = input("Enter card type (Credit/Debit): ")
    
    while True:
        card_number = input("Enter 16-digit card number: ")
        if len(card_number) != 16:
            print("Invalid card number. Please enter a 16-digit card number.")
        else:
            break
    
    pin = ''
    cvv = ''

    while len(pin) != 4:
        pin = getpass.getpass(prompt="Enter 4-digit PIN: ")
        if len(pin) != 4:
            print("PIN must be exactly 4 digits.")

    while len(cvv) != 3:
        cvv = getpass.getpass(prompt="Enter 3-digit CVV: ")
        if len(cvv) != 3:
            print("CVV must be exactly 3 digits.")

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Harshi@526",
            database="Banking"
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
    print("1. Show Account Information")
    print("2. List Beneficiaries")
    print("3. List Cards")
    print("4. Add Beneficiary")
    print("5. Update Account Information")
    print("6. Transfer Funds")
    print("7. Change_card_pins")
    print("8. Reset PIN")
    print("9. Reset CVV")
    print("10. Register New Cards")
    print("11. Logout")
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
        show_updated_account_info(user)
    elif choice == '6':
        transfer_funds(user)
    elif choice == '7':
        change_card_pins(user.username)
    elif choice == '8':
        reset_pin(user)
    elif choice == '9':
        reset_cvv(user)
    elif choice == '10':
        register_new_credit_card(user)
    elif choice == '11':
        print("Logged out successfully.")
    else:
        print("Invalid choice.")
        show_options(user)

def main_menu():
    print("Welcome to the Banking System!")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        register_user()
    elif choice == '2':
        login_user()
    elif choice == '3':
        print("Exiting....")
        return
    else:
        print("Invalid choice. Please try again.")
        main_menu()

if __name__ == "__main__":
    main_menu()
