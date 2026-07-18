import { AvatarController } from "./avatar.js";
import { ChatUI } from "./ui.js";
import { ChatController } from "./chat.js";

function bindQuickActions(chat, ui) {
    document.querySelectorAll("[data-prompt]").forEach(button => {
        button.addEventListener("click", () => {
            const prompt = button.dataset.prompt;
            if (!prompt) return;

            document.getElementById("chatExperience")?.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });

            chat.queueMessage(prompt);
            ui.userInput.focus();
        });
    });

    document.querySelectorAll("[data-click-target]").forEach(button => {
        button.addEventListener("click", () => {
            const targetId = button.dataset.clickTarget;
            if (!targetId) return;

            document.getElementById(targetId)?.click();
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const avatar = new AvatarController(
        document.getElementById("baseFace"),
        document.getElementById("mouthOpenImg"),
        document.getElementById("avatarHalo"),
        document.getElementById("avatar"),
        document.getElementById("avatarStatus")
    );

    const ui = new ChatUI(
        document.getElementById("chatContainer"),
        document.getElementById("userInput"),
        document.getElementById("sendBtn"),
        document.getElementById("clearBtn")
    );

    const chat = new ChatController(ui, avatar, "/chat");

    window.chatUI = ui;
    window.chatController = chat;

    bindQuickActions(chat, ui);

    setTimeout(() => {
        ui.addBotMessageTyping(
            "Hola. Soy Mesa Viva Bot.\n\n" +
            "Puedo ayudarte con la carta, el menú del día, recomendaciones, fotos del local y reservas.\n\n" +
            "Prueba con mensajes como:\n" +
            "- Enséñame la carta\n" +
            "- Qué me recomiendas si quiero algo vegetariano\n" +
            "- Quiero ver fotos de la terraza\n" +
            "- Quiero reservar para 4 mañana a las 21:00"
        );
    }, 300);
});
