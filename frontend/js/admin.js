// admin.js - Admin Panel Logic

document.addEventListener('DOMContentLoaded', () => {
    const token = api.getToken();
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.role !== 'admin') {
        window.location.href = 'dashboard.html';
        return;
    }

    loadAdminView('reports');
});

function logout() {
    api.clearToken();
    window.location.href = 'index.html';
}

function loadAdminView(viewId) {
    document.querySelectorAll('.menu-item').forEach(el => {
        el.classList.remove('active');
        if (el.getAttribute('onclick')?.includes(viewId)) {
            el.classList.add('active');
        }
    });

    const template = document.getElementById(`tpl-${viewId}`);
    if (!template) return;
    
    const contentArea = document.getElementById('adminContentArea');
    contentArea.innerHTML = '';
    contentArea.appendChild(template.content.cloneNode(true));

    if (viewId === 'reports') {
        fetchAdminReports();
    } else if (viewId === 'users') {
        fetchAdminUsers();
    }
}

async function fetchAdminReports() {
    // Enhanced: fetch once, store locally, enable search + pagination + inline actions
    const tbody = document.querySelector('#reportsTable tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';
    try {
        window._adminReports = await api.request('/admin/reports') || [];
        window._reportsPage = 1;
        window._reportsPageSize = 10;
        renderAdminReports();

        // Setup search and pagination handlers
        const search = document.getElementById('adminReportSearch');
        if (search) {
            search.addEventListener('input', () => { window._reportsPage = 1; renderAdminReports(); });
        }
        const prev = document.getElementById('prevPage');
        const next = document.getElementById('nextPage');
        if (prev) prev.onclick = () => { if (window._reportsPage>1) { window._reportsPage--; renderAdminReports(); } };
        if (next) next.onclick = () => { window._reportsPage++; renderAdminReports(); };

    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">Error loading reports.</td></tr>`;
    }
}

function renderAdminReports() {
    const all = window._adminReports || [];
    const q = (document.getElementById('adminReportSearch')?.value || '').toLowerCase().trim();
    const filtered = all.filter(r => {
        if (!q) return true;
        return (r.report_id || '').toLowerCase().includes(q) || (r.name || '').toLowerCase().includes(q) || (r.status || '').toLowerCase().includes(q);
    });

    const countEl = document.getElementById('reportsCount');
    if (countEl) countEl.innerText = filtered.length;

    const page = Math.max(1, window._reportsPage || 1);
    const pageSize = window._reportsPageSize || 10;
    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    if (page > totalPages) window._reportsPage = totalPages;

    const start = (window._reportsPage - 1) * pageSize;
    const pageItems = filtered.slice(start, start + pageSize);

    const tbody = document.querySelector('#reportsTable tbody');
    if (!pageItems.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No reports found.</td></tr>';
    } else {
        tbody.innerHTML = pageItems.map(r => `
            <tr data-id="${r.id}">
                <td><strong>${r.report_id}</strong></td>
                <td>${r.name || 'Unknown'}</td>
                <td>${new Date(r.created_at).toLocaleDateString()}</td>
                <td><span class="status-badge status-${r.status}">${r.status}</span></td>
                <td>
                    <div style="display:flex; gap:0.5rem;">
                        <button class="btn btn-primary" onclick="updateReportStatusInline('${r.id}','approved')">Approve</button>
                        <button class="btn btn-outline" onclick="updateReportStatusInline('${r.id}','rejected')">Reject</button>
                        <button class="btn btn-outline" onclick="updateReportStatusInline('${r.id}','found')">Mark Found</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    const pageEl = document.getElementById('reportsPage');
    if (pageEl) pageEl.innerText = `${window._reportsPage} / ${totalPages}`;

    // Disable prev/next appropriately
    const prev = document.getElementById('prevPage');
    const next = document.getElementById('nextPage');
    if (prev) prev.disabled = window._reportsPage <= 1;
    if (next) next.disabled = window._reportsPage >= totalPages;
}

async function updateReportStatus(id, status) {
    // kept for backward compatibility
    return updateReportStatusInline(id, status);
}

async function updateReportStatusInline(id, status) {
    if (!id || !status) return;
    if (!confirm(`Change status to ${status}?`)) return;
    try {
        await api.request(`/admin/reports/${id}/status?status=${status}`, { method: 'PATCH' });
        showToast('Status updated');
        // update local cache and re-render
        const r = (window._adminReports || []).find(x => x.id === id);
        if (r) r.status = status;
        renderAdminReports();
    } catch (e) {}
}

async function fetchAdminUsers() {
    const tbody = document.querySelector('#usersTable tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';
    try {
        const users = await api.request('/admin/users');
        if (!users.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No users found.</td></tr>';
            return;
        }

        tbody.innerHTML = users.map(u => `
            <tr>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td>${u.mobile}</td>
                <td>${new Date(u.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-outline" style="color:red; border-color:red; padding:4px 8px; font-size:0.8rem;" onclick="deleteUser('${u.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">Error loading users.</td></tr>`;
    }
}

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user completely?')) return;
    try {
        await api.request(`/admin/users/${id}`, { method: 'DELETE' });
        showToast('User deleted successfully');
        fetchAdminUsers();
    } catch (e) {}
}
