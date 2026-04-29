// dashboard.js - Core logic for Dashboard SPA

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auth Check
    const token = api.getToken();
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.role === 'admin') {
        window.location.href = 'admin.html';
        return;
    }

    // 2. Setup UI
    document.getElementById('userName').innerText = user.name;
    document.getElementById('userAvatar').innerText = user.name.charAt(0).toUpperCase();

    // 3. Load initial view
    loadView('overview');
    
    // 4. Start polling notifications
    fetchNotifications();
    setInterval(fetchNotifications, 15000); // Poll every 15s
});

function logout() {
    api.clearToken();
    window.location.href = 'index.html';
}

function loadView(viewId) {
    // Update sidebar active state
    document.querySelectorAll('.menu-item').forEach(el => {
        el.classList.remove('active');
        if (el.getAttribute('onclick')?.includes(viewId)) {
            el.classList.add('active');
        }
    });

    // Clone template and insert
    const template = document.getElementById(`tpl-${viewId}`);
    if (!template) return;
    
    const contentArea = document.getElementById('contentArea');
    contentArea.innerHTML = '';
    contentArea.appendChild(template.content.cloneNode(true));

    // Execute view-specific logic
    if (viewId === 'overview') {
        const user = JSON.parse(localStorage.getItem('user'));
        document.getElementById('overviewName').innerText = user.name;
        loadOverviewStats();
    } else if (viewId === 'myReports') {
        loadMyReports();
    } else if (viewId === 'notifications') {
        renderNotifications();
    }
}

// --- Data Loaders ---

async function loadOverviewStats() {
    try {
        const reports = await api.request('/reports/user/me');
        const family = await api.request('/family/');
        document.getElementById('countReports').innerText = reports.length || 0;
        document.getElementById('countFamily').innerText = family.length || 0;
    } catch (e) {
        console.error(e);
    }
}

