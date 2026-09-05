const gate = document.getElementById("gate");
const grid = document.getElementById("grid");
const sheet = document.getElementById("sheet");
const profileEl = document.getElementById("profile");
const threadEl = document.getElementById("thread");
let current = null;

if (localStorage.getItem("orbit_18") === "1") gate.remove();

document.getElementById("yes").onclick = () => {
  localStorage.setItem("orbit_18", "1");
  gate.remove();
};
document.getElementById("no").onclick = () => {
  document.body.innerHTML = "<p style='padding:2rem'>Orbit is 18+ only.</p>";
};

async function loadGrid() {
  const res = await fetch("/api/nearby");
  const data = await res.json();
  grid.innerHTML = data.results.map((p) => `
    <button class="card" data-id="${p.id}" style="box-shadow: inset 0 0 0 2px ${p.accent}33">
      <strong>${p.name}, ${p.age}</strong>
      <small>${p.distance_km} km · ${p.city}</small>
      <span class="dot ${p.online ? "" : "off"}"></span>
    </button>
  `).join("");
  grid.querySelectorAll(".card").forEach((btn) => {
    btn.onclick = () => openProfile(btn.dataset.id);
  });
}

async function openProfile(id) {
  current = id;
  const p = await (await fetch("/api/profiles/" + id)).json();
  profileEl.innerHTML = `
    <h2>${p.name}, ${p.age}</h2>
    <p class="muted">${p.distance_km} km · ${p.city} · ${p.tribe}</p>
    <p>${p.headline}</p>
    <p>${p.bio}</p>
    <div class="tags">${p.tags.map((t) => `<span>${t}</span>`).join("")}</div>
  `;
  sheet.classList.remove("hidden");
  await loadThread();
}

async function loadThread() {
  const data = await (await fetch("/api/messages/" + current)).json();
  threadEl.innerHTML = (data.messages || []).map((m) =>
    `<div class="msg"><strong>${m.from}</strong> ${m.text}</div>`
  ).join("") || "<p class='muted'>No messages yet.</p>";
}

document.getElementById("close").onclick = () => sheet.classList.add("hidden");

document.getElementById("chat").onsubmit = async (e) => {
  e.preventDefault();
  const input = document.getElementById("text");
  await fetch("/api/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ to: current, text: input.value }),
  });
  input.value = "";
  await loadThread();
};

document.getElementById("block").onclick = async () => {
  await fetch("/api/block/" + current, { method: "POST" });
  sheet.classList.add("hidden");
  await loadGrid();
};

document.getElementById("report").onclick = async () => {
  const reason = prompt("Why are you reporting this profile?");
  if (!reason) return;
  await fetch("/api/report/" + current, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  sheet.classList.add("hidden");
  await loadGrid();
};

loadGrid();
