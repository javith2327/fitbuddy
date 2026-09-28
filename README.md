# FitBuddy — AI Fitness Plan Generator

FitBuddy is a FastAPI web application that uses Google's Gemini API to generate personalized 7-day workout plans, nutrition/recovery tips, and feedback-based plan revisions.

## Architecture

- Frontend: HTML + Jinja2 + responsive CSS
- Backend: FastAPI
- AI: Google Gemini through the current `google-genai` Python SDK
- Database: SQLite + SQLAlchemy ORM
- API: REST-style JSON endpoints plus the browser UI
- Testing: pytest + FastAPI TestClient

## Project structure

```text
fitbuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── routes.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   ├── workout_generator.py
│   │   ├── nutrition.py
│   │   └── plan_updater.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── result.html
│   │   ├── all_users.html
│   │   └── error.html
│   └── static/
│       └── style.css
├── tests/
│   └── test_app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 1. Install Python

Use Python 3.11 or newer.

Check:

```bash
python --version
```

## 2. Open the project in VS Code

Open the `fitbuddy` folder:

```bash
code .
```

## 3. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Create `.env` by copying `.env.example`.

### Windows

```powershell
copy .env.example .env
```

### macOS/Linux

```bash
cp .env.example .env
```

Put your Gemini API key into `.env`:

```env
GEMINI_API_KEY=YOUR_REAL_KEY
```

Do not commit `.env` to Git.

## 6. Start FitBuddy

From the project root:

```bash
uvicorn app.main:app --reload
```

Open:

- Website: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Admin/coach view: http://127.0.0.1:8000/view-all-users

## 7. Test the application

Run:

```bash
pytest -q
```

The included tests verify the home page, health endpoint, users endpoint, and FastAPI docs.

## 8. Test the complete AI flow

1. Open the home page.
2. Enter name, unique User ID, age, weight, goal and intensity.
3. Click **Generate My 7-Day Plan**.
4. Confirm that the result page shows seven days and a nutrition/recovery tip.
5. Enter feedback such as:
   `Add more cardio and make Day 4 a recovery day.`
6. Submit it.
7. Confirm the updated plan is displayed.
8. Open `/view-all-users` and verify both original and updated plans are stored.

## JSON API examples

### Generate

POST `/api/generate-workout`

```json
{
  "username": "Alex",
  "user_id": "FB001",
  "age": 21,
  "weight": 70,
  "goal": "muscle gain",
  "intensity": "medium"
}
```

### Feedback

POST `/api/submit-feedback`

```json
{
  "user_id": "FB001",
  "feedback": "Add more cardio and make Day 4 a recovery day."
}
```

### List users

GET `/api/users`

## Important notes

- The SQLite database file `fitbuddy.db` is created automatically when the server starts.
- The AI generation routes require a valid Gemini API key.
- The project deliberately uses the current Google Gen AI SDK (`google-genai`) instead of the older `google-generativeai` package described in older project documentation.
- The model names are environment variables so they can be changed without editing application code.
- The `/view-all-users` page is a local development admin/coach dashboard. For production, add authentication/authorization before exposing user data.
- Fitness and nutrition output is general educational guidance, not medical care.
