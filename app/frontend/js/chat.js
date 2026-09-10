export class ChatController {
    constructor(ui, avatar, apiUrl) {
        this.ui = ui;
        this.avatar = avatar;
        this.apiUrl = apiUrl;

        this.queue = [];
        this.processing = false;
        this.currentPhotos = [];
        this.currentIndex = 0;

        this.ui.sendBtn.addEventListener("click", () => this.queueMessage(this.ui.userInput.value));
        this.ui.userInput.addEventListener("keydown", event => {
            if (event.key !== "Enter") return;
            event.preventDefault();
            this.queueMessage(this.ui.userInput.value);
        });

        this.bindImageViewer();
    }

    bindImageViewer() {
        const viewer = document.getElementById("imageViewer");
        const closeBtn = document.getElementById("closeViewer");
        const leftBtn = document.getElementById("viewerLeft");
        const rightBtn = document.getElementById("viewerRight");

        if (closeBtn && viewer) {
            closeBtn.addEventListener("click", () => viewer.classList.add("hidden"));
        }

        if (viewer) {
            viewer.addEventListener("click", event => {
                if (event.target === viewer) {
                    viewer.classList.add("hidden");
                }
            });
        }

        if (leftBtn) {
            leftBtn.addEventListener("click", event => {
                event.stopPropagation();
                this.showPrev();
            });
        }

        if (rightBtn) {
            rightBtn.addEventListener("click", event => {
                event.stopPropagation();
                this.showNext();
            });
        }

        document.addEventListener("keydown", event => {
            if (!viewer || viewer.classList.contains("hidden")) return;

            if (event.key === "ArrowRight") this.showNext();
            if (event.key === "ArrowLeft") this.showPrev();
            if (event.key === "Escape") viewer.classList.add("hidden");
        });
    }

    openViewer(index) {
        const viewer = document.getElementById("imageViewer");
        const viewerImg = document.getElementById("viewerImg");
        if (!viewer || !viewerImg) return;

        this.currentIndex = index;
        viewerImg.src = this.currentPhotos[this.currentIndex];
        viewer.classList.remove("hidden");
    }

    showNext() {
        if (!this.currentPhotos.length) return;
        this.currentIndex = (this.currentIndex + 1) % this.currentPhotos.length;
        document.getElementById("viewerImg").src = this.currentPhotos[this.currentIndex];
    }

    showPrev() {
        if (!this.currentPhotos.length) return;
        this.currentIndex = (this.currentIndex - 1 + this.currentPhotos.length) % this.currentPhotos.length;
        document.getElementById("viewerImg").src = this.currentPhotos[this.currentIndex];
    }

    queueMessage(text) {
        const normalized = text.trim();
        if (!normalized) return;

        this.ui.addUserMessage(normalized);
        this.ui.userInput.value = "";
        this.queue.push(normalized);
        this.processQueue();
    }

    async processQueue() {
        if (this.processing || this.queue.length === 0) return;
        this.processing = true;

        const text = this.queue.shift();
        let avatarState = "online";

        this.avatar.startTalking();
        this.ui.userInput.disabled = true;
        this.ui.sendBtn.disabled = true;
        this.ui.clearBtn.disabled = true;
        this.ui.showTypingIndicator();

        try {
            const response = await fetch(this.apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_message: text }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error("El servidor ha rechazado el mensaje.");
            }
            this.ui.hideTypingIndicator();
            await this.ui.addBotMessageTyping(data.bot_message);

            if (data.photos && data.photos.length) {
                this.currentPhotos = data.photos;
                this.ui.appendPhotoGallery(data.photos, index => this.openViewer(index));
            }
        } catch (error) {
            avatarState = "error";
            this.ui.hideTypingIndicator();
            await this.ui.addBotMessageTyping("No he podido conectar con el servidor. Intentalo de nuevo en unos segundos.");
        } finally {
            this.avatar.stopTalking(avatarState);
            this.ui.userInput.disabled = false;
            this.ui.sendBtn.disabled = false;
            this.ui.clearBtn.disabled = false;
            this.ui.userInput.focus();
            this.processing = false;
            this.processQueue();
        }
    }
}
