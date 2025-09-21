import os
import mariadb
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv

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

# --- THE API ENDPOINT ---
# This is the single endpoint our student website will call.
@app.route('/request-cleaning', methods=['POST'])
def create_cleaning_request():
    """Receives a request, saves it to MariaDB, and pings Supabase."""
    
    data = request.get_json()
    room_number = data.get('room_number')
    cleaning_type = data.get('type') # Details are optional

    if not room_number:
        return jsonify({"status": "error", "message": "Room number is required"}), 400
    if not cleaning_type:
        return jsonify({"status": "error", "message": "Cleaning type is required"}), 400
    details = cleaning_type


    try:
        # --- STEP 1: Save to MariaDB (Our Main Database) ---
        print(f"Connecting to MariaDB to save request for room {room_number}...")
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()
        
        # Make sure your table and column names match here
        cursor.execute(
            "INSERT INTO cleaning_service_requests (room_number, details) VALUES (?, ?)", 
            (room_number, details)
        )
        conn.commit()
        conn.close()
        print("Successfully saved to MariaDB.")

        # --- STEP 2: Ping Supabase (Our Real-time Messenger) ---
        print(f"Pinging Supabase for room {room_number}...")
        response = supabase.table('cleaning_requests').insert({
            "room_number": room_number,
            "details": details
        }).execute()
        print("Successfully pinged Supabase.")

        return jsonify({"status": "success", "message": "Request created and staff notified"}), 201

    except Exception as e:
        print(f"!!! AN ERROR OCCURRED: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- RUN THE SERVER ---
if __name__ == '__main__':
    # We run on port 5000. The website will run on a different one.
    app.run(port=5000, debug=True)
