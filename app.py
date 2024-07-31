from flask import Flask, request, jsonify  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore
from flask_cors import CORS  # type: ignore
from models import User, session
import requests  # type: ignore

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
def test():
    return "working"


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data["username"]
    email = data["email"]
    password = generate_password_hash(data["password"], method="pbkdf2:sha256")

    new_user = User(username=username, email=email, password=password)
    session.add(new_user)
    session.commit()

    return jsonify({"message": "User signed up successfully"}), 201


@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data["username"]
    password = data["password"]

    user = session.query(User).filter(User.username == username)
    user = user[0]
    if user.username and check_password_hash(user.password, password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401


@app.route("/tutor/text", methods=["POST"])
def tutor_image():
    try:
        data = request.get_json()
        
        url = "https://ai-api-textgen.p.rapidapi.com/completions"

        
        with open('prompt.txt','r') as file:
            tutor_init = file.read()
        
        payload = {
            "init_character": tutor_init,
            "user_name": "Kile",
            "character_name": "tutor",
            "text": data["data"],
        }
        headers = {
            "x-rapidapi-key": "fa07435fdfmshb2efcaa08b470aap1d2830jsn5e56356904bc",
            "x-rapidapi-host": "ai-api-textgen.p.rapidapi.com",
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)

        data = response.json()

        return {"message": data}

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging output
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
