# PASSWORD MANAGER

## CS50P
>This was my final project for the course : CS50P Introduction to programming with Python.
>python, CS50

## Demonstration on youtube
For the CS50 final project you have to make a video showning your project,
[My Final Project presentation](https://youtu.be/-aGQ_ZCtjTg)


## Tech Stack and Documentation
- [Cryptography-Fernet](https://cryptography.io/en/latest/fernet/)
- [bcrypt](https://pypi.org/project/bcrypt/)
- [sqlite](https://docs.python.org/3/library/sqlite3.html)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [getpass](https://docs.python.org/3/library/getpass.html)
- [pytest](https://pypi.org/project/pytest/)
- [regex](https://docs.python.org/3/library/re.html)


## Project Description
This is a password manager that can be used to store all your accounts and passwords in one place securely and view them ( only you!! ) whenever needed. You can add an account , update passwords , delete an account , view all the existing accounts.

This project was developed using VisualStudio Code and is built in Python.
The password are stored securely in a database after they are encrypted using a 'master key' . The user needs to have a 'master password' in order to view his/her accounts stored in the database , incase the user forgets the 'master password' he/she can update it by answering a secret phrase ( What is your favourite sport?) 
The master key , master password and secret phrase are hashed away in a .env file.

 While adding the accounts , user must go through a password strength check ( alphanumeric combinations , inclusion of special charecters etc ) , the accounts are added only if the corresponding password checks the criteria set , else the user is propted for a stronger password.

 The database was created using sqlite consisting of 4 columns : Id , Website name , User name , password

 The project is also accompanied by a test code , testing various functions that are defined in the main code

 ## Setting up databse
 
```python
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
``` 

##Encryption and decryption technique

```python
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
```

## Password strength checker

```python
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
```


## About CS50P
CS50P is a openware course from Havard University and taught by David J. Malan

Introduction to the intellectual enterprises of computer science (specifically python) and the art of programming. This course teaches students how to think algorithmically and solve problems efficiently.The course include basic Python functions , conditionals , unit tests , modules , regular expressions , introduction to object oriented programming etc

Thank you for all CS50P.

- Where I get CS50 course?
- https://cs50.harvard.edu/python/2022/
