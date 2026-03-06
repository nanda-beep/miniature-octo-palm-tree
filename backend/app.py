import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database connection configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'quiz_db')
DB_USER = os.getenv('DB_USER', 'quiz_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'quiz_password')


def get_db_connection():
    """Create and return a database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


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


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/quiz/start', methods=['POST'])
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
            return jsonify({'error': 'Nickname is required'}), 400
        
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
        
        return jsonify({
            'nickname': result['nickname'],
            'quiz_starts': result['quiz_starts']
        }), 200
    
    except Exception as e:
        print(f"Error in /api/quiz/start: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/quiz/stats/<nickname>', methods=['GET'])
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
            return jsonify({
                'nickname': result['nickname'],
                'quiz_starts': result['quiz_starts']
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    
    except Exception as e:
        print(f"Error in /api/quiz/stats: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
