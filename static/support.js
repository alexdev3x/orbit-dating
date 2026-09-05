const list = document.getElementById("list");

async function load() {
  const data = await (await fetch("/api/support/tickets")).json();
  list.innerHTML = (data.tickets || []).map((t) => `
    <article class="ticket" data-id="${t.id}">
      <h3>${t.subject} <small class="muted">${t.id} · ${t.status}</small></h3>
      <div class="thread">
        ${(t.messages || []).map((m) =>
          `<div class="msg"><strong>${m.role}${m.name ? " · " + m.name : ""}</strong> ${m.text}</div>`
        ).join("")}
      </div>
      <form class="reply">
        <input name="text" placeholder="Reply…" required />
        <label class="check"><input type="checkbox" name="as_support" /> as support</label>
        <button type="submit">Send</button>
      </form>
    </article>
  `).join("") || "<p class='muted'>No tickets.</p>";

  list.querySelectorAll("form.reply").forEach((form) => {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const id = form.closest(".ticket").dataset.id;
      const text = form.text.value;
      const as_support = form.as_support.checked;
      await fetch(`/api/support/tickets/${id}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, as_support }),
      });
      await load();
    };
  });
}

document.getElementById("new").onsubmit = async (e) => {
  e.preventDefault();
  await fetch("/api/support/tickets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      subject: document.getElementById("subject").value,
      text: document.getElementById("text").value,
    }),
  });
  e.target.reset();
  await load();
};

load();
