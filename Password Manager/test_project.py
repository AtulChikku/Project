import os
import sqlite3
import pytest
from project import add , view , update ,delete , encrypt_passwd , decrypt_passwd 


@pytest.fixture(scope="function")
def setup_database():
    os.environ["IS_TESTING"] = "True"
    conn = sqlite3.connect(":memory:") 
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        website TEXT NOT NULL)''')
    conn.commit()
    yield conn  
    del os.environ["IS_TESTING"]


def test_add(setup_database):
    conn = setup_database
    website = "example.com"
    user_name = "user123"
    passwd = "TestPassword123!"
    add(conn,website,user_name,passwd)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE website = 'example.com' AND username = 'user123'")
    result = cursor.fetchone()

    assert result is not None, "Account was not added."
    decrypted_password = decrypt_passwd(result[2])  
    assert decrypted_password == "TestPassword123!", "Password wasn't stored or decrypted correctly."
    conn.close()


def test_view(setup_database,capsys):
    website = "example.com"
    user_name = "user123"
    password = "TestPassword123!"
    encrypted_password = encrypt_passwd(password)
    conn = setup_database
    cursor = conn.cursor()
    cursor.execute("INSERT INTO accounts (website, username, password) VALUES (?, ?, ?)",
                   (website, user_name, encrypted_password))
    conn.commit()
    master_pwd = "root123"
    view(conn,master_pwd)

    captured = capsys.readouterr()
    assert f"Website : {website} , Username : {user_name} , Password : {password}" in captured.out, \
        "Account details were not displayed correctly."

    assert "----YOUR STORED ACCOUNTS----" in captured.out, "Heading not found in the output."
    conn.close()


def test_update(setup_database):
    website = "example.com"
    user_name = "user123"
    old_passwd = "TestPassword123!"
    encrypted_old_pwd = encrypt_passwd(old_passwd)
    new_passwd = "NewTestPassword123!"
    encrypted_new_passwd = encrypt_passwd(new_passwd)
    conn = setup_database
    cursor = conn.cursor()
    cursor.execute("INSERT INTO accounts (website, username, password) VALUES (?, ?, ?)",
                           (website, user_name, encrypted_old_pwd))
    conn.commit()

    update(conn,website,user_name,old_passwd,new_passwd)
    
    cursor.execute("SELECT password FROM accounts WHERE website='example.com' AND username='user123';")
    result = cursor.fetchone()
    assert result is not None, "Account was not found for update."
    assert result[0] != encrypted_old_pwd, "Password was not updated."
    conn.close()


def test_delete(setup_database):
    website = "example.com"
    user_name = "user123"
    passwd = "TestPassword123!"
    encrypted_pwd = encrypt_passwd(passwd)
    conn = setup_database
    cursor = conn.cursor()
    cursor.execute("INSERT INTO accounts (website, username, password) VALUES (?, ?, ?)",
                           (website, user_name, encrypted_pwd))
    conn.commit()

    consent = "yes"
    delete(conn,website,user_name,passwd,consent)
    cursor.execute("SELECT * FROM accounts WHERE website='example.com' AND username='user123';")
    result = cursor.fetchone()
    assert result is None, "Account was not deleted."
    conn.close()
