import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'quiz_db')
DB_USER = os.getenv('DB_USER', 'quiz_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'quiz_password')


def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))


def init_db():
    """Initialize the database with required tables"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create users table if it doesn't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                nickname VARCHAR(255) UNIQUE NOT NULL,
                quiz_starts INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"})


@app.post("/api/quiz/start")
def start_quiz():
    """
    Increment the quiz start counter for a user
    Expected JSON: { "nickname": "PlayerName" }
    Returns: { "quiz_starts": 5, "nickname": "PlayerName" }
    """
    try:
        data = request.get_json()
        nickname = data.get('nickname', '').strip()
        
        if not nickname:
            return {'error': 'Nickname is required'}, 400
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Try to update existing user, if not found, insert new user
        cur.execute('''
            INSERT INTO users (nickname, quiz_starts, created_at, updated_at)
            VALUES (%s, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (nickname) DO UPDATE
            SET quiz_starts = quiz_starts + 1, updated_at = CURRENT_TIMESTAMP
            RETURNING nickname, quiz_starts
        ''', (nickname,))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'nickname': result['nickname'],
            'quiz_starts': result['quiz_starts']
        }, 200
    
    except Exception as e:
        print(f"Error in /api/quiz/start: {e}")
        return {'error': str(e)}, 500


@app.get("/api/quiz/stats/{nickname}")
def get_user_stats(nickname):
    """
    Get quiz statistics for a user
    Returns: { "nickname": "PlayerName", "quiz_starts": 5 }
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            SELECT nickname, quiz_starts FROM users WHERE nickname = %s
        ''', (nickname,))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            return {
                'nickname': result['nickname'],
                'quiz_starts': result['quiz_starts']
            }, 200
        else:
            return {'error': 'User not found'}, 404
    
    except Exception as e:
        print(f"Error in /api/quiz/stats: {e}")
        return {'error': str(e)}, 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
