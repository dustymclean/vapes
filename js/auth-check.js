document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const authArea = document.getElementById('auth-buttons');
    if (authArea) {
        if (token) {
            authArea.innerHTML = `<div class="nav-section-label">Session</div>
                <a href="index.html" class="sidebar-link" style="font-weight:700;">Hardware Hub</a>
                <a href="#" onclick="localStorage.clear();location.reload();" class="sidebar-link" style="color:red;">Logout</a>`;
        } else {
            authArea.innerHTML = `<div class="nav-section-label">Account</div>
                <a href="login.html" class="sidebar-link">Login</a>
                <a href="signup.html" class="sidebar-link" style="font-weight:900; font-size:1.1em;">SIGN UP</a>`;
        }
    }
});
