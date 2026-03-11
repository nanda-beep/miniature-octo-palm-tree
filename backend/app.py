import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuizStartRequest(BaseModel):
    nickname: str

def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL is not set")
    return psycopg2.connect(database_url)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                nickname VARCHAR(255) UNIQUE NOT NULL,
                quiz_starts INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/quiz/start")
def start_quiz(payload: QuizStartRequest):
    nickname = payload.nickname.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="Nickname is required")

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            INSERT INTO users (nickname, quiz_starts, created_at, updated_at)
            VALUES (%s, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (nickname) DO UPDATE
            SET quiz_starts = users.quiz_starts + 1,
                updated_at = CURRENT_TIMESTAMP
            RETURNING nickname, quiz_starts
        """, (nickname,))

        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return {
            "nickname": result["nickname"],
            "quiz_starts": result["quiz_starts"]
        }

    except Exception as e:
        print(f"Error in /api/quiz/start: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quiz/stats/{nickname}")
def get_user_stats(nickname: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT nickname, quiz_starts
            FROM users
            WHERE nickname = %s
        """, (nickname,))

        result = cur.fetchone()
        cur.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "nickname": result["nickname"],
            "quiz_starts": result["quiz_starts"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /api/quiz/stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
