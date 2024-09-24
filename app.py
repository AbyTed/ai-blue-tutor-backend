from flask import Flask, request, jsonify, send_file 
from flask_sqlalchemy import SQLAlchemy  
from werkzeug.security import generate_password_hash, check_password_hash  
from flask_cors import CORS 
from models import User, session
import requests  
from form import Form
import assemblyai as aai  
import os
from transcript import Transcript
from openai import OpenAI  
import tempfile
from dotenv import load_dotenv  
import io

load_dotenv()

client = OpenAI(api_key=os.getenv("API_KEY_OPENAI"))


app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "https://bluetutor.vercel.app",
                "http://localhost:5173/",
                "https://bluetutor.vercel.app/login/blueTutor",
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    },
)


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
def tutor_text():
    form = Form(request, os, tempfile)
    transcript = Transcript("no question")
    saved_files = form.save_files()
    transcript.text = ""
    text = form.get_text()
    student_question = form.get_student_question()

    if saved_files:
        try:

            aai.settings.api_key = os.getenv("API_KEY_ASSEMBLY_AI")
            transcriber = aai.Transcriber()

            transcript = transcriber.transcribe(saved_files["audio"])

        except Exception as e:
            print("audio couldn't be transcribed", e)
            return jsonify({"error": str(e)}), 500
    try:

        with open("prompt.txt", "r") as file:
            tutor_init = file.read()

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": tutor_init},
                {
                    "role": "user",
                    "content": f"{text} student question {student_question}; {transcript.text}",
                },
            ],
        )
        data = stream.choices[0].message.content
        return {"message": data}
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging output
        return jsonify({"error": str(e)}), 500


@app.route("/tutor/audio", methods=["POST"])
def tutor_audio():
    CHUNK_SIZE = 1024
    data = request.get_json()
    text = data['text']
    text = text.replace('*', '')
    print(f"Received text: {text}")  # Debugging output

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.getenv('ELEVEN_LABS_VOICE_ID')}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.getenv("API_KEY_ELEVEN_LABS"),
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    try:
        print(f"Sending request to URL: {url}")  # Debugging output
        response = requests.post(url, json=data, headers=headers, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check the content type to ensure it's audio
        if "audio/mpeg" not in response.headers.get("Content-Type", ""):
            raise ValueError("Response content is not audio/mpeg")

        # Use a BytesIO buffer to hold the audio content
        audio_content = io.BytesIO()

        # Write the audio content to the buffer in chunks
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                audio_content.write(chunk)

        # Reset buffer position to the beginning
        audio_content.seek(0)

        return send_file(
            audio_content,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="output.mp3",
        )
    except Exception as e:
        print(f"Failed to convert text to speech: {str(e)}")
        return jsonify({"error": "Failed to generate audio"}), 500


if __name__ == "__main__":
    app.run(debug=True)
