async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "No fue posible ejecutar la simulacion.");
  }
  return data;
}

function setError(elementId, message = "") {
  document.getElementById(elementId).textContent = message;
}

let lamportRounds = [];

function updateProcessCards(processes) {
  processes.forEach((process) => {
    const card = document.querySelector(`[data-process-id="${process.id}"]`);
    const ticketLabel = card.querySelector("span");

    if (process.requesting) {
      card.classList.remove("is-pending");
      card.classList.add("is-selected");
      card.disabled = true;
      ticketLabel.textContent = `Ticket ${process.ticket}`;
    }
  });
}

function pendingProcessIds() {
  return [...document.querySelectorAll(".process-option.is-pending")].map((card) =>
    Number(card.dataset.processId)
  );
}

function updateLamportButtons() {
  const hasPendingProcesses = pendingProcessIds().length > 0;
  document.getElementById("assign-tickets").disabled = !hasPendingProcesses;
  document.getElementById("run-lamport").disabled = hasPendingProcesses || lamportRounds.length === 0;
}

function renderRoundHistory(rounds) {
  document.getElementById("round-history").innerHTML = rounds
    .map(
      (round) => `
        <div class="round-item">
          Ronda ${round.number}: ${round.processes.map((id) => `P${id}`).join(" y ")}
          reciben ticket ${round.ticket}
        </div>`
    )
    .join("");
}

async function assignTicketsToRound() {
  setError("lamport-error");
  const selectedIds = pendingProcessIds();
  if (selectedIds.length === 0) {
    throw new Error("Selecciona al menos un proceso.");
  }

  const newRounds = [...lamportRounds, selectedIds];
  const data = await postJson("/api/lamport/simulate", { request_rounds: newRounds });

  lamportRounds = newRounds;
  updateProcessCards(data.processes);
  renderRoundHistory(data.rounds);
  document.getElementById("lamport-concept").textContent = data.concept;
  document.getElementById("lamport-results").hidden = true;
  updateLamportButtons();
}

async function runLamport() {
  setError("lamport-error");
  if (lamportRounds.length === 0) {
    throw new Error("Asigna primero al menos un ticket.");
  }

  const data = await postJson("/api/lamport/simulate", { request_rounds: lamportRounds });

  document.getElementById("lamport-concept").textContent = data.concept;
  const orderedProcesses = [...data.processes].sort(
    (first, second) => (first.queue_position ?? 99) - (second.queue_position ?? 99)
  );

  document.getElementById("lamport-table").innerHTML = orderedProcesses
    .map(
      (process) => `
        <tr class="${process.id === data.first_process ? "is-first" : ""}">
          <td><strong>P${process.id}</strong></td>
          <td>${process.ticket ?? "-"}</td>
          <td>${process.queue_position ?? "-"}</td>
          <td>${process.id === data.first_process ? "En seccion critica" : process.status}</td>
        </tr>`
    )
    .join("");

  document.getElementById("lamport-winner").textContent = `P${data.first_process}`;
  document.getElementById("lamport-order").textContent = `Orden: ${data.access_order
    .map((id) => `P${id}`)
    .join(" -> ")}`;
  document.getElementById("lamport-results").hidden = false;
}

function resetLamport() {
  lamportRounds = [];
  document.querySelectorAll(".process-option").forEach((card) => {
    card.classList.remove("is-pending");
    card.classList.remove("is-selected");
    card.disabled = false;
    card.querySelector("span").textContent = "Sin ticket";
  });
  document.getElementById("round-history").innerHTML = "";
  document.getElementById("lamport-results").hidden = true;
  document.getElementById("lamport-concept").textContent =
    "Los procesos elegidos juntos reciben el mismo ticket. Si hay empate, se compara el ID fijo para decidir quien entra primero.";
  updateLamportButtons();
  setError("lamport-error");
}

function getClients() {
  return [...document.querySelectorAll(".client-input")].map((card) => ({
    id: Number(card.dataset.clientId),
    initial_time: card.querySelector(".client-time").value,
    round_trip_ms: Number(card.querySelector(".client-rtt").value),
  }));
}

function formatAdjustment(value) {
  const seconds = value / 1000;
  return `${seconds >= 0 ? "+" : ""}${seconds.toFixed(3)} s`;
}

async function runCristian() {
  setError("cristian-error");
  const data = await postJson("/api/cristian/simulate", {
    server_time: document.getElementById("server-time").value,
    clients: getClients(),
  });

  document.getElementById("cristian-concept").textContent = data.concept;
  document.getElementById("cristian-cards").innerHTML = data.clients
    .map(
      (client) => `
        <article class="sync-card">
          <div class="sync-card__title"><strong>C${client.id}</strong><span>${client.result}</span></div>
          <dl>
            <div><dt>Hora inicial</dt><dd>${client.initial_time}</dd></div>
            <div><dt>Hora del servidor</dt><dd>${client.server_time}</dd></div>
            <div><dt>RTT / 2</dt><dd>${client.estimated_one_way_ms} ms</dd></div>
            <div class="sync-card__final"><dt>Hora sincronizada</dt><dd>${client.synchronized_time}</dd></div>
            <div><dt>Ajuste realizado</dt><dd>${formatAdjustment(client.adjustment_ms)}</dd></div>
          </dl>
        </article>`
    )
    .join("");

  document.getElementById(
    "sync-result"
  ).textContent = `Resultado final: los ${data.clients.length} clientes quedaron sincronizados.`;
  document.getElementById("cristian-results").hidden = false;
}

document.getElementById("run-lamport").addEventListener("click", () => {
  runLamport().catch((error) => setError("lamport-error", error.message));
});

document.getElementById("assign-tickets").addEventListener("click", () => {
  assignTicketsToRound().catch((error) => setError("lamport-error", error.message));
});

document.querySelectorAll(".process-option").forEach((card) => {
  card.addEventListener("click", () => {
    card.classList.toggle("is-pending");
    card.querySelector("span").textContent = card.classList.contains("is-pending")
      ? "Seleccionado"
      : "Sin ticket";
    updateLamportButtons();
  });
});

document.getElementById("reset-lamport").addEventListener("click", resetLamport);

document.getElementById("run-cristian").addEventListener("click", () => {
  runCristian().catch((error) => setError("cristian-error", error.message));
});
