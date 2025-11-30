async function upload() {
    const fileInput = document.getElementById("file");
    const data = new FormData();
    data.append("file", fileInput.files[0]);

    const res = await fetch("http://localhost:8001/upload", {
        method: "POST",
        body: data
    });

    const json = await res.json();
    alert(JSON.stringify(json, null, 2));
}