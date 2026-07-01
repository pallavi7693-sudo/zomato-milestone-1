const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:5000').replace(/\/+$/, '');

const DEFAULT_LOCATIONS = [
  "Jayanagar", "Banashankari", "Basavanagudi", "JP Nagar",
  "Koramangala", "Indiranagar", "Whitefield", "HSR Layout",
  "Malleshwaram", "MG Road", "BTM Layout", "Electronic City"
];

const DEFAULT_CUISINES = [
  "Italian", "Chinese", "Biryani", "North Indian", "South Indian",
  "Fast Food", "Continental", "Desserts", "Bakery", "Beverages",
  "Street Food", "Cafe", "Burger", "Pizza", "Mughlai"
];

const DEFAULT_TYPES = [
  "Casual Dining", "Fine Dining", "Cafe", "Pub", "Bar",
  "Lounge", "Quick Bites"
];

export async function fetchLocations() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/locations`);
    const data = await res.json();
    return (data.locations && data.locations.length > 0) ? data.locations : DEFAULT_LOCATIONS;
  } catch (e) {
    console.error('Failed to load locations from API, using fallback:', e);
    return DEFAULT_LOCATIONS;
  }
}

export async function fetchCuisines() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/cuisines`);
    const data = await res.json();
    return (data.cuisines && data.cuisines.length > 0) ? data.cuisines : DEFAULT_CUISINES;
  } catch (e) {
    console.error('Failed to load cuisines from API, using fallback:', e);
    return DEFAULT_CUISINES;
  }
}

export async function fetchRestaurantTypes() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/restaurant-types`);
    const data = await res.json();
    return (data.types && data.types.length > 0) ? data.types : DEFAULT_TYPES;
  } catch (e) {
    console.error('Failed to load restaurant types from API, using fallback:', e);
    return DEFAULT_TYPES;
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
