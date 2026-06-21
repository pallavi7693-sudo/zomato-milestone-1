# GastroAI Deployment Plan (Vercel + Railway)

This plan outlines the steps to decouple the monolithic Flask application into a standalone frontend (deployed on Vercel) and a REST API backend (deployed on Railway).

## Database Strategy
Railway's filesystem is ephemeral, meaning any writes to the SQLite database will be lost when the app restarts. However, since our application only *reads* from the database for searches, we safely use the bundled `restaurants.db`. 
The database is small (~1.8MB), so it is committed to the repository and the Railway build will include the pre-built database.

## CORS Configuration
By separating the frontend and backend, they will be hosted on different domains. `flask-cors` is added to the backend to allow the Vercel frontend to make API requests. 
For security, you should configure CORS to *only* accept requests from your Vercel deployment URL (once generated).

---

## 1. Backend Modifications (Railway)

The Flask application is prepared for production on Railway.

- **`requirements.txt`**: Added `gunicorn` (production WSGI server) and `flask-cors` (to handle Cross-Origin Resource Sharing).
- **`web_app.py`**: Imported and initialized `flask-cors` for the Vercel frontend.
- **`Procfile`**: Created to tell Railway how to run the application using Gunicorn:
  ```text
  web: gunicorn web_app:app --bind 0.0.0.0:$PORT
  ```
- **`.gitignore`**: Removed the rule ignoring `data/*.db` so that `restaurants.db` is tracked and available to Railway at runtime.

---

## 2. Frontend Modifications (Vercel)

The frontend is configured to be served statically by Vercel and point its API requests to the Railway backend.

- **`vercel.json`**: Created a Vercel configuration file to define how the static site is served, effectively treating the `templates` and `static` folders as a static project.
  ```json
  {
    "rewrites": [
      { "source": "/", "destination": "/templates/index.html" },
      { "source": "/(.*)", "destination": "/static/$1" }
    ]
  }
  ```
- **`static/js/app.js`**: Defined a `BACKEND_URL` variable. All `fetch()` calls (e.g., `fetch('/api/recommend')`) use the `BACKEND_URL`.

---

## Deployment Workflow

### Step 1: Deploy Backend to Railway
1. Go to [Railway.app](https://railway.app/).
2. Create a new project -> Deploy from GitHub repo -> Select `zomato-milestone-1`.
3. Add the `GROQ_API_KEY` to the Railway Environment Variables.
4. Once deployed, Railway will generate a public URL (e.g., `https://gastroai-backend.up.railway.app`).

### Step 2: Deploy Frontend to Vercel
1. Update `static/js/app.js` with the newly generated Railway URL:
   ```javascript
   const BACKEND_URL = 'https://gastroai-backend.up.railway.app';
   ```
2. Push the update to GitHub.
3. Go to [Vercel.com](https://vercel.com/).
4. Create a new project -> Import the `zomato-milestone-1` repository.
5. Vercel will automatically detect the static configuration and deploy the frontend.
6. (Optional) Update the CORS settings in `web_app.py` on Railway to explicitly only allow the generated Vercel domain.