async function loadMyReports() {
    try {
        const reports = await api.request('/reports/user/me');
        const list = document.getElementById('reportsList');
        if (!reports.length) {
            list.innerHTML = '<p class="text-muted">No reports found.</p>';
            return;
        }

        list.innerHTML = reports.map(r => `
            <div class="card">
                <img src="${r.photo_url}" style="width:100%; height:200px; object-fit:cover; border-radius:var(--radius-md); margin-bottom:1rem;">
                <h3>${r.name || 'Unknown'}</h3>
                <p class="text-sm text-muted">ID: ${r.report_id}</p>
                <div style="display:flex; justify-content:space-between; margin-top:1rem; align-items:center;">
                    <span style="background: ${r.status === 'approved' ? 'var(--success-green)' : (r.status === 'found' ? 'var(--accent-blue)' : '#f59e0b')}; color:white; padding:0.25rem 0.75rem; border-radius:1rem; font-size:0.8rem; text-transform:capitalize;">${r.status}</span>
                    <span class="text-sm">${new Date(r.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error(e);
    }
}

// --- Form Handlers ---

async function submitReport(e) {
    e.preventDefault();
    const btn = document.getElementById('btnReportSubmit');
    btn.disabled = true;
    btn.innerText = 'Uploading & Analyzing...';

    const form = document.getElementById('reportForm');
    const formData = new FormData(form);

    try {
        await api.request('/reports/', {
            method: 'POST',
            body: formData
        });
        showToast('Report submitted successfully! Waiting for admin approval.');
        form.reset();
        setTimeout(() => loadView('myReports'), 1500);
    } catch (e) {
        console.error(e);
    } finally {
        btn.disabled = false;
        btn.innerText = 'Submit Report';
    }
}

async function submitFamily(e) {
    e.preventDefault();
    const btn = document.getElementById('btnFamilySubmit');
    btn.disabled = true;
    btn.innerText = 'Registering Face Data...';

    const form = document.getElementById('familyForm');
    const formData = new FormData(form);

    try {
        await api.request('/family/', {
            method: 'POST',
            body: formData
        });
        showToast('Family member registered for Face Search Monitoring!');
        form.reset();
        setTimeout(() => loadView('overview'), 1500);
    } catch (e) {
        console.error(e);
    } finally {
        btn.disabled = false;
        btn.innerText = 'Register Family Member';
    }
}

async function submitFaceSearch(e) {
    e.preventDefault();
    const btn = document.getElementById('btnFaceSearch');
    btn.disabled = true;
    btn.innerText = 'Scanning Database...';

    const form = document.getElementById('searchFaceForm');
    const formData = new FormData(form);
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '<p class="text-center" style="grid-column: 1/-1;">Analyzing face data, please wait...</p>';

    try {
        const data = await api.request('/face/search', {
            method: 'POST',
            body: formData
        });
        
        if (!data.matches || data.matches.length === 0) {
            resultsDiv.innerHTML = '<p class="text-center text-muted" style="grid-column: 1/-1;">No matches found in the database.</p>';
            return;
        }

        resultsDiv.innerHTML = data.matches.map(m => `
            <div class="card" style="border: 2px solid ${m.confidence > 80 ? 'var(--success-green)' : 'var(--border-light)'}">
                <img src="${m.photo_url}" style="width:100%; height:200px; object-fit:cover; border-radius:var(--radius-md); margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3>${m.name}</h3>
                    <span style="font-weight:bold; color: ${m.confidence > 80 ? 'var(--success-green)' : 'var(--primary-orange)'}">${m.confidence}% Match</span>
                </div>
                <p class="text-sm text-muted mt-4">Report ID: ${m.report_id}</p>
                <p class="text-sm text-muted">Location: ${m.location}</p>
            </div>
        `).join('');
    } catch (e) {
        resultsDiv.innerHTML = '';
        console.error(e);
    } finally {
        btn.disabled = false;
        btn.innerText = 'Scan Database';
    }
}

async function submitTextSearch(e) {
    e.preventDefault();
    const btn = document.getElementById('btnTextSearch');
    btn.disabled = true;
    btn.innerText = 'Searching...';

    const q = document.getElementById('searchKeywordInput').value.trim();
    const resultsDiv = document.getElementById('textSearchResults');
    resultsDiv.innerHTML = '<p class="text-center" style="grid-column: 1/-1;">Searching records, please wait...</p>';

    try {
        const reports = await api.request(`/reports/search/text?q=${encodeURIComponent(q)}`);
        
        if (!reports || reports.length === 0) {
            resultsDiv.innerHTML = '<p class="text-center text-muted" style="grid-column: 1/-1;">No matching records found.</p>';
            return;
        }

        resultsDiv.innerHTML = reports.map(r => `
            <div class="card">
                <img src="${r.photo_url}" style="width:100%; height:200px; object-fit:cover; border-radius:var(--radius-md); margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3>${r.name || 'Unknown'}</h3>
                </div>
                <p class="text-sm text-muted mt-2"><strong>Location:</strong> ${r.location}</p>
                <p class="text-sm text-muted"><strong>Clothes:</strong> ${r.clothes || 'N/A'}</p>
                <p class="text-sm text-muted"><strong>Notes:</strong> ${r.notes || 'N/A'}</p>
                <p class="text-sm text-muted mt-2">Report ID: ${r.report_id}</p>
            </div>
        `).join('');
    } catch (e) {
        resultsDiv.innerHTML = '';
        console.error(e);
    } finally {
        btn.disabled = false;
        btn.innerText = 'Search Database';
    }
}

// --- Notifications ---
let cachedNotifs = [];

async function fetchNotifications() {
    try {
        cachedNotifs = await api.request('/notifications/');
        updateBell();
        
        // If current view is notifications, re-render silently
        if (document.getElementById('notificationsList')) {
            renderNotifications();
        }
    } catch (e) {
        console.error(e);
    }
}

function updateBell() {
    const unreadCount = cachedNotifs.filter(n => !n.read).length;
    const badge = document.getElementById('notifBadge');
    if (unreadCount > 0) {
        badge.style.display = 'flex';
        badge.innerText = unreadCount > 9 ? '9+' : unreadCount;
    } else {
        badge.style.display = 'none';
    }
}

function renderNotifications() {
    const list = document.getElementById('notificationsList');
    if (!list) return;

    if (!cachedNotifs.length) {
        list.innerHTML = '<div class="card"><p class="text-muted text-center">No notifications yet.</p></div>';
        return;
    }

    list.innerHTML = cachedNotifs.map(n => `
        <div class="card" style="padding: 1rem; border-left: 4px solid ${n.read ? 'var(--border-light)' : 'var(--primary-orange)'}; background: ${n.read ? 'var(--bg-white)' : 'var(--bg-cream)'}">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <strong>System Alert</strong>
                <span class="text-sm text-muted">${new Date(n.created_at).toLocaleString()}</span>
            </div>
            <p>${n.message}</p>
            ${!n.read ? `<button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size:0.8rem; margin-top:0.5rem;" onclick="markRead('${n.id}')">Mark Read</button>` : ''}
        </div>
    `).join('');
}

async function markRead(id) {
    try {
        await api.request(`/notifications/${id}/read`, { method: 'PATCH' });
        await fetchNotifications();
    } catch (e) {}
}

async function markAllRead() {
    try {
        await api.request('/notifications/mark-all-read', { method: 'POST' });
        await fetchNotifications();
        showToast('All notifications marked as read');
    } catch (e) {}
}
