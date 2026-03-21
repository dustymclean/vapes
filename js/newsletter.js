document.querySelector('.newsletter-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = e.target.querySelector('input').value;
    const body = JSON.stringify({ email });
    fetch('https://formspree.io/f/xeoqkzdj', { method: 'POST', body, headers: {'Content-Type': 'application/json'} });
    fetch('https://vapes.pixiespantryshop.com/api/v1/newsletter/subscribe', { method: 'POST', body, headers: {'Content-Type': 'application/json'} });
    alert("Subscription confirmed.");
});
