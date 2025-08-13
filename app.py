from flask import Flask, request, jsonify
from routing import bp as user_bp
from dotenv import load_dotenv
import os
load_dotenv()



app = Flask(__name__)
app.register_blueprint(user_bp)
app.secret_key = os.getenv("SECRET_KEY")
if __name__ == "__main__":
    app.run(debug=True)

