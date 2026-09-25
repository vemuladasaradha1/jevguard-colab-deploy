const canvas = document.getElementById("stars");
const ctx = canvas.getContext("2d");

let stars = [];

function resize() {
  canvas.width = window.innerWidth * devicePixelRatio;
  canvas.height = window.innerHeight * devicePixelRatio;
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  stars = Array.from({ length: Math.min(170, Math.floor(window.innerWidth / 8)) }, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    r: Math.random() * 1.5 + .2,
    a: Math.random() * .7 + .2,
    s: Math.random() * .15 + .02
  }));
}

function animate() {
  ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

  for (const s of stars) {
    s.y += s.s;
    if (s.y > window.innerHeight) s.y = -2;

    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(180,190,255,${s.a})`;
    ctx.fill();
  }

  requestAnimationFrame(animate);
}

window.addEventListener("resize", resize);
resize();
animate();

const messages = document.getElementById("messages");
const queryBox = document.getElementById("query");
const send = document.getElementById("send");
const status = document.getElementById("status");
const latency = document.getElementById("latency");
const tools = document.getElementById("tools");

function addMessage(text, who = "assistant", meta = "JEVGUARD") {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${who}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = who === "user" ? "U" : "J";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const m = document.createElement("div");
  m.className = "meta";
  m.textContent = meta;

  const p = document.createElement("p");
  p.textContent = text;

  bubble.appendChild(m);
  bubble.appendChild(p);
  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

async function sendQuery() {
  const query = queryBox.value.trim();
  if (!query) return;

  addMessage(query, "user", "TRANSMISSION");
  queryBox.value = "";
  send.disabled = true;
  status.textContent = "THINKING";
  status.style.color = "#fbbf24";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed.");
    }

    addMessage(data.answer || "No answer returned.", "assistant", `JEVGUARD • ${data.status.toUpperCase()}`);

    latency.textContent = `${data.latency_ms} ms`;
    tools.textContent = `TOOLS: ${(data.tools_used || []).join(", ").toUpperCase() || "NONE"}`;
    status.textContent = data.status.toUpperCase();
    status.style.color = data.status === "approved" ? "#4ade80" : "#fbbf24";
  } catch (err) {
    addMessage(`Connection error: ${err.message}`, "assistant", "SYSTEM ERROR");
    status.textContent = "ERROR";
    status.style.color = "#fb7185";
  } finally {
    send.disabled = false;
    queryBox.focus();
  }
}

send.addEventListener("click", sendQuery);

queryBox.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendQuery();
  }
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    queryBox.value = chip.dataset.query;
    queryBox.focus();
  });
});
