# flask blueprint
from flask import Blueprint, request, jsonify,session
from db import *
import random
import pywhatkit as kit

import time

bp=Blueprint("user",__name__)




@bp.route("/Signup",methods=['POST'])
def signup():
    if request.method == 'POST':
        data =request.get_json()
        if user_exists(data.get("username")):
            return jsonify({"message": "User already exists"}), 409
        
        create_user_account(data)
        return jsonify({"message": "User account created successfully"}), 200
    
    return jsonify({"message": "Method not allowed"}), 405



@bp.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    phone_number = str(data.get("phonenumber", "")).strip()  # Ensure string

    if not phone_number:
        return jsonify({"message": "Phone number is required"}), 400

    # Auto-add +91 if not present
    if not phone_number.startswith("+"):
        phone_number = "+91" + phone_number

    otp = random.randint(1000, 9999)
    session["otp"] = otp
    session["phone"] = phone_number

    # Current time + 1 minute for scheduling
    now = time.localtime()
    hour = int(time.strftime("%H", now))
    minute = int(time.strftime("%M", now)) + 1

    try:
        kit.sendwhatmsg(
            phone_number,
            f"Your OTP is: {otp}",
            time_hour=hour,
            time_min=minute
        )
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Failed to send OTP: {str(e)}"}), 500


# Step 2: Verify OTP
@bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    if request.method != "POST":
        return jsonify({"message": "Method not allowed"}), 405
    data = request.get_json()
    user_otp = data.get("otp")

    if "otp" not in session:
        return jsonify({"message": "No OTP found. Please request one first."}), 400

    if int(user_otp) == session["otp"]:
        # Optionally check DB user existence here
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"message": "Invalid OTP"}), 401
