const casesList = document.getElementById('casesList');
let allReports = [];

function formatDate(value) {
    const date = new Date(value);
    return isNaN(date.getTime()) ? 'Unknown date' : date.toLocaleDateString('en-IN');
}

function renderCases(filter = '') {
    const q = (filter || '').toLowerCase().trim();
    if (!allReports.length) {
        casesList.innerHTML = '<div class="loading-card">No published cases found yet.</div>';
        return;
    }

    const filtered = allReports.filter(r => {
        if (!q) return true;
        const name = (r.name || '').toLowerCase();
        const location = (r.location || '').toLowerCase();
        const status = (r.status || '').toLowerCase();
        const notes = (r.notes || '').toLowerCase();
        return name.includes(q) || location.includes(q) || status.includes(q) || notes.includes(q);
    });

    if (!filtered.length) {
        casesList.innerHTML = '<div class="loading-card">No cases match your search.</div>';
        return;
    }

    const cards = filtered.map(report => {
        const dateLabel = formatDate(report.date || report.created_at);
        const location = report.location || 'Location not available';
        return `
            <article class="case-card">
                <div class="case-card-top">
                    <div>
                        <h3>${report.name || 'Unnamed Case'}</h3>
                        <div class="case-meta">${location} · ${dateLabel}</div>
                    </div>
                    <span class="status-badge status-${report.status}">${report.status}</span>
                </div>
                <img src="${report.photo_url || 'https://via.placeholder.com/520x320?text=No+Photo'}" alt="Case photo" />
                <p>${report.notes || 'No additional notes were submitted for this case.'}</p>
            </article>
        `;
    }).join('');

    casesList.innerHTML = `<div class="case-grid">${cards}</div>`;
}

async function loadCases() {
    casesList.innerHTML = '<div class="loading-card">Loading reported cases...</div>';

    try {
        const reports = await api.request('/reports');
        allReports = Array.isArray(reports) ? reports : [];
        renderCases();
    } catch (error) {
        casesList.innerHTML = '<div class="loading-card">Unable to load cases right now. Please try again later.</div>';
    }
}

// Hook up search input
window.addEventListener('DOMContentLoaded', () => {
    const search = document.getElementById('caseSearch');
    if (search) {
        search.addEventListener('input', (e) => renderCases(e.target.value));
    }
    loadCases();
});
