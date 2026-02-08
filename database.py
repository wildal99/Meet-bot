import sqlite3
import os

DB_NAME = "meetbot.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # This allows us to access columns by name (row['email'])
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            refresh_token TEXT,
            email TEXT
            timezone TEXT DEFAULT 'UTC'
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"{DB_NAME}' initialized successfully.")

def save_user_token(discord_id, refresh_token, email=None):
    """
    Saves or updates a user's refresh token.
    UPSERT logic: If the user exists, update them. If not, insert them.
    """
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO users (discord_id, refresh_token, email)
            VALUES (?, ?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET
                refresh_token=excluded.refresh_token,
                email=COALESCE(excluded.email, users.email)
        ''', (str(discord_id), refresh_token, email))
        conn.commit()
        print(f"User {discord_id} saved/updated.")
    except Exception as e:
        print(f"Error saving user: {e}")
    finally:
        conn.close()

def get_user_data(discord_id):
    """
    Retrieves a user's data (token, email, timezone).
    Returns a dictionary or None.
    """
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE discord_id = ?', (str(discord_id),))
    row = c.fetchone()
    conn.close()
    
    if row:
        return dict(row) # Convert sqlite3.Row to a standard Python dict
    return None

def get_user_token(discord_user_id):
    """
    Returns the token info if user exists, or None if they don't.
    """
    conn = sqlite3.connect('meetbot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE discord_id=?", (discord_user_id,))
    data = c.fetchone()
    conn.close()
    return data # Returns None if no user found

# Run initialization immediately when this file is imported
# This ensures the DB file exists before we try to use it
if __name__ == "__main__":
    # If you run 'python database.py' directly, it will init and show data
    init_db()
else:
    init_db() # If imported, just ensure the table exists