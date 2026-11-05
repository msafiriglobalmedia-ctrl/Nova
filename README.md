# NOVA Social — Prototype v0.1.0

An original, responsive social-platform starter inspired by the *overall product breadth* in the reference image. It does not reuse that image's name, logo, people, photographs, or branded assets.

## Included in this first build

- Animated NOVA launch screen with an original SVG logo and glowing orbit effects.
- Responsive desktop layout and Android-friendly mobile navigation.
- Home feed, stories preview, post composer, likes, and server-persisted posts.
- Explore, messages preview, communities, watch, marketplace, learning, AI Lab preview, projects, profile, and settings screens.
- Dark/light appearance toggle.
- FastAPI backend with SQLite starter database and basic health/posts endpoints.
- PWA manifest and service worker for installable app behaviour.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS/Termux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://127.0.0.1:8000` in a browser. On an Android phone, open the deployed HTTPS site in Chrome and use **Add to Home screen** / **Install app** when available.

## Deploy on Render (prototype)

1. Push this folder to a GitHub repository.
2. Create a new Render **Web Service** from that repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Health check path: `/api/health`

The default SQLite file is stored in `data/nova.db`. A standard Render filesystem can be ephemeral, so this prototype database may reset after redeploy/restart. Before real users or important data are added, move to managed PostgreSQL and configure backups.

## Important development status

This is a functional UI prototype, not yet a public-ready social network. The current API has no real registration/login, password handling, roles, moderation, private storage, encryption layer, or production anti-abuse controls. Messages, stories, video, marketplace checkout, AI responses, and course enrolment are front-end previews. Do not collect real users' private information or payments with this version.

## Suggested build order

1. Final product name, logo system, brand colours and screens.
2. PostgreSQL database, registration/login, profile and session security.
3. Follow system, posts, comments, media upload and notifications.
4. Real-time messaging, communities and moderation/reporting.
5. Video hosting, marketplace, learning and AI provider integration.
6. Privacy review, tests, backups, monitoring and production deployment.
