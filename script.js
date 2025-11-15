const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// send button click
sendBtn.addEventListener("click", sendMessage);

// enter key press
userInput.addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMessage();
});

function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    addMessage(message, "user");
    userInput.value = "";

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => addMessage(data.reply, "bot"))
    .catch(err => addMessage("❌ Error connecting to server.", "bot"));
}

function addMessage(message, sender = "bot") {
    const div = document.createElement("div");
    div.classList.add("message", sender);

    // points formatting - only for bot messages that look like numbered lists
    if (sender === "bot" && message.match(/^\d+\./m)) {
        const lines = message.split(/\n/).filter(l => l.trim() !== "");
        const ol = document.createElement("ol");
        ol.style.paddingLeft = "20px";

        lines.forEach((line) => {
            const li = document.createElement("li");
            li.style.marginBottom = "10px";

            // remove ** from GPT and trim
            line = line.replace(/\*\*/g, "").trim();

            // Remove the existing number prefix (like "1. ", "2. ") since <ol> will auto-number
            const numberedMatch = line.match(/^\d+\.\s*(.*)$/);
            if (numberedMatch) {
                line = numberedMatch[1]; // Keep only the content after the number
            }

            // split topic and description with yellow highlighting
            const colonIndex = line.indexOf(":");
            if (colonIndex !== -1) {
                const topic = line.substring(0, colonIndex);
                const description = line.substring(colonIndex + 1);
                
                const spanTopic = document.createElement("span");
                spanTopic.textContent = topic.trim();
                spanTopic.style.fontWeight = "bold";
                spanTopic.style.color = "yellow";
                
                li.appendChild(spanTopic);
                li.appendChild(document.createTextNode(": " + description.trim()));
            } else {
                // No colon found, just add the text
                li.textContent = line;
            }

            ol.appendChild(li);
        });

        div.appendChild(ol);
    } else if (sender === "bot" && message.includes(":")) {
        // For non-numbered messages with colons, still apply yellow styling
        const lines = message.split(/\n/).filter(l => l.trim() !== "");
        
        if (lines.length > 1) {
            // Multiple lines with colons
            lines.forEach(line => {
                const lineDiv = document.createElement("div");
                lineDiv.style.marginBottom = "10px";
                
                const colonIndex = line.indexOf(":");
                if (colonIndex !== -1) {
                    const topic = line.substring(0, colonIndex);
                    const description = line.substring(colonIndex + 1);
                    
                    const spanTopic = document.createElement("span");
                    spanTopic.textContent = topic.trim();
                    spanTopic.style.fontWeight = "bold";
                    spanTopic.style.color = "yellow";
                    
                    lineDiv.appendChild(spanTopic);
                    lineDiv.appendChild(document.createTextNode(": " + description.trim()));
                } else {
                    lineDiv.textContent = line;
                }
                
                div.appendChild(lineDiv);
            });
        } else {
            // Single line with colon
            const colonIndex = message.indexOf(":");
            if (colonIndex !== -1) {
                const topic = message.substring(0, colonIndex);
                const description = message.substring(colonIndex + 1);
                
                const spanTopic = document.createElement("span");
                spanTopic.textContent = topic.trim();
                spanTopic.style.fontWeight = "bold";
                spanTopic.style.color = "yellow";
                
                div.appendChild(spanTopic);
                div.appendChild(document.createTextNode(": " + description.trim()));
            } else {
                div.textContent = message;
            }
        }
    } else {
        // normal text for bot or user
        div.textContent = message;
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}
