document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chatBox");
    const input = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");

 function addMessage(message, sender = "bot") {
    const div = document.createElement("div");
    div.classList.add("message", sender);

    if (sender === "bot" && message.includes(":")) {
        const lines = message.split(/\d+\.\s/).filter(l => l.trim() !== "");
        const ol = document.createElement("ol");
        ol.style.paddingLeft = "20px";

        lines.forEach(line => {
            const li = document.createElement("li");
            li.style.marginBottom = "10px"; // spacing between points

            const [topic, ...desc] = line.split(":");

            // remove ** from topic
            let cleanTopic = topic.trim().replace(/\*\*/g, "");

            const spanTopic = document.createElement("span");
            spanTopic.textContent = cleanTopic;
            spanTopic.style.fontWeight = "bold";
            spanTopic.style.color = "yellow"; // yellow text color

            li.appendChild(spanTopic);
            li.appendChild(document.createTextNode(": " + desc.join(":").trim()));
            ol.appendChild(li);
        });

        div.appendChild(ol);
    } else {
        div.textContent = message;
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}



    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        addMessage(message, "user");
        input.value = "";

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message})
            });

            const data = await res.json();
            addMessage(data.reply, "bot");
        } catch (err) {
            console.error(err);
            addMessage("❌ Error connecting to server.", "bot");
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
});
