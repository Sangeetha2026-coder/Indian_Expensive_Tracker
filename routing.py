# flask blueprint
from flask import Blueprint, request, jsonify, session
from db import user_exists, create_user_account, db
import random
from twilio.rest import Client
from datetime import datetime
import os

bp = Blueprint("user", __name__)

# Load Twilio credentials from environment variables
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")  # e.g., 'whatsapp:+14155238886'

# Initialize Twilio client
client = Client(TWILIO_SID, TWILIO_AUTH)


# ====================== SIGNUP ======================
@bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data.get("username"):
        return jsonify({"message": "Username is required"}), 400

    if user_exists(data.get("username")):
        return jsonify({"message": "User already exists"}), 409

    create_user_account(data)
    return jsonify({"message": "User account created successfully"}), 200


# ====================== SEND OTP ======================
@bp.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    phone_number = str(data.get("phonenumber", "")).strip()

    if not phone_number:
        return jsonify({"message": "Phone number is required"}), 400

    if not phone_number.startswith("+"):
        phone_number = "+91" + phone_number  # Default India country code

    otp = random.randint(1000, 9999)
    session["otp"] = otp
    session["phone"] = phone_number

    try:
        client.messages.create(
            from_=TWILIO_WHATSAPP,
            body=f"Your OTP is: {otp}",
            to=f"whatsapp:{phone_number}"
        )
        return jsonify({"message": "OTP sent successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to send OTP: {str(e)}"}), 500


# ====================== VERIFY OTP ======================
@bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    user_otp = data.get("otp")

    if "otp" not in session:
        return jsonify({"message": "No OTP found. Please request one first."}), 400

    try:
        if int(user_otp) == session["otp"]:
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"message": "Invalid OTP"}), 401
    except ValueError:
        return jsonify({"message": "Invalid OTP format"}), 400


# ====================== EXPENSE TRACKER ======================
@bp.route("/expensive_tracker", methods=["POST"])
def expensive_tracker():
    data = request.get_json()

    # Required fields
    required_fields = [
        "Description", "Amount", "status", "start_Date",
        "Date_Added", "Expecting_Amount", "Current_Value"
    ]

    # Check for missing fields
    for field in required_fields:
        if not data.get(field):
            return jsonify({"message": f"Missing required field: {field}"}), 400

    try:
        start_date = datetime.strptime(data.get("start_Date"), "%Y-%m-%d").strftime("%Y-%m-%d")
        date_added = datetime.strptime(data.get("Date_Added"), "%Y-%m-%d").strftime("%Y-%m-%d")


        tracker = {
            "username": session.get("username", "default_user"),
            "phonenumber": session.get("phone", "default_phone"),
            "Description": data["Description"],
            "Amount": int(data["Amount"]),
            "status": data["status"],
            "start_Date": start_date,
            "End_Date": date_added,
            "Expecting_Amount": int(data["Expecting_Amount"]),
            "Current_Value": int(data["Current_Value"]),
            "Total_Amount": int(data["Amount"]) + int(data["Expecting_Amount"])
        }

  
        result = db.expensive_trackers.insert_one(tracker)

        return jsonify({
            "message": "Tracker created successfully",
            "id": str(result.inserted_id)
        }), 201

    except ValueError:
        return jsonify({"message": "Invalid numeric or date format"}), 400
    except Exception as e:
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500
