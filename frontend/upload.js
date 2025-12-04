// LOCAL development:
// const API_BASE_URL = "http://localhost:8001";

const API_BASE = "https://upload-service.jollygrass-3de8a9a7.centralus.azurecontainerapps.io";

async function upload() {
    const fileInput = document.getElementById("file");
    const data = new FormData();
    data.append("file", fileInput.files[0]);

    const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: data
    });

    const json = await res.json();
    alert(JSON.stringify(json, null, 2));
}