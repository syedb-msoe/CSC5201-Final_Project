// LOCAL development:
// const API_BASE_URL = "http://localhost:8001";

const API_BASE = "https://upload-service.jollygrass-3de8a9a7.centralus.azurecontainerapps.io";

async function upload() {
    const fileInput = document.getElementById("file");
    const data = new FormData();
    data.append("file", fileInput.files[0]);
    // Collect selected languages
    const selected = document.getElementById("languages").value;
    data.append("language", selected);

    const headers = getAuthHeader ? getAuthHeader() : {};
    const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        headers,
        body: data
    });

    const json = await res.json();
    alert('Document uploaded successfully!');
}