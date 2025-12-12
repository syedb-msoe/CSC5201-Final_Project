const API_BASE = "https://results-service.jollygrass-3de8a9a7.centralus.azurecontainerapps.io";

async function loadResults() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        document.getElementById("results").innerHTML =
            "<p class='error'>You are not logged in.</p>";
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/results`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) {
            document.getElementById("results").innerHTML =
                `<p class='error'>Error: ${res.status} ${res.statusText}</p>`;
            return;
        }

        const data = await res.json();
        renderResults(data);
    } catch (err) {
        document.getElementById("results").innerHTML =
            `<p class='error'>Failed to load results: ${err}</p>`;
    }
}

function renderResults(data) {
    const container = document.getElementById("results");

    if (data.count === 0) {
        container.innerHTML = "<p>No documents found.</p>";
        return;
    }

    container.innerHTML = "";

    data.documents.forEach(doc => {
        const div = document.createElement("div");
        div.className = "doc-card";

        div.innerHTML = `
            <h2>${extractFileName(doc.blobPath)}</h2>
            <p><strong>Uploaded:</strong> ${doc.uploadedAt || "Unknown"}</p>
            <p><strong>Languages:</strong> ${doc.languages?.join(", ") || "None"}</p>

            <h3>Extracted Text</h3>
            <div class="text-block">${doc.processedText || "(No processed text available)"}</div>
        `;

        container.appendChild(div);
    });
}

function extractFileName(path) {
    return path.split("/").pop();
}

// Logout (clear token)
document.getElementById("logout").onclick = () => {
    localStorage.removeItem("token");
    window.location.href = "index.html";
};

// Load results immediately
loadResults();