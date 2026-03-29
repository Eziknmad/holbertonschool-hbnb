/*
  HBnB Part 4 — scripts.js
  JavaScript logic will be added in subsequent tasks:
    Task 2: Login (JWT + cookie)              ✓
    Task 3: List of Places (fetch + filter)   ✓
    Task 4: Add Review (authenticated submit) ✓
*/

const API_URL = 'http://127.0.0.1:5000';

/* ── Cookie helpers ── */
function setCookie(name, value, days) {
  const expires = days
    ? '; expires=' + new Date(Date.now() + days * 864e5).toUTCString()
    : '';
  document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/';
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

/* ── Task 2: Login ── */
async function loginUser(email, password) {
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  if (response.ok) {
    const data = await response.json();
    setCookie('token', data.access_token, 7);
    window.location.href = 'index.html';
  } else {
    const errorEl = document.getElementById('login-error');
    if (errorEl) {
      errorEl.textContent = 'Login failed: ' + response.statusText;
    }
  }
}

/* ── Task 3: List of Places ── */
let allPlaces = [];

function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');

  if (!token) {
    if (loginLink) loginLink.style.display = 'block';
  } else {
    if (loginLink) loginLink.style.display = 'none';
    fetchPlaces(token);
  }
}

async function fetchPlaces(token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const response = await fetch(`${API_URL}/api/v1/places/`, { headers });
  if (response.ok) {
    allPlaces = await response.json();
    populatePriceFilter();
    displayPlaces(allPlaces);
  }
}

function populatePriceFilter() {
  const select = document.getElementById('price-filter');
  if (!select) return;
  select.innerHTML = '';
  [10, 50, 100, 'All'].forEach(val => {
    const option = document.createElement('option');
    option.value = val;
    option.textContent = val === 'All' ? 'All' : '$' + val;
    select.appendChild(option);
  });
  // Default to "All"
  select.value = 'All';

  select.addEventListener('change', (event) => {
    const selected = event.target.value;
    const cards = document.querySelectorAll('.place-card');
    cards.forEach(card => {
      const price = parseFloat(card.dataset.price);
      if (selected === 'All' || price <= parseFloat(selected)) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

function displayPlaces(places) {
  const list = document.getElementById('places-list');
  if (!list) return;
  list.innerHTML = '';

  if (places.length === 0) {
    list.innerHTML = '<div class="empty-state"><p>No places found.</p></div>';
    return;
  }

  places.forEach(place => {
    const card = document.createElement('div');
    card.className = 'place-card';
    card.dataset.price = place.price;
    card.innerHTML = `
      <h3>${place.title}</h3>
      <p class="price">$${place.price} <span>/ night</span></p>
      <a href="place.html?id=${place.id}" class="details-button">View Details</a>
    `;
    list.appendChild(card);
  });
}

/* ── Task 4: Add Review ── */
function getPlaceIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get('id');
}

async function submitReview(token, placeId, reviewText, rating) {
  const response = await fetch(`${API_URL}/api/v1/reviews/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
      comment: reviewText,
      rating: parseInt(rating),
      place_id: placeId
    })
  });
  return response;
}

function handleResponse(response, form) {
  if (response.ok) {
    alert('Review submitted successfully!');
    form.reset();
  } else {
    alert('Failed to submit review');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  /* ── Login form ── */
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      await loginUser(email, password);
    });
  }

  /* ── Index page ── */
  if (document.getElementById('places-list')) {
    checkAuthentication();
  }

  /* ── Add Review page ── */
  const reviewForm = document.getElementById('review-form');
  if (reviewForm && document.getElementById('rating')) {
    const token = getCookie('token');
    if (!token) {
      window.location.href = 'index.html';
      return;
    }

    const placeId = getPlaceIdFromURL();

    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const reviewText = document.getElementById('review').value.trim();
      const rating = document.getElementById('rating').value;
      const response = await submitReview(token, placeId, reviewText, rating);
      handleResponse(response, reviewForm);
    });
  }
});
