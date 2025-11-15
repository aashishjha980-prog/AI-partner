from flask import Flask, request, jsonify, send_from_directory
import os, string, requests
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

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please type something first!"})

    # Normalize message
    msg_clean = user_message.lower().translate(str.maketrans('', '', string.punctuation))

    # ---------- 1️⃣ Special handler for "about yourself" ----------
    creator_words = [
        "made", "create", "built", "code", "program", "designed", "develop", 
        "train", "implement", "author", "engineer", "supervise", "maintain", 
        "manage", "run", "control", "fund", "own", "owner", "developer", 
        "creator", "yourself", "about yourself"
    ]

    if any(word in msg_clean for word in creator_words):
        reply_points = [
            "AI Name: I am Daffodils AI, made by Aashish Jha",
            "Capabilities: I can answer questions in points and paragraphs",
            "Support: I can provide answers to almost any question and even support you",
            "Purpose: My purpose is to make your tasks easier and simpler",
            "Prompt: Ask me anything!"
        ]
        reply = "\n".join([f"{i+1}. {p}" for i, p in enumerate(reply_points)])
        return jsonify({"reply": reply})

    # ---------- 2️⃣ Decide response style ----------
    response_style = "Answer naturally with proper formatting."
    points_mode = False
    if "points" in msg_clean or "list" in msg_clean:
        points_mode = True
        response_style = "Answer in clean numbered points, with topics before colon, e.g.:\n1. Topic: Description\n2. Topic: Description\n..."

    elif "short" in msg_clean:
        response_style = "Answer concisely in 1-3 lines."
    elif "paragraph" in msg_clean:
        response_style = "Answer in 2-3 paragraphs."

    # ---------- 3️⃣ GPT request ----------
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are Daffodils AI, a friendly AI assistant."},
            {"role": "user", "content": f"{user_message}\nInstruction: {response_style}"}
        ]
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]

        # ---------- 4️⃣ Optional cleanup for points ----------
        if points_mode:
            lines = [line.strip("-• ") for line in reply.splitlines() if line.strip()]
            cleaned_lines = []
            for line in lines:
                # Remove ** markers from GPT
                line = line.replace("**", "").strip()

                # Remove double numbering (e.g., 1. 1. Topic: ...)
                numbered_match = line.lstrip().split(". ", 1)
                if len(numbered_match) == 2 and numbered_match[0].isdigit():
                    line = numbered_match[1].strip()

                cleaned_lines.append(line)

            # Reconstruct numbered points
            reply = ""
            for i, line in enumerate(cleaned_lines, 1):
                reply += f"{i}. {line}\n"

    except Exception as e:
        print("Error:", e)
        reply = "❌ Something went wrong. Check API key or internet."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

