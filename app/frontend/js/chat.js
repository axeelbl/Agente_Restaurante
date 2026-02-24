export class ChatController {
    constructor(ui, avatar, apiUrl) {
        this.ui = ui;
        this.avatar = avatar;
        this.apiUrl = apiUrl;

        this.queue = [];
        this.processing = false;

        // galería estado
        this.currentPhotos = [];
        this.currentIndex = 0;

        this.ui.sendBtn.addEventListener("click", () => this.queueMessage(this.ui.userInput.value));
        this.ui.userInput.addEventListener("keydown", e => {
            if (e.key === "Enter") {
                e.preventDefault();
                this.queueMessage(this.ui.userInput.value);
                this.ui.userInput.value = "";
            }
        });

        // ---------- VISOR ----------
        const viewer = document.getElementById("imageViewer");
        const closeBtn = document.getElementById("closeViewer");
        const leftBtn = document.getElementById("viewerLeft");
        const rightBtn = document.getElementById("viewerRight");

        if (closeBtn && viewer){
            closeBtn.addEventListener("click", () => viewer.classList.add("hidden"));
        }

        if (viewer){
            viewer.addEventListener("click", e => {
                if (e.target === viewer){
                    viewer.classList.add("hidden");
                }
            });
        }

        if (leftBtn){
            leftBtn.addEventListener("click", e => {
                e.stopPropagation();
                this.showPrev();
            });
        }

        if (rightBtn){
            rightBtn.addEventListener("click", e => {
                e.stopPropagation();
                this.showNext();
            });
        }

        // teclado
        document.addEventListener("keydown", e => {
            if (viewer.classList.contains("hidden")) return;

            if (e.key === "ArrowRight") this.showNext();
            if (e.key === "ArrowLeft") this.showPrev();
            if (e.key === "Escape") viewer.classList.add("hidden");
        });
    }

    // ---------- GALERÍA CONTROL ----------
    openViewer(index){
        const viewer = document.getElementById("imageViewer");
        const viewerImg = document.getElementById("viewerImg");

        this.currentIndex = index;
        viewerImg.src = this.currentPhotos[this.currentIndex];
        viewer.classList.remove("hidden");
    }

    showNext(){
        if (!this.currentPhotos.length) return;
        this.currentIndex = (this.currentIndex + 1) % this.currentPhotos.length;
        document.getElementById("viewerImg").src = this.currentPhotos[this.currentIndex];
    }

    showPrev(){
        if (!this.currentPhotos.length) return;
        this.currentIndex =
            (this.currentIndex - 1 + this.currentPhotos.length) % this.currentPhotos.length;
        document.getElementById("viewerImg").src = this.currentPhotos[this.currentIndex];
    }

    // ---------- CHAT ----------
    queueMessage(text) {
        if (!text.trim()) return;
        this.ui.addUserMessage(text.trim());
        this.queue.push(text.trim());
        this.processQueue();
    }

    async processQueue() {
        if (this.processing || this.queue.length === 0) return;
        this.processing = true;

        const text = this.queue.shift();

        this.avatar.startTalking();
        this.ui.userInput.disabled = true;
        this.ui.sendBtn.disabled = true;

        try {
            const res = await fetch(this.apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_message: text })
            });

            const data = await res.json();
            await this.ui.addBotMessageTyping(data.bot_message);

            // ---------- FOTOS ----------
            if (data.photos && data.photos.length) {

                this.currentPhotos = data.photos;

                const gallery = document.createElement("div");
                gallery.className = "photo-gallery";

                data.photos.forEach((src, index) => {
                    const img = document.createElement("img");
                    img.src = src;
                    img.className = "chat-photo";

                    img.addEventListener("click", () => {
                        this.openViewer(index);
                    });

                    gallery.appendChild(img);
                });

                this.ui.chatContainer.appendChild(gallery);
                this.ui.chatContainer.scrollTop = this.ui.chatContainer.scrollHeight;
            }

        } catch (err) {
            await this.ui.addBotMessageTyping("❌ Error conectando con el servidor.");
            this.avatar.avatarStatus.textContent = "🔴 Error";
        } finally {
            this.avatar.stopTalking();
            this.ui.userInput.disabled = false;
            this.ui.sendBtn.disabled = false;
            this.ui.userInput.focus();
            this.processing = false;
            this.processQueue();
        }
    }
}