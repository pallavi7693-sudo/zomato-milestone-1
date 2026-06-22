# GastroAI Deployment Plan (Next.js on Vercel + API on Railway/Render)

This plan outlines the steps to deploy the application. It consists of a modern Next.js frontend and a Flask REST API backend.

## 1. Backend Modifications (Railway / Render)
The Flask application is prepared for production:
- **`requirements.txt`**: Includes `gunicorn` and `flask-cors`.
- **`web_app.py`**: Handles API routes (`/api/...`) and configures CORS.
- **Database**: The SQLite database (`data/restaurants.db`) is committed to the repo, so it is deployed along with the backend. Since the app only reads from the DB, the ephemeral filesystem of Railway/Render is perfectly fine.
- **Procfile**: Tells the hosting provider how to run the app:
  ```text
  web: gunicorn web_app:app --bind 0.0.0.0:$PORT
  ```

### Backend Deployment Steps
1. Deploy the root of this repository to Railway or Render.
2. Ensure you add `GROQ_API_KEY` to the environment variables on the hosting provider.
3. Note your generated backend URL (e.g., `https://gastroai-backend.onrender.com`).

---

## 2. Frontend Modifications (Next.js on Vercel)
The new frontend is built using Next.js 14 and is located in the `frontend-nextjs` directory.

### CRITICAL: Fixing Vercel Configuration
If you previously deployed the app and the frontend was broken or looked like the old static site, it's because Vercel was trying to deploy the old HTML files instead of the Next.js app! 

To deploy the Next.js app correctly, follow these exact steps in your Vercel Dashboard:

1. **Delete the old `vercel.json` file** from the root of your GitHub repository (I have already removed it for you locally, just commit the change). The old `vercel.json` was forcing Vercel to serve the old static HTML site.
2. Go to your project on Vercel -> **Settings** -> **General**.
3. Scroll down to **Root Directory** and click **Edit**.
4. Type `frontend-nextjs` and click Save. 
5. Scroll down to **Environment Variables**.
6. Add a new variable:
   - **Key**: `NEXT_PUBLIC_BACKEND_URL`
   - **Value**: Your backend URL from step 1 (e.g., `https://gastroai-backend.onrender.com`). Do not include a trailing slash.
7. Go to the **Deployments** tab and click **Redeploy** on your latest commit.

Vercel will now correctly detect Next.js, run `npm run build`, and serve your beautiful new React frontend!
