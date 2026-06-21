const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:5000';

export async function fetchLocations() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/locations`);
    const data = await res.json();
    return data.locations || [];
  } catch (e) {
    console.error('Failed to load locations:', e);
    return [];
  }
}

export async function fetchCuisines() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/cuisines`);
    const data = await res.json();
    return data.cuisines || [];
  } catch (e) {
    console.error('Failed to load cuisines:', e);
    return [];
  }
}

export async function fetchRestaurantTypes() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/restaurant-types`);
    const data = await res.json();
    return data.types || [];
  } catch (e) {
    console.error('Failed to load restaurant types:', e);
    return [];
  }
}

export async function fetchAIRecommendations(query) {
  const res = await fetch(`${BACKEND_URL}/api/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit: 6 }),
  });
  return await res.json();
}

export async function fetchFilterRecommendations(filters) {
  const res = await fetch(`${BACKEND_URL}/api/filter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters),
  });
  return await res.json();
}
