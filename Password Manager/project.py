from bcrypt import hashpw, gensalt, checkpw
from cryptography.fernet import Fernet , InvalidToken
import os
import re
import sqlite3
from getpass import getpass
from dotenv import load_dotenv

def main():
    try:
        init_db()
        load_master_key()
        load_master_passwd()
        while True:
            mode = input("Please choose an option (add,update,view,delete,exit) : ").lower().strip()

            if mode == "exit" :
                print("You have successfully exited..")
                break

            if mode == "add" :
                website,user_name,conn = get_details()
                passwd = get_passwd()
                add(conn,website,user_name,passwd)

            elif mode == "update" :
                website,user_name,conn = get_details()
                old_passwd = getpass("Password : ").strip()
                new_passwd = getpass("New password : ").strip()
                update(conn,website,user_name,old_passwd,new_passwd)

            elif mode == "view" :
                conn = sqlite3.connect('Accounts.db')
                ent_master_passwd = getpass("Enter master password : ").strip()
                view(conn,ent_master_passwd)

            elif mode == "delete" :
                website,user_name,conn = get_details()
                passwd = getpass("Password : ").strip()
                consent = input("Are you sure you wan't to delete this account? (yes/no)").lower().strip()
                delete(conn,website,user_name,passwd,consent)
            else:
                print("Chosen mode doesn't exist..")
    except Exception as e:
        print(f"An unexpected error occurred in main : {e}")


def init_db():
    '''Setting up the database'''

    try:
        conn = sqlite3.connect('Accounts.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL,
                            website TEXT NOT NULL)''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"sqlite error : {e}")
    except Exception as e:
        print(f"An unexpected error occured in init_db : {e}")

# Creates a master key used for encrypting and decrypting passwords and stores the master key in .env file only one time..
def load_master_key():
    '''loading the master key (which will be used for encrypting passwords)'''

    try:
        load_dotenv()
        master_key = os.getenv('MASTER_KEY')
        if not master_key:
            if not os.path.exists(".env"):
                key = Fernet.generate_key()
                with open(".env", "a") as env_file:
                    env_file.write(f"MASTER_KEY={key.decode()}\n")
            else:
                key = Fernet.generate_key()
                with open(".env", "a") as env_file:
                    env_file.write(f"MASTER_KEY={key.decode()}\n")

        load_dotenv()
        master_key = os.getenv('MASTER_KEY')
        return master_key
    except Exception as e:
        print(f"An error occured while loading master key : {e}")


def load_master_passwd():
    '''Creates a master password which user sets , so that in future if user wants to view accounts present he must enter master password..'''

    try:
        master_passwd = os.getenv('MASTER_PASSWORD')
        secret_phrase = os.getenv('SECRET_PHRASE')
        if not (master_passwd and secret_phrase):
            pwd = getpass("Set Master Password : ").strip()
            secret = input("What is your favourite sport ?  ").strip().lower()

    # Master password and secret phrase don't need to be retrieved thus its safer to hash them..
    # Hashing or encryption requires encoding (normal string --> byte string) then later be decoded while writing it to a file (byte string --> normal string)
            hashed_pwd = hashpw(pwd.encode() , gensalt())
            hashed_secret = hashpw(secret.encode() , gensalt())
            with open(".env", "a") as env_file:
                env_file.write(f"MASTER_PASSWORD={hashed_pwd.decode()}\n")
                env_file.write(f"SECRET_PHRASE={hashed_secret.decode()}\n ")

        load_dotenv()
        master_passwd = os.getenv('MASTER_PASSWORD')
        secret_phrase = os.getenv('SECRET_PHRASE')
        return master_passwd, secret_phrase  # Returns a tuple , therefore load_master_password is tuple = (master_passwd,secret_phrase)
    except Exception as e:
        print(f"An error occured while loading master password : {e}")


def encrypt_passwd(pwd):
    '''encrypts passwords'''

    try:
        master_key = load_master_key()
        f = Fernet(master_key)
        return f.encrypt(pwd.encode()).decode()
    except Exception as e:
        print(f"An error occurred while encrypting the password : {e}")


def decrypt_passwd(pwd):
    '''decrypts passwords'''

    try:
        master_key = load_master_key()
        f = Fernet(master_key)
        return f.decrypt(pwd.encode()).decode()
    except InvalidToken as e:
        print(f"Decryption failed : Invalid token")
    except Exception as e:
        print(f"An error occured while decrypting the password : {e}")


def get_details():
    '''gets user details'''

    try:
        website = input("Website name : ").strip()
        user_name = input("Username : ").strip()
        conn = sqlite3.connect('Accounts.db')
        return [website,user_name,conn]
    except Exception as e:
        print(f"An error occurred while getting details : {e}")


