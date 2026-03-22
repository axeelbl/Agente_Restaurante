export class ChatUI {
    constructor(chatContainer, userInput, sendBtn, clearBtn) {
        this.chatContainer = chatContainer;
        this.userInput = userInput;
        this.sendBtn = sendBtn;
        this.clearBtn = clearBtn;
        this.typingIndicator = null;

        this.clearBtn.addEventListener("click", () => this.clearChat());
    }

    addUserMessage(text) {
        const message = this.createMessage("user");
        this.renderGenericMessage(message.body, this.decodeText(text));
        this.scrollToBottom();
        return message;
    }

    async addBotMessageTyping(text, speed = 10) {
        const normalizedText = this.decodeText(text);
        const message = this.createMessage("bot");
        const typeParagraph = document.createElement("p");
        typeParagraph.className = "message-paragraph";
        message.body.appendChild(typeParagraph);

        return new Promise(resolve => {
            let index = 0;

            const typeChar = () => {
                if (index < normalizedText.length) {
                    typeParagraph.textContent += normalizedText[index++];
                    this.scrollToBottom();
                    setTimeout(typeChar, speed);
                    return;
                }

                this.renderMessageBody(message.body, normalizedText);
                this.scrollToBottom();
                resolve(message);
            };

            typeChar();
        });
    }

    showTypingIndicator() {
        if (this.typingIndicator) return;

        const row = document.createElement("div");
        row.className = "message-row typing";

        const indicator = document.createElement("div");
        indicator.className = "typing-indicator";

        for (let index = 0; index < 3; index += 1) {
            const dot = document.createElement("span");
            dot.className = "typing-dot";
            indicator.appendChild(dot);
        }

        row.appendChild(indicator);
        this.chatContainer.appendChild(row);
        this.typingIndicator = row;
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        if (!this.typingIndicator) return;
        this.typingIndicator.remove();
        this.typingIndicator = null;
    }

    appendPhotoGallery(photos, onPhotoClick) {
        if (!Array.isArray(photos) || photos.length === 0) return;

        const row = document.createElement("div");
        row.className = "message-row bot";

        const gallery = document.createElement("div");
        gallery.className = "photo-gallery";

        photos.forEach((src, index) => {
            const image = document.createElement("img");
            image.src = src;
            image.className = "chat-photo";
            image.alt = `Foto ${index + 1} del restaurante`;
            image.addEventListener("click", () => onPhotoClick(index));
            gallery.appendChild(image);
        });

        row.appendChild(gallery);
        this.chatContainer.appendChild(row);
        this.scrollToBottom();
    }

    clearChat() {
        if (!confirm("Seguro que quieres borrar la conversacion?")) return;
        this.hideTypingIndicator();
        this.chatContainer.innerHTML = "";
        this.userInput.value = "";
        this.userInput.focus();
    }

    createMessage(role) {
        const row = document.createElement("div");
        row.className = `message-row ${role}`;

        const bubble = document.createElement("div");
        bubble.className = `message ${role}`;

        const meta = document.createElement("div");
        meta.className = "message-meta";

        const author = document.createElement("span");
        author.textContent = role === "user" ? "Tu mensaje" : "Mesa Viva";

        const time = document.createElement("span");
        time.textContent = this.getTimeLabel();

        meta.append(author, time);

        const body = document.createElement("div");
        body.className = "message-body";

        bubble.append(meta, body);
        row.appendChild(bubble);
        this.chatContainer.appendChild(row);

        return { row, bubble, body };
    }

    renderMessageBody(container, text) {
        const normalizedText = this.decodeText(text).trim();
        container.innerHTML = "";

        if (!normalizedText) return;

        if (this.renderMenuDayMessage(container, normalizedText)) return;
        if (this.renderReservationMessage(container, normalizedText)) return;
        if (this.renderPhotoSummaryMessage(container, normalizedText)) return;
        if (this.renderDishCollectionMessage(container, normalizedText)) return;
        if (this.renderDetailMessage(container, normalizedText)) return;

        this.renderGenericMessage(container, normalizedText);
    }

    renderMenuDayMessage(container, text) {
        const plain = this.normalizeForMatch(text);
        if (!plain.includes("menu del dia") || !plain.includes("primeros:") || !plain.includes("segundos:")) {
            return false;
        }

        const lines = this.getMeaningfulLines(text);
        const title = lines.shift();
        const sections = [];
        let currentSection = null;

        lines.forEach(line => {
            if (line.endsWith(":") && !line.startsWith("- ")) {
                if (currentSection) sections.push(currentSection);
                currentSection = { title: line.slice(0, -1), items: [] };
                return;
            }

            if (line.startsWith("- ") && currentSection) {
                currentSection.items.push(line.slice(2));
            }
        });

        if (currentSection) sections.push(currentSection);

        this.appendParagraph(container, title);

        const grid = document.createElement("div");
        grid.className = "message-section-grid";

        sections.forEach(section => {
            const card = document.createElement("div");
            card.className = "message-section-card";

            const heading = document.createElement("h4");
            heading.className = "message-section-title";
            heading.textContent = section.title;

            card.append(heading, this.buildSimpleList(section.items));
            grid.appendChild(card);
        });

        container.appendChild(grid);
        return true;
    }

    renderReservationMessage(container, text) {
        const lines = this.getMeaningfulLines(text);
        const firstLine = this.normalizeForMatch(lines[0] || "");

        if (!firstLine.startsWith("reserva ")) return false;

        this.appendParagraph(container, lines[0]);

        const detailLines = lines.slice(1).filter(line => line.includes(":"));
        const noteLines = lines.slice(1).filter(line => !line.includes(":"));

        if (detailLines.length) {
            const details = document.createElement("div");
            details.className = "message-detail-grid";

            detailLines.forEach(line => {
                const [label, ...rest] = line.split(":");
                details.appendChild(this.buildDetailCard(label.trim(), rest.join(":").trim()));
            });

            container.appendChild(details);
        }

        noteLines.forEach(line => this.appendParagraph(container, line));
        return true;
    }

    renderPhotoSummaryMessage(container, text) {
        const plain = this.normalizeForMatch(text);
        if (!plain.startsWith("aqui tienes algunas fotos")) return false;

        const lines = this.getMeaningfulLines(text);
        this.appendParagraph(container, lines[0]);

        const cards = document.createElement("div");
        cards.className = "message-list";

        lines.slice(1).forEach(line => {
            const item = document.createElement("div");
            item.className = "message-section-card";
            item.textContent = line.replace(/^- /, "");
            cards.appendChild(item);
        });

        container.appendChild(cards);
        return true;
    }

    renderDishCollectionMessage(container, text) {
        const lines = this.getMeaningfulLines(text);
        if (!lines.some(line => this.parseDishLine(line))) return false;

        const introLines = [];
        const standaloneItems = [];
        const sections = [];
        let currentSection = null;

        lines.forEach(line => {
            if (line.startsWith("- ") && this.parseDishLine(line)) {
                if (currentSection) {
                    currentSection.items.push(line);
                } else {
                    standaloneItems.push(line);
                }
                return;
            }

            if (line.endsWith(":") && !line.startsWith("- ")) {
                if (currentSection) sections.push(currentSection);

                const heading = line.slice(0, -1);
                const headingPlain = this.normalizeForMatch(heading);
                const isSectionHeading = ["entrantes", "principales", "bebidas", "postres"].includes(headingPlain);

                if (isSectionHeading) {
                    currentSection = { title: heading, items: [] };
                    return;
                }

                currentSection = null;
                introLines.push(heading);
                return;
            }

            introLines.push(line);
        });

        if (currentSection) sections.push(currentSection);

        introLines.forEach(line => this.appendParagraph(container, line));

        if (standaloneItems.length) {
            container.appendChild(this.buildDishList(standaloneItems));
        }

        if (sections.length) {
            const grid = document.createElement("div");
            grid.className = "message-section-grid";

            sections.forEach(section => {
                const card = document.createElement("div");
                card.className = "message-section-card";

                const heading = document.createElement("h4");
                heading.className = "message-section-title";
                heading.textContent = section.title;

                card.append(heading, this.buildDishList(section.items));
                grid.appendChild(card);
            });

            container.appendChild(grid);
        }

        return true;
    }

    renderDetailMessage(container, text) {
        const lines = this.getMeaningfulLines(text);
        const detailLines = lines.filter(line => line.includes(":"));

        if (detailLines.length < 2) {
            return false;
        }

        const introLines = lines.filter(line => !line.includes(":"));
        introLines.forEach(line => this.appendParagraph(container, line));

        const details = document.createElement("div");
        details.className = "message-detail-grid";

        detailLines.forEach(line => {
            const [label, ...rest] = line.split(":");
            details.appendChild(this.buildDetailCard(label.trim(), rest.join(":").trim()));
        });

        container.appendChild(details);
        return true;
    }

    renderGenericMessage(container, text) {
        const blocks = this.decodeText(text).trim().split(/\n{2,}/);

        blocks.forEach(block => {
            const lines = block.split("\n").map(line => line.trim()).filter(Boolean);
            if (!lines.length) return;

            const bulletLines = lines.filter(line => line.startsWith("- "));
            if (bulletLines.length === lines.length) {
                container.appendChild(this.buildSimpleList(bulletLines.map(line => line.slice(2))));
                return;
            }

            if (lines.length > 1 && lines[0].endsWith(":") && bulletLines.length === lines.length - 1) {
                this.appendParagraph(container, lines[0].slice(0, -1));
                container.appendChild(this.buildSimpleList(bulletLines.map(line => line.slice(2))));
                return;
            }

            this.appendParagraph(container, lines.join(" "));
        });
    }

    buildSimpleList(items) {
        const list = document.createElement("div");
        list.className = "message-list";

        items.forEach(itemText => {
            const item = document.createElement("div");
            item.className = "message-section-card";
            item.textContent = itemText;
            list.appendChild(item);
        });

        return list;
    }

    buildDishList(lines) {
        const list = document.createElement("div");
        list.className = "message-list";

        lines.forEach(line => {
            const item = this.parseDishLine(line);
            if (!item) return;

            const card = document.createElement("div");
            card.className = "message-item-card";

            const head = document.createElement("div");
            head.className = "message-item-head";

            const name = document.createElement("h4");
            name.className = "message-item-name";
            name.textContent = item.name;

            const price = document.createElement("span");
            price.className = "message-item-price";
            price.textContent = item.price;

            head.append(name, price);

            const description = document.createElement("p");
            description.className = "message-item-description";
            description.textContent = item.description;

            card.append(head, description);

            if (item.tags.length) {
                const tags = document.createElement("div");
                tags.className = "message-tags";

                item.tags.forEach(tagText => {
                    const tag = document.createElement("span");
                    tag.className = "message-tag";
                    tag.textContent = tagText;
                    tags.appendChild(tag);
                });

                card.appendChild(tags);
            }

            list.appendChild(card);
        });

        return list;
    }

    buildDetailCard(label, value) {
        const card = document.createElement("div");
        card.className = "message-detail";

        const heading = document.createElement("strong");
        heading.textContent = label;

        const content = document.createElement("span");
        content.textContent = value;

        card.append(heading, content);
        return card;
    }

    appendParagraph(container, text) {
        const paragraph = document.createElement("p");
        paragraph.className = "message-paragraph";
        paragraph.textContent = text;
        container.appendChild(paragraph);
    }

    parseDishLine(line) {
        const match = line.match(/^- (.+?) \(([^)]+)\):\s*(.+)$/);
        if (!match) return null;

        const [, name, price, remainder] = match;
        const segments = remainder.split(" | ").map(segment => segment.trim()).filter(Boolean);
        const description = segments.shift() || "";
        const tags = [];

        segments.forEach(segment => {
            if (this.normalizeForMatch(segment).startsWith("alergenos:")) {
                tags.push(segment);
                return;
            }

            segment.split(",").map(part => part.trim()).filter(Boolean).forEach(tag => tags.push(tag));
        });

        return { name, price, description, tags };
    }

    getMeaningfulLines(text) {
        return this.decodeText(text)
            .split("\n")
            .map(line => line.trim())
            .filter(Boolean);
    }

    decodeText(text) {
        const textarea = document.createElement("textarea");
        textarea.innerHTML = text;
        return textarea.value;
    }

    normalizeForMatch(text) {
        return text
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase();
    }

    getTimeLabel() {
        return new Intl.DateTimeFormat("es-ES", {
            hour: "2-digit",
            minute: "2-digit",
        }).format(new Date());
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
}
