import os
import mariadb
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
# --- NEW IMPORT: For securely handling passwords ---
from werkzeug.security import generate_password_hash, check_password_hash

# --- INITIALIZATION ---
load_dotenv() # Load variables from our .env file

app = Flask(__name__)
# CRITICAL: This allows our website (running on a different port) to talk to our server.
CORS(app)

# --- DATABASE CONNECTIONS ---
# Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# MariaDB Connection Details (we connect inside the function)
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE"),
}

# --- THE API ENDPOINT (EXISTING CODE - UNCHANGED) ---
# This is the single endpoint our student website will call.
@app.route('/request-cleaning', methods=['POST'])
def create_cleaning_request():
    """Receives a request, saves it to MariaDB, and pings Supabase."""
    
    data = request.get_json()
    room_number = data.get('room_number')
    cleaning_type = data.get('type')
    slot = data.get('slot')

    # Basic input validation
    if not room_number:
        return jsonify({"status": "error", "message": "Room number is required"}), 400
    if not cleaning_type:
        return jsonify({"status": "error", "message": "Cleaning type is required"}), 400
    if not slot:
        return jsonify({"status": "error", "message": "Slot is required"}), 400

    try:
        # --- STEP 1: Save to MariaDB (Our Main Database) ---
        print(f"Connecting to MariaDB to save request for room {room_number}...")
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO cleaning_service_requests (room_number, details) VALUES (?, ?)", 
            (room_number, cleaning_type)
        )
        conn.commit()
        conn.close()
        print("Successfully saved to MariaDB.")

        # --- STEP 2: Ping Supabase (Our Real-time Messenger) ---
        print(f"Pinging Supabase for room {room_number}...")
        response = supabase.table('cleaning_requests').insert({
            "room_number": room_number,
            "details": cleaning_type
        }).execute()
        print("Successfully pinged Supabase.")

        return jsonify({"status": "success", "message": "Request created and staff notified"}), 201

    except Exception as e:
        print(f"!!! AN ERROR OCCURRED: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# =================================================================
# --- NEW AUTHENTICATION ENDPOINTS ---
# =================================================================

##
# Endpoint for user registration
##
@app.route('/register', methods=['POST'])
def register_user():
    """Registers a new user."""
    data = request.get_json(silent=True) or request.form.to_dict()
    username = data.get('username')
    password = data.get('password')
    table = data.get('user_type').capitalize()
    print(data)


    # --- 1. Validate Input ---
    if not username or not password or not table:
        return jsonify({"status": "error", "message": "Username, password, and type are required"}), 400
    
    # --- 2. Hash the Password (NEVER STORE PLAIN TEXT) ---
    password_hash = generate_password_hash(password)

    try:
        # --- 3. Connect and Insert into Database ---
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()

        cmd = f"SELECT Username FROM {table} WHERE username = '{username}'"
        # Check if username already exists
        cursor.execute(cmd)
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": "error", "message": "Username already exists"}), 409 # 409 Conflict


        print(username)
        print(password_hash)
        # Insert the new user
        cmd = f"INSERT INTO {table} (Username, Password_hash) VALUES ('{username}', '{password_hash}')"
        cursor.execute(cmd)
        conn.commit()
        conn.close()

        print(f"User '{username}' registered successfully.")
        return jsonify({"status": "success", "message": "User registered successfully"}), 201

    except mariadb.Error as e:
        print(f"!!! DATABASE ERROR: {e}")
        return jsonify({"status": "error", "message": f"Database error: {e}"}), 500
    except Exception as e:
        print(f"!!! AN ERROR OCCURRED: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

##
# Endpoint for user login
##
@app.route('/login', methods=['POST'])
def login_user():
    """Authenticates a user."""
    data = request.get_json(silent=True) or request.form.to_dict()
    username = data.get('username')
    password = data.get('password')
    table = data.get('user_type').capitalize()


    # --- 1. Validate Input ---
    if not username or not password or not table:
        return jsonify({"status": "error", "message": "Username,password and table are required"}), 400


    try:
        # --- 2. Fetch User from Database ---
        conn = mariadb.connect(**db_config)
        # We use a dictionary cursor to get column names
        cursor = conn.cursor(dictionary=True)

        cmd = f"SELECT * FROM {table} WHERE Username = '{username}'"
        cursor.execute(cmd)
        user = cursor.fetchone()
        print(user)
        conn.close()

        print("Checking pw")
        # --- 3. Verify User and Password Hash ---
        if user and check_password_hash(user[f'Password_hash'], password):
            # Password is correct!
            print(f"User '{username}' logged in successfully.")
            # Pro-tip: In a real app, you would generate a JWT token here and return it.
            return jsonify({
                "status": "success", 
                "message": "Login successful",
                "user": {
                    "username": user['Username'],
                }
            }), 200
        else:
            # User not found or password incorrect
            print(f"Failed login attempt for username '{username}'.")
            return jsonify({"status": "error", "message": "Invalid username or password"}), 401 # 401 Unauthorized

    except mariadb.Error as e:
        print(f"!!! DATABASE ERROR: {e}")
        return jsonify({"status": "error", "message": f"Database error: {e}"}), 500
    except Exception as e:
        print(f"!!! AN ERROR OCCURRED: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# --- RUN THE SERVER ---
if __name__ == '__main__':
    # We run on port 5000. The website will run on a different one.
    app.run(port=8000, debug=True)