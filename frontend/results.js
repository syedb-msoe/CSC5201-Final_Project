// LOCAL development:
// const API_BASE_URL = "http://localhost:8003";

// Azure Container Apps (example):
// const API_BASE_URL = "https://resultsservice-xyz.azcontainerapps.io";

const API_BASE_URL = "http://localhost:8003"; // change this later

async function loadResults() {
    const docId = document.getElementById("docId").value.trim();
    if (!docId) {
        alert("Please enter a document ID");
        return;
    }

    const url = `${API_BASE_URL}/results/${docId}`;
    console.log("Fetching:", url);

    try {
        const response = await fetch(url);

        if (!response.ok) {
            document.getElementById("jsonOutput").textContent =
                `Server returned error: ${response.status}`;
            return;
        }

        const data = await response.json();

        document.getElementById("jsonOutput").textContent = 
            JSON.stringify(data, null, 2);

    } catch (err) {
        document.getElementById("jsonOutput").textContent =
            "Error fetching results: " + err;
    }
}