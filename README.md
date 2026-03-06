# Thai Consonant Quiz Application

A web-based quiz application for learning Thai consonants with a backend service that tracks user progress.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose (or PostgreSQL installed locally)
- Python 3.7+
- Git

### Step 1: Start PostgreSQL Database

Using Docker Compose (recommended):
```bash
docker-compose up -d
```

Or if using a local PostgreSQL installation, ensure it's running on localhost:5432 with the credentials:
- Database: `quiz_db`
- User: `quiz_user`
- Password: `quiz_password`

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Start the Backend Service

```bash
python app.py
```

The API will be available at `http://localhost:5000`

The server will automatically initialize the database schema on startup.

### Step 4: Open the Application

Open `index.html` in your web browser, or serve it with a simple HTTP server:

```bash
python -m http.server 8000
```

Then navigate to `http://localhost:8000`

## API Endpoints

### `POST /api/quiz/start`
Increments the quiz start counter for a user.

**Request:**
```json
{
  "nickname": "PlayerName"
}
```

**Response:**
```json
{
  "nickname": "PlayerName",
  "quiz_starts": 5
}
```

### `GET /api/quiz/stats/<nickname>`
Retrieves quiz statistics for a user.

**Response:**
```json
{
  "nickname": "PlayerName",
  "quiz_starts": 5
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Features

- Track Thai consonant learning with 44 consonants
- User nickname support
- Quiz start counter persisted in PostgreSQL database
- Display quiz start count on the quiz screen
- 3-life system with feedback on answers
- Progress counter for consonants learned

## Database Schema

The application uses a single `users` table:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(255) UNIQUE NOT NULL,
    quiz_starts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Stopping the Application

To stop the PostgreSQL database:
```bash
docker-compose down
```

To remove all data and stop the database:
```bash
docker-compose down -v
```

## Troubleshooting

**Connection refused error:** Ensure PostgreSQL is running on port 5432 and the credentials match the configuration in `app.py`.

**API not responding:** Make sure the Flask backend is running with `python app.py`.

**CORS errors:** The Flask app has CORS enabled for all origins. Ensure the API URL in `index.html` matches your backend URL.
