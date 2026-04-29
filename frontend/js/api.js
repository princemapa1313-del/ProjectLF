/* api.js - Centralized API calling wrapper */
const API_BASE_URL = 'http://127.0.0.1:8000';

const api = {
    getToken() {
        return localStorage.getItem('token');
    },

    setToken(token) {
        localStorage.setItem('token', token);
    },

    clearToken() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            ...options.headers
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // If body is plain object, stringify and add JSON content-type
        // If FormData, don't set Content-Type (browser does it with boundary)
        if (options.body && !(options.body instanceof FormData)) {
            options.body = JSON.stringify(options.body);
            headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(url, { ...options, headers });
            
            // Handle unauthorized globally
            if (response.status === 401) {
                if (!endpoint.includes('/auth/login')) {
                    this.clearToken();
                    window.location.href = 'index.html';
                    throw new Error("Session expired. Please login again.");
                }
            }

            const contentType = response.headers.get('content-type') || '';
            const data = contentType.includes('application/json')
                ? await response.json().catch(() => null)
                : null;

            if (!response.ok) {
                const detail = data?.detail || data?.message || response.statusText;
                throw new Error(detail || "Something went wrong");
            }

            return data;
        } catch (error) {
            showToast(error.message, 'error');
            throw error;
        }
    }
};

// Global UI Helpers
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
