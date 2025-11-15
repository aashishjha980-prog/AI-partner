const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// Send button click
sendBtn.addEventListener("click", sendMessage);

// Enter key press
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

    if (sender === "bot") {
        // Split into lines
        const lines = message.split(/\n/).filter(l => l.trim() !== "");

        let ol = null;
        let hasNumberedTopics = false;

        // Check if there are lines with colon (topics)
        lines.forEach(line => {
            const cleanLine = line.replace(/\*\*/g, "").trim();
            if (cleanLine.includes(":") && /^\d+\./.test(line)) {
                hasNumberedTopics = true;
            }
        });

        if (hasNumberedTopics) {
            ol = document.createElement("ol");
            ol.style.paddingLeft = "20px";
        }

        lines.forEach((line) => {
            const cleanLine = line.replace(/\*\*/g, "").trim();
            
            // Check if this is a numbered topic line (has number and colon)
            const numberedMatch = line.match(/^(\d+)\.\s*(.*)$/);
            const hasColon = cleanLine.includes(":");
            
            if (numberedMatch && hasColon && ol) {
                // This is a numbered topic line - add to ordered list
                const li = document.createElement("li");
                li.style.marginBottom = "10px";
                
                const content = numberedMatch[2]; // Content after the number

                // Split topic and description at the first colon
                const colonIndex = content.indexOf(":");
                if (colonIndex !== -1) {
                    const topic = content.substring(0, colonIndex).trim();
                    const description = content.substring(colonIndex + 1).trim();
                    
                    const spanTopic = document.createElement("span");
                    spanTopic.textContent = topic;
                    spanTopic.style.fontWeight = "bold";
                    spanTopic.style.color = "yellow";
                    
                    li.appendChild(spanTopic);
                    li.appendChild(document.createTextNode(": " + description));
                } else {
                    li.textContent = content;
                }
                ol.appendChild(li);
            } else {
                // This is regular text (headings, descriptions, etc) - no numbering
                const lineDiv = document.createElement("div");
                lineDiv.style.marginBottom = "10px";
                lineDiv.textContent = cleanLine;
                div.appendChild(lineDiv);
            }
        });

        // Add the ordered list to the div if it has items
        if (ol && ol.children.length > 0) {
            div.appendChild(ol);
        }
    } else {
        // User message
        div.textContent = message;
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}
