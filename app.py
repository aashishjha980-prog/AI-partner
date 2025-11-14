from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

app = Flask(__name__)

# Serve frontend
@app.route("/")
def home():
    return send_from_directory('.', "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory('.', path)

# Chat API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type something first!"})

    # Decide response style
    response_style = "Answer naturally with proper formatting."
    if "points" in user_message.lower() or "list" in user_message.lower():
        response_style = "Answer in numbered points with line breaks."
    elif "short" in user_message.lower():
        response_style = "Answer concisely in 1-3 lines."
    elif "paragraph" in user_message.lower():
        response_style = "Answer in 2-3 paragraphs."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are Jarvis, a friendly AI assistant."},
            {"role": "user", "content": f"{user_message}\nInstruction: {response_style}"}
        ]
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error:", e)
        reply = "❌ Something went wrong. Check API key or internet."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
