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

    msg_clean = user_message.lower().translate(str.maketrans('', '', string.punctuation))

    # -------------------- 1️⃣ Special handler: About Yourself --------------------
    about_keywords = ["yourself", "about yourself"]
    if any(word in msg_clean for word in about_keywords):
        reply_points = [
            "I am Daffodils AI, made by Aashish Jha Production",
            "I can answer questions in points and paragraphs",
            "I can provide answers to almost any question and even support you",
            "My purpose is to make your tasks easier and simpler",
            "Ask me anything!"
        ]
        reply = "\n".join([f"{i+1}. {p}" for i, p in enumerate(reply_points)])
        return jsonify({"reply": reply})

    # -------------------- 2️⃣ Special handler: Who Made You --------------------
    who_keywords = [
        "who made", "who created", "who developed", "who mde", "who mafe", "who amde",
        "who mde you", "who mafe you", "who amde you"
    ]
    if any(word in msg_clean for word in who_keywords):
        reply = "I am made by Aashish Jha Production."
        return jsonify({"reply": reply})

    # -------------------- 3️⃣ Decide response style --------------------
    response_style = "Answer naturally with proper formatting."
    points_mode = False
    if any(word in msg_clean for word in ["points", "list", "recipe", "step"]):
        points_mode = True
        response_style = "Answer in clean numbered points where EACH point follows this format: 'Number. Topic: Description'. Combine the topic and description in one line. Example:\n1. Early Life: Born on June 28, 1971, in Pretoria, South Africa.\n2. Education: Attended Queen's University and University of Pennsylvania.\n3. Career: Co-founded Zip2 and PayPal. Always put the topic before colon and description after colon."

    elif "short" in msg_clean:
        response_style = "Answer concisely in 1-3 lines."
    elif "paragraph" in msg_clean:
        response_style = "Answer in 2-3 paragraphs."

    # -------------------- 4️⃣ Prepare GPT request --------------------
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

    # -------------------- 5️⃣ Call GPT API --------------------
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]

        # -------------------- 6️⃣ Cleanup points --------------------
        if points_mode:
            lines = [line.strip("-• ") for line in reply.splitlines() if line.strip()]
            
            # Group related lines together (topic + description)
            formatted_lines = []
            i = 0
            while i < len(lines):
                current_line = lines[i]
                
                # Remove any existing numbering from the line
                if "." in current_line[:5]:
                    parts = current_line.split(".", 1)
                    if len(parts) > 1:
                        current_line = parts[1].strip()
                
                # If this line looks like a topic (short, ends with colon or is a heading)
                if (len(current_line) < 50 and 
                    (current_line.endswith(':') or 
                     current_line.istitle() or 
                     any(word in current_line.lower() for word in ['life', 'education', 'career', 'foundation', 'venture', 'company', 'background', 'personal']))):
                    
                    # Try to combine with next line if it exists and looks like a description
                    if i + 1 < len(lines) and (lines[i + 1].endswith('.') or len(lines[i + 1]) > 30):
                        next_line = lines[i + 1]
                        # Remove numbering from next line too
                        if "." in next_line[:5]:
                            parts = next_line.split(".", 1)
                            if len(parts) > 1:
                                next_line = parts[1].strip()
                        
                        # Add colon if not present in current line
                        if not current_line.endswith(':'):
                            current_line += ':'
                        
                        combined_line = f"{current_line} {next_line}"
                        formatted_lines.append(combined_line)
                        i += 2  # Skip next line since we combined it
                    else:
                        formatted_lines.append(current_line)
                        i += 1
                else:
                    formatted_lines.append(current_line)
                    i += 1
            
            # Number the formatted lines properly
            numbered_lines = []
            for idx, line in enumerate(formatted_lines, 1):
                numbered_lines.append(f"{idx}. {line}")
            
            reply = "\n".join(numbered_lines)

    except Exception as e:
        print("Error:", e)
        reply = "❌ Something went wrong. Check API key or internet."

    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