def get_passwd():
    '''checks for password strength and accepts the password only if it is strong enough ( i.e pass all the criteria below)'''

    try:
        while True:
            pwd = getpass("Password : ").strip()
            if len(pwd) < 8:
                print("Password must be at least 8 characters long.")

            elif not re.search(r'[A-Z]', pwd):
                print("Password must contain at least one uppercase letter.")

            elif not re.search(r'[a-z]', pwd):
                print("Password must contain at least one lowercase letter.")

            elif not re.search(r'[0-9]', pwd):
                print("Password must contain at least one digit.")

            elif not re.search(r'[@$!_%*?&]', pwd):
                print("Password must contain at least one special character (@$!_%*?&).")

            else:
                print("Password is strong!")
                return pwd
    except Exception as e:
        print(f"An error occurred while getting the password : {e}")


def update_master_passwd():
    '''updates master password using secret phrase in case the user forgets it'''

    try:
        secret = load_master_passwd()[1]   # Since load_master_passwd is a tuple ,its 2nd element is secret_phrase
        entered_secret_phrase = getpass("What is your favourite sport ? ").strip().lower()

        with open (".env") as env_file:
            lines = env_file.readlines()

        if checkpw(entered_secret_phrase.encode(), secret.strip().encode()):
            new_master_pwd = getpass("Update your master password : ")
            new_hashed_master_pwd = hashpw(new_master_pwd.encode() , gensalt())

            for i in range(len(lines)):
                if lines[i].startswith(f"MASTER_PASSWORD="):
                    lines[i] = f"MASTER_PASSWORD={new_hashed_master_pwd.decode()}\n"
                    break
        else:
            print("Incorrect Secret phrase!")

        with open (".env" , "w") as env_file:
            env_file.writelines(lines)

    # This manually updates the environment variable for current session
        os.environ['MASTER_PASSWORD'] = new_hashed_master_pwd.decode()
        print("Master password updated successfully!")
    except Exception as e:
        print(f"An error occurred while updating the master password : {e}")


def add(conn,website,user_name,passwd):
    '''adds new account to the databse'''

    try:
        encrypted_password = encrypt_passwd(passwd)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO accounts (website, password, username) VALUES (?, ?, ?)",
                    (website, encrypted_password, user_name))
        conn.commit()
        if os.getenv("IS_TESTING") != "True":
            conn.close()
        print("Account added successfully!")
    except sqlite3.Error as e:
        print(f"sqlite error : {e}")
    except Exception as e:
        print(f"An error occurred while adding new account : {e}")

def update(conn,website,user_name,old_passwd,new_passwd):
    '''updates password of an existing account'''

    try:
        encrypted_new_password = encrypt_passwd(new_passwd)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM accounts WHERE username = ? AND website = ?" , (user_name, website))
        record = cursor.fetchone()

        if record:
            if decrypt_passwd(record[0]) == old_passwd:
                cursor.execute("UPDATE accounts SET password = ? WHERE username = ? AND website = ?",
                            (encrypted_new_password, user_name, website))
                conn.commit()
                print("Password updated successfully!")
            else:
                print("Incorrect pasword..")
        else:
            print("Match not found! Please enter correct credentials next time..")
    except sqlite3.Error as e:
        print(f"sqlite error : {e}")
    except Exception as e:
        print(f"An error occurred while updating password : {e}")


def view(conn,ent_master_passwd):
    '''views the existing accounts and passwords only if the correct master password is entered'''

    try:
        master_passwd = load_master_passwd()[0]   # Since load_master_passwd is a tuple , its 1st element is master_passwd
        #if ent_master_passwd == master_passwd :
        if checkpw(ent_master_passwd.encode(), master_passwd.strip().encode()):
            cursor = conn.cursor()
            cursor.execute("SELECT website, username, password FROM accounts")
            records = cursor.fetchall()
            conn.close()
            print("----YOUR STORED ACCOUNTS----")
            for website, user_name, encrypted_passwd in records:
                print(f"Website : {website} , Username : {user_name} , Password : {decrypt_passwd(encrypted_passwd)}")

        else:
            print("Incorrect master password! , ACCESS DENIED..")
            update_mp = input("Do you want to update master password ? (yes/no) ").strip().lower()
            if update_mp in ["yes","no"]:
                if update_mp == "yes" :
                    update_master_passwd()
            else:
                print("Invalid option , master password will not be updated..")
    except sqlite3.Error as e:
        print(f"sqlite error : {e}")
    except Exception as e:
        print(f"An error occurred while viewing existing accounts : {e}")


def delete(conn,website,user_name,passwd,consent):
    '''deletes a particular account'''

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM accounts WHERE username = ? AND website = ?" , (user_name, website))
        records = cursor.fetchone()
        if records:
            if decrypt_passwd(records[0]) == passwd:
                if consent == "yes" :
                    cursor.execute("DELETE FROM accounts WHERE username = ? AND website = ?" , (user_name, website))
                    conn.commit()
                    print("Account deleted successfully!")
            else:
                print("Incorrect password..")
        else:
            print("Match not found! Please enter correct credentials next time..")
    except sqlite3.Error as e:
        print(f"sqlite error : {e}")
    except Exception as e:
        print(f"An error occurred while deleting the account : {e}")


if __name__ == "__main__" :
    main()
