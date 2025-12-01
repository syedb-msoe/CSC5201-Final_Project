// LOCAL development:
// const API_BASE_URL = "http://localhost:8004";

// Azure Container Apps (example):
// const API_BASE_URL = "https://adminservice-xyz.azcontainerapps.io";

const API_BASE_URL = "http://localhost:8004"; // change this later

async function loadStats() {
    const url = `${API_BASE_URL}/admin/stats`;
    console.log("Fetching:", url);

    try {
        const response = await fetch(url);
        if (!response.ok) {
            alert("Error fetching stats: " + response.status);
            return;
        }

        const stats = await response.json();

        // Update raw JSON block
        document.getElementById("rawJson").textContent =
            JSON.stringify(stats, null, 2);

        // Update human-readable table
        const tbody = document.getElementById("statsBody");
        tbody.innerHTML = "";

        stats.endpoints.forEach(stat => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${stat.endpoint}</td>
                <td>${stat.method}</td>
                <td>${stat.count}</td>
                <td>${stat.avg_response_ms}</td>
            `;

            tbody.appendChild(tr);
        });

    } catch (err) {
        alert("Error loading stats: " + err);
    }
}