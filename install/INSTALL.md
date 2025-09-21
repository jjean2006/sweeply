#### 1. Install MariaDB
- Use your system’s package manager or the official installer to install MariaDB.
- Ensure the MariaDB service is running before continuing.

#### 2. Create The Sweeply Database User  
- Open the MariaDB client as admin/root: `mariadb -u root -p`
- #### At the MariaDB prompt, run the following in order:
```
CREATE USER 'sweeply'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON mydb.* TO 'sweeply'@'localhost';
QUIT;
```

#### 3. Create a Python virtual environment
- Create the environment: `python -m venv .venv`
- Activate your virtual environment for your operating system.

#### 4. Install Python dependencies
- Install modules from the requirements file: `pip install -r requirements.txt`
  
#### 5. Clone the repository
- Clone the codebase: `git clone https://github.com/jjean2006/sweeply.git`
- Navigate into the project directory.
  
#### 6. Initialize the database
  - Run the setup script: `python ./install/setup_db.py`
  



#### You’re done. Sweeply and its database user should now be set up and ready to use.
