export class ChatUI {
    constructor(chatContainer, userInput, sendBtn, clearBtn) {
        this.chatContainer = chatContainer;
        this.userInput = userInput;
        this.sendBtn = sendBtn;
        this.clearBtn = clearBtn;

        this.clearBtn.addEventListener("click", () => this.clearChat());
    }

    addUserMessage(text) {
        const div = document.createElement("div");
        div.classList.add("message", "user");
        div.textContent = text;
        this.chatContainer.appendChild(div);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    async addBotMessageTyping(text, speed = 10) {
        return new Promise(resolve => {
            const div = document.createElement("div");
            div.classList.add("message", "bot");
            this.chatContainer.appendChild(div);

            let i = 0;
            const typeChar = () => {
                if (i < text.length) {
                    div.textContent += text[i++];
                    this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
                    setTimeout(typeChar, speed);
                } else resolve();
            };
            typeChar();
        });
    }

    clearChat() {
        if (!confirm("¿Seguro que quieres borrar la conversación?")) return;
        this.chatContainer.innerHTML = "";
        this.userInput.value = "";
    }
}
