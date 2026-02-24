import { AvatarController } from "./avatar.js";
import { ChatUI } from "./ui.js";
import { ChatController } from "./chat.js";

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
 
    // HACERLO GLOBAL - I know this is not the most good way to do it, but I'm hurry now
    window.chatUI = ui;

    // Mensaje de bienvenida
    setTimeout(() => {
        ui.addBotMessageTyping(
            "¡Hola! 👋 Soy el PeluqueroBot, tu peluquero profesional.\n\n" +
            "Puedo ayudarte con cortes, precios, reservar cita, modificar o anular citas y enseñarte fotos de los cortes 📸✂️\n\n" +
            "👉 Para una cita, dime que quieres reservar y estos datos juntos:\n" +
            "• Tu nombre\n" +
            "• Servicio (Corte, Barba o Corte + Barba)\n" +
            "• Día (dd/mm/aaaa)\n" +
            "• Hora (24h)\n" +
            "• Teléfono o email\n\n" +
            "👉 Para ver fotos, solo escribe: ver fotos"
        );
    }, 300);
});
