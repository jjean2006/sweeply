#!/bin/python


# mariadb -u root -p
# CREATE USER 'monty'@'localhost' IDENTIFIED BY 'some_pass';
# GRANT ALL PRIVILEGES ON mydb.* TO 'monty'@'localhost';
# quit;

import mariadb
try:
    conn = mariadb.connect(
        user="sweeply",
        password="sweeply_db_pass",
        host="localhost",
        port=3306,
        database="sweeply_db"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

cur.execute("create table Student(User_ID varchar(10), Username varchar(20), Password_Salt Varchar(5), Password_hash Varchar(64), Name Varchar(20), Room_No int);")
cur.execute("create table Staff(User_ID varchar(10), Username varchar(20), Password_Salt varchar(5), Password_hash varchar(64), Name varchar(20), Rating decimal(2,1), Slot_1 int, Slot_2 int, Slot_3 int, Slot_4 int, Slot_5 int);")
cur.execute("create table Admin(User_ID varchar(10), Username varchar(20), Password_Salt Varchar(5), Password_hash Varchar(64), Name Varchar(20));")

conn.close()
