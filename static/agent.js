const history = [];

async function loadCfg() {
  const a = await (await fetch("/api/agent")).json();
  document.getElementById("name").value = a.name;
  document.getElementById("instructions").value = a.instructions;
  document.getElementById("auto").checked = !!a.auto_reply_support;
}

document.getElementById("cfg").onsubmit = async (e) => {
  e.preventDefault();
  await fetch("/api/agent", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: document.getElementById("name").value,
      instructions: document.getElementById("instructions").value,
      auto_reply_support: document.getElementById("auto").checked,
    }),
  });
};

document.getElementById("ask").onsubmit = async (e) => {
  e.preventDefault();
  const q = document.getElementById("q");
  const text = q.value;
  q.value = "";
  history.push({ role: "user", text });
  const res = await fetch("/api/agent/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, history }),
  });
  const data = await res.json();
  history.push({ role: "assistant", text: data.text });
  const log = document.getElementById("log");
  log.innerHTML += `<div class="msg"><strong>you</strong> ${text}</div>`;
  log.innerHTML += `<div class="msg"><strong>${data.agent} · ${data.provider}</strong> ${data.text}</div>`;
};

loadCfg();
