// AUTH_BASE: change this to your deployed auth service URL or localhost for development
// LOCAL dev example: const AUTH_BASE = 'http://localhost:8004';
const AUTH_BASE = 'https://auth-service.jollygrass-3de8a9a7.centralus.azurecontainerapps.io';

async function authRegister(email, password) {
    const res = await fetch(`${AUTH_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw await res.json();
    return res.json();
}

async function authLogin(email, password) {
    const res = await fetch(`${AUTH_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw await res.json();
    return res.json();
}

function getAuthHeader() {
    const token = localStorage.getItem('access_token');
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
}
