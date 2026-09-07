document.addEventListener("DOMContentLoaded", () => {
    const reserveBtn = document.getElementById("reserveBtn");
    const bookingModal = document.getElementById("bookingModal");
    const closeBookingBtn = document.getElementById("closeModal");
    const closeBookingBtnSecondary = document.getElementById("closeModalSecondary");
    const bookingForm = document.getElementById("bookingForm");
    const dateInput = bookingForm.querySelector("input[name='date']");
    const partySizeInput = bookingForm.querySelector("input[name='party_size']");
    const timeSelect = document.getElementById("timeSelect");

    const manageModal = document.getElementById("manageBookingModal");
    const closeManageBtn = document.getElementById("closeManageModal");
    const closeManageBtnSecondary = document.getElementById("closeManageModalSecondary");
    const manageForm = document.getElementById("manageBookingForm");
    const manageDateInput = manageForm.querySelector("input[name='new_date']");
    const managePartySizeInput = manageForm.querySelector("input[name='new_party_size']");
    const manageTimeSelect = document.getElementById("manageTimeSelect");
    const modifyBtn = document.getElementById("modifyBtn");
    const cancelBtn = document.getElementById("cancelBtn");
    const manageBtn = document.getElementById("manageBtn");

    async function loadAvailableHours(date, selectElement, partySize = 2, bookingUuid = "") {
        if (!date) {
            selectElement.innerHTML = "<option>Selecciona una hora</option>";
            selectElement.value = "";
            return;
        }

        selectElement.innerHTML = "<option>Cargando...</option>";
        selectElement.value = "";

        const params = new URLSearchParams({
            date,
            party_size: String(partySize || 2),
            _: String(Date.now()),
        });

        if (bookingUuid) {
            params.set("booking_uuid", bookingUuid);
        }

        try {
            const res = await fetch(`/agents/restaurante/booking/availability?${params.toString()}`, { cache: "no-store" });
            const hours = await res.json();

            selectElement.innerHTML = "";
            if (!hours.length) {
                selectElement.innerHTML = "<option>No hay mesas disponibles</option>";
                return;
            }

            const placeholder = document.createElement("option");
            placeholder.value = "";
            placeholder.textContent = "Selecciona una hora";
            placeholder.disabled = true;
            placeholder.selected = true;
            selectElement.appendChild(placeholder);

            hours.forEach(hour => {
                const option = document.createElement("option");
                option.value = hour;
                option.textContent = hour;
                selectElement.appendChild(option);
            });
        } catch {
            selectElement.innerHTML = "<option>Error cargando horas</option>";
        }
    }

    function openModal(modal) {
        modal.classList.remove("hidden");
    }

    function closeModal(modal) {
        modal.classList.add("hidden");
    }

    [bookingModal, manageModal].forEach(modal => {
        if (!modal) return;
        modal.addEventListener("click", event => {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });

    document.addEventListener("keydown", event => {
        if (event.key !== "Escape") return;
        if (bookingModal && !bookingModal.classList.contains("hidden")) closeModal(bookingModal);
        if (manageModal && !manageModal.classList.contains("hidden")) closeModal(manageModal);
    });

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function sendBotMessageSafe(message) {
        if (!window.chatUI || !window.chatUI.addBotMessageTyping) return;
        const safeMessage = message.split("\n").map(line => escapeHtml(line)).join("\n");
        window.chatUI.addBotMessageTyping(safeMessage);
    }

    async function readErrorMessage(res, fallbackMessage) {
        try {
            const data = await res.json();
            return data.detail || data.message || fallbackMessage;
        } catch {
            return fallbackMessage;
        }
    }

    if (reserveBtn && bookingModal && bookingForm && dateInput && timeSelect) {
        reserveBtn.addEventListener("click", event => {
            event.preventDefault();
            openModal(bookingModal);
            timeSelect.innerHTML = "<option>Selecciona una hora</option>";
            timeSelect.value = "";
            if (dateInput.value) {
                loadAvailableHours(dateInput.value, timeSelect, partySizeInput.value || 2);
            }
        });

        closeBookingBtn.addEventListener("click", () => closeModal(bookingModal));
        closeBookingBtnSecondary?.addEventListener("click", () => closeModal(bookingModal));
        dateInput.addEventListener("change", () => loadAvailableHours(dateInput.value, timeSelect, partySizeInput.value || 2));
        partySizeInput.addEventListener("change", () => {
            if (dateInput.value) loadAvailableHours(dateInput.value, timeSelect, partySizeInput.value || 2);
        });

        dateInput.min = new Date().toISOString().split("T")[0];

        bookingForm.addEventListener("submit", async event => {
            event.preventDefault();
            const data = Object.fromEntries(new FormData(bookingForm));

            try {
                const res = await fetch("/agents/restaurante/booking/reserve", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data),
                });

                if (!res.ok) {
                    throw new Error(await readErrorMessage(res, "No se pudo crear la reserva."));
                }

                const payload = await res.json();
                alert("Reserva creada correctamente");

                const notesLine = data.notes ? `\nObservaciones: ${escapeHtml(data.notes)}` : "";
                const message =
                    `Reserva confirmada\n\n` +
                    `Cliente: ${escapeHtml(data.name)}\n` +
                    `Comensales: ${escapeHtml(data.party_size)}\n` +
                    `Fecha: ${escapeHtml(data.date)}\n` +
                    `Hora: ${escapeHtml(data.time)}${notesLine}\n` +
                    `Confirmación enviada a: ${escapeHtml(data.contact)}\n` +
                    `ID de reserva: ${escapeHtml(payload.booking_uuid)}`;

                sendBotMessageSafe(message);

                closeModal(bookingModal);
                bookingForm.reset();
                timeSelect.innerHTML = "<option>Selecciona una hora</option>";
                timeSelect.value = "";
            } catch (error) {
                alert(error.message || "No se pudo crear la reserva");
            }
        });
    }

    if (manageModal && manageForm && manageBtn && manageDateInput && manageTimeSelect) {
        manageBtn.addEventListener("click", event => {
            event.preventDefault();
            openModal(manageModal);
            manageForm.reset();
            manageTimeSelect.innerHTML = "<option value=''>Selecciona una hora</option>";
        });

        closeManageBtn.addEventListener("click", () => closeModal(manageModal));
        closeManageBtnSecondary?.addEventListener("click", () => closeModal(manageModal));

        const refreshManageAvailability = () => {
            if (!manageDateInput.value) return;
            loadAvailableHours(
                manageDateInput.value,
                manageTimeSelect,
                managePartySizeInput.value || 2,
                manageForm.booking_uuid.value
            );
        };

        manageDateInput.addEventListener("change", refreshManageAvailability);
        managePartySizeInput.addEventListener("change", refreshManageAvailability);
        manageDateInput.min = new Date().toISOString().split("T")[0];

        modifyBtn.addEventListener("click", async event => {
            event.preventDefault();

            const data = {
                booking_uuid: manageForm.booking_uuid.value,
                contact: manageForm.contact.value,
                new_date: manageForm.new_date.value,
                new_time: manageForm.new_time.value,
                new_party_size: manageForm.new_party_size.value,
                new_notes: manageForm.new_notes.value,
            };

            const hasChanges = Boolean(
                data.new_date || data.new_time || data.new_party_size || data.new_notes
            );

            if (!data.booking_uuid || !data.contact) {
                alert("Indica el ID y el contacto de la reserva");
                return;
            }

            if (!hasChanges) {
                alert("Indica al menos un cambio para modificar la reserva");
                return;
            }

            try {
                const res = await fetch("/agents/restaurante/booking/modify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data),
                });

                if (res.status === 404) {
                    throw new Error("No se ha encontrado la reserva");
                }

                if (!res.ok) {
                    throw new Error(await readErrorMessage(res, "No se pudo modificar la reserva."));
                }

                alert("Reserva modificada correctamente");

                const detailLines = [
                    "Reserva modificada",
                    "",
                    `ID: ${escapeHtml(data.booking_uuid)}`,
                ];

                if (data.new_date) detailLines.push(`Nueva fecha: ${escapeHtml(data.new_date)}`);
                if (data.new_time) detailLines.push(`Nueva hora: ${escapeHtml(data.new_time)}`);
                if (data.new_party_size) detailLines.push(`Comensales: ${escapeHtml(data.new_party_size)}`);
                if (data.new_notes) detailLines.push(`Observaciones: ${escapeHtml(data.new_notes)}`);

                sendBotMessageSafe(detailLines.join("\n"));
                closeModal(manageModal);
                manageForm.reset();
            } catch (error) {
                alert(error.message || "No se pudo modificar la reserva");
            }
        });

        cancelBtn.addEventListener("click", async () => {
            const booking_uuid = manageForm.booking_uuid.value;
            const contact = manageForm.contact.value;

            if (!contact) {
                alert("Indica el contacto de la reserva para cancelarla");
                return;
            }

            if (!booking_uuid) {
                alert("Indica el ID de reserva para cancelarla");
                return;
            }

            if (!confirm("¿Seguro que quieres cancelar la reserva?")) return;

            try {
                const res = await fetch("/agents/restaurante/booking/cancel", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ booking_uuid, contact }),
                });

                if (res.status === 404) {
                    throw new Error("No se ha encontrado la reserva");
                }

                if (!res.ok) {
                    throw new Error(await readErrorMessage(res, "No se pudo cancelar la reserva."));
                }

                alert("Reserva cancelada correctamente");

                const message =
                    `Reserva cancelada\n\n` +
                    `ID: ${escapeHtml(booking_uuid)}\n` +
                    `La reserva ha sido cancelada correctamente.`;

                sendBotMessageSafe(message);
                closeModal(manageModal);
                manageForm.reset();
            } catch (error) {
                alert(error.message || "No se pudo cancelar la reserva");
            }
        });
    }
});
