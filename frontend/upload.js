// LOCAL development:
// const API_BASE_URL = "http://localhost:8001";

const API_BASE = "https://upload-service.jollygrass-3de8a9a7.centralus.azurecontainerapps.io";

async function upload() {
    const fileInput = document.getElementById("file");
    const data = new FormData();
    data.append("file", fileInput.files[0]);
    // Collect selected languages
    const selected = Array.from(document.querySelectorAll('input[name="languages"]:checked')).map(x => x.value);
    data.append("languages", JSON.stringify(selected));

    const headers = getAuthHeader ? getAuthHeader() : {};
    const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        headers,
        body: data
    });

    const json = await res.json();
    alert(JSON.stringify(json, null, 2));
}