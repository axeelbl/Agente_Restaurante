export class AvatarController {
    constructor(baseFace, mouthOpenImg, avatarHalo, avatar, avatarStatus) {
        this.baseFace = baseFace;
        this.mouthOpenImg = mouthOpenImg;
        this.avatarHalo = avatarHalo;
        this.avatar = avatar;
        this.avatarStatus = avatarStatus;

        this.mouthOpen = false;
        this.talkingInterval = null;

        this.setStatus("online", "Online");
        this.startBlinking();
    }

    startBlinking() {
        setInterval(() => {
            if (this.talkingInterval) return;
            this.baseFace.src = "/agents/restaurante/pictures/eyes_closed_mouth_closed.png";
            setTimeout(() => {
                this.baseFace.src = "/agents/restaurante/pictures/eyes_open_mouth_closed.png";
            }, 200);
        }, 4000);
    }

    startTalking() {
        if (this.talkingInterval) return;

        this.avatarHalo.style.opacity = "1";
        this.avatar.style.transform = "scale(1.05)";
        this.setStatus("thinking", "Pensando...");

        this.talkingInterval = setInterval(() => {
            this.mouthOpen = !this.mouthOpen;
            this.mouthOpenImg.style.opacity = this.mouthOpen ? "1" : "0";
        }, 300);
    }

    stopTalking(state = "online") {
        clearInterval(this.talkingInterval);
        this.talkingInterval = null;
        this.mouthOpen = false;
        this.mouthOpenImg.style.opacity = "0";
        this.avatarHalo.style.opacity = "0";
        this.avatar.style.transform = "scale(1)";

        if (state === "error") {
            this.setStatus("error", "Sin conexion");
            return;
        }

        this.setStatus("online", "Online");
    }

    setStatus(state, label) {
        this.avatarStatus.dataset.state = state;
        this.avatarStatus.textContent = label;
    }
}
