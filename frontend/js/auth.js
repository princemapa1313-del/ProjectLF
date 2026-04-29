// auth.js - Authentication Modal Logic

// Modal Handling
function openLoginModal() {
    document.getElementById('registerModal').classList.remove('active');
    document.getElementById('loginModal').classList.add('active');
}

function openRegisterModal() {
    document.getElementById('loginModal').classList.remove('active');
    document.getElementById('registerModal').classList.add('active');
}

function closeModals() {
    document.querySelectorAll('.modal-overlay').forEach(el => el.classList.remove('active'));
}

// Redirect if already logged in
window.addEventListener('DOMContentLoaded', () => {
    if (api.getToken()) {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (user.role === 'admin') {
            window.location.href = 'admin.html';
        } else {
            window.location.href = 'dashboard.html';
        }
    }
});

// Form Submissions
async function handleLogin(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    btn.disabled = true;
    btn.innerText = 'Logging in...';

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    try {
        const data = await api.request('/auth/login', {
            method: 'POST',
            body: { email, password }
        });

        api.setToken(data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        showToast('Login successful!');
        
        setTimeout(() => {
            if (data.user.role === 'admin') {
                window.location.href = 'admin.html';
            } else {
                window.location.href = 'dashboard.html';
            }
        }, 1000);
        
    } catch (error) {
        // Error toast is handled in api.js
    } finally {
        btn.disabled = false;
        btn.innerText = 'Login securely';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    btn.disabled = true;
    btn.innerText = 'Registering...';

    const name = document.getElementById('regName').value;
    const mobile = document.getElementById('regMobile').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;

    try {
        const data = await api.request('/auth/register', {
            method: 'POST',
            body: { name, email, mobile, password }
        });

        api.setToken(data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        showToast('Registration successful! Redirecting...');
        
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);

    } catch (error) {
        // Error handled in api.js
    } finally {
        btn.disabled = false;
        btn.innerText = 'Register Now';
    }
}
