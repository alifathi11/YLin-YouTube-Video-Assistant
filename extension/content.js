const BASE = "http://127.0.0.1:8000";

let videoIdCache = null;
let isIndexed = false;
let lastCitations = [];

// =====================
// utils
// =====================

function getVideoUrl() {
    return window.location.href;
}

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
}

function seekVideo(time) {
    const video = document.querySelector("video");
    if (video) {
        video.currentTime = time;
        video.play();
    }
}

// =====================
// UI
// =====================

function createUI() {
    const root = document.createElement("div");
    root.id = "rag-root";

    root.innerHTML = `
        <div id="rag-header">
            <div id="rag-brand">
                <div id="rag-logo">Y</div>
                <div id="rag-title">
                    <strong>YLin</strong>
                    <span>Video Assistant</span>
                </div>
            </div>
            <button
                id="rag-close"
                type="button"
                aria-label="Close assistant"
                title="Close assistant"
            >×</button>
        </div>

        <div id="rag-chat">
            <div id="rag-welcome">
                <strong>Ask about this video</strong>
                <span>Get answers with clickable timestamps.</span>
            </div>
        </div>

        <div id="rag-input-box">
            <input id="rag-input" placeholder="Ask anything about this video..." />
            <button
                id="rag-send"
                type="button"
                aria-label="Send question"
                title="Send question"
            >➤</button>
        </div>
    `;

    const launcher = document.createElement("button");
    launcher.id = "rag-launcher";
    launcher.type = "button";
    launcher.setAttribute("aria-label", "Open YLin Video Assistant");
    launcher.setAttribute("aria-expanded", "true");
    launcher.title = "Open YLin Video Assistant";
    launcher.textContent = "Y";

    document.body.appendChild(root);
    document.body.appendChild(launcher);

    function setPanelOpen(isOpen) {
        root.classList.toggle("is-closed", !isOpen);
        launcher.classList.toggle("is-visible", !isOpen);
        launcher.setAttribute("aria-expanded", String(isOpen));

        if (isOpen) {
            setTimeout(() => document.getElementById("rag-input")?.focus(), 220);
        }
    }

    document.getElementById("rag-send").onclick = ask;
    document.getElementById("rag-close").onclick = () => setPanelOpen(false);
    launcher.onclick = () => setPanelOpen(true);

    document.getElementById("rag-input").addEventListener("keydown", (e) => {
        if (e.key === "Enter") ask();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !root.classList.contains("is-closed")) {
            setPanelOpen(false);
        }
    });

    document.addEventListener("click", (e) => {
        const citation = e.target.closest(".citation");

        if (citation) {
            const index = citation.dataset.index;
            const c = lastCitations[index];
            if (c) seekVideo(c.start);
        }
    });
}

// =====================
// index
// =====================

async function indexVideoIfNeeded() {
    if (isIndexed) return;

    const res = await fetch(`${BASE}/api/videos/index`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: getVideoUrl() })
    });

    const data = await res.json();

    videoIdCache = data.video_id;
    isIndexed = true;
}

// =====================
// typing effect
// =====================

function typeText(element, text, speed = 8) {
    element.textContent = "";

    let i = 0;

    const interval = setInterval(() => {
        element.textContent += text[i] || "";
        i++;

        if (i >= text.length) {
            clearInterval(interval);
        }
    }, speed);
}

// =====================
// messages
// =====================

function addMessage(role, text, citations = null) {
    const chat = document.getElementById("rag-chat");
    const welcome = document.getElementById("rag-welcome");

    if (welcome) welcome.remove();

    const msg = document.createElement("div");
    msg.className = `msg ${role}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    msg.appendChild(bubble);
    chat.appendChild(msg);

    if (role === "assistant") {
        typeText(bubble, text);
    } else {
        bubble.textContent = text;
    }

    if (role === "assistant" && citations?.length) {
        lastCitations = citations;

        const citBox = document.createElement("div");
        citBox.className = "citations";

        citBox.innerHTML = citations.map((c, i) => `
            <div class="citation" data-index="${i}">
                ▶ ${formatTime(c.start)} → ${formatTime(c.end)}
            </div>
        `).join("");

        msg.appendChild(citBox);
    }

    chat.scrollTop = chat.scrollHeight;
}

// =====================
// loading
// =====================

function addTyping() {
    const chat = document.getElementById("rag-chat");

    const typing = document.createElement("div");
    typing.id = "typing";
    typing.className = "msg assistant";

    typing.innerHTML = `<div class="bubble typing">thinking...</div>`;

    chat.appendChild(typing);
    chat.scrollTop = chat.scrollHeight;
}

function removeTyping() {
    const t = document.getElementById("typing");
    if (t) t.remove();
}

// =====================
// main flow
// =====================

async function ask() {
    const input = document.getElementById("rag-input");
    const question = input.value.trim();

    if (!question) return;

    input.value = "";

    addMessage("user", question);
    addTyping();

    await indexVideoIfNeeded();

    const res = await fetch(`${BASE}/api/chat/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            video_id: videoIdCache,
            question
        })
    });

    const data = await res.json();

    removeTyping();

    if (!data?.answer) {
        addMessage("assistant", "Error: invalid response from server");
        return;
    }

    addMessage("assistant", data.answer, data.citations || []);
}

// =====================
// init
// =====================

createUI();