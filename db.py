from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

MongoDB_URI =os.getenv("MongoDB_URI")
client = MongoClient(MongoDB_URI)
db=client["Indian_Expensive_Tracker"]

# How to create user account db
def create_user_account(user):
    user ={
        "username": user.get("username"),
        "password": user.get("password"),
        "email_id": user.get("email_id"),
        "phonenumber": user.get("phonenumber")
    }

    db.users.insert_one(user)
# check if user exists
def user_exists(username):
    return db.users.find_one({"username": username}) is not None


#
def login_user(user):
    user = {
        "phonenumber": user.get("phonenumber"),
    }

    return db.users.find_one(user) is not None




def Indian_Expensive_Tracker():
    Indian_Expensive_Tracker={
        "Description": "A tracker for expensive items in India",
        "Amount": 0,
        "status": "active",
        "start_Date": None,
        "End_Date": None,
        "Expecting_Amount":0,
        "Current_Value":0,
        "Total_Amount":0

}