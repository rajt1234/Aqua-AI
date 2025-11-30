import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file.")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

app = Flask(__name__, static_folder="static")
CORS(app)  # For local dev if frontend served separately

def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Python Voice Assistant"
    }
    body = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful voice assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(OPENROUTER_URL, json=body, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"answer": "Please provide a prompt."})
    try:
        response = ask_openrouter(prompt)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

@app.route("/")
def serve_frontend():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
