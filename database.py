import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

# Get the URL from Render (or use None if not set)
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    if not DATABASE_URL:
        print("rror: DATABASE_URL is missing! Add it to Render Environment Variables.")
        return None
        
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        return None

def init_db():
    """Creates the table if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Postgres Syntax: SERIAL is auto-increment, TEXT is standard
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    discord_id TEXT PRIMARY KEY,
                    refresh_token TEXT,
                    email TEXT,
                    timezone TEXT DEFAULT 'UTC'
                );
            ''')
            conn.commit()
            print("✅ Database initialized (Table 'users' is ready).")
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        conn.close()

def save_user_token(discord_id, refresh_token, email=None):
    """
    Saves or updates a user. 
    Uses Postgres 'ON CONFLICT' syntax (Upsert).
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Postgres uses %s for placeholders, NOT ?
            query = '''
                INSERT INTO users (discord_id, refresh_token, email)
                VALUES (%s, %s, %s)
                ON CONFLICT (discord_id) 
                DO UPDATE SET 
                    refresh_token = EXCLUDED.refresh_token,
                    email = COALESCE(EXCLUDED.email, users.email);
            '''
            cur.execute(query, (str(discord_id), refresh_token, email))
            conn.commit()
            print(f"User {discord_id} saved/updated successfully.")
    except Exception as e:
        print(f"Error saving user: {e}")
    finally:
        conn.close()

def get_user_data(discord_id):
    """Retrieves user data as a dictionary."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE discord_id = %s', (str(discord_id),))
            user = cur.fetchone()
            # RealDictCursor automatically returns a dictionary-like object
            return user 
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        conn.close()

# --- Initialization ---
if __name__ == "__main__":
    init_db()