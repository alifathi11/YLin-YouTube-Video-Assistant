const BASE = "http://127.0.0.1:8000/api";

async function indexVideo() {
    const url = document.getElementById("url").value;

    const res = await fetch(`${BASE}/videos/index`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    });

    const data = await res.json();

    document.getElementById("output").innerText =
        JSON.stringify(data, null, 2);

    document.getElementById("videoId").value = data.video_id;
}

async function ask() {
    const video_id = document.getElementById("videoId").value;
    const question = document.getElementById("question").value;

    const res = await fetch(`${BASE}/chat/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id, question })
    });

    const data = await res.json();

    document.getElementById("output").innerText =
        JSON.stringify(data, null, 2);
}