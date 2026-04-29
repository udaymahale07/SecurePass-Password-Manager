import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="s_pass.db"):
        self.db_name = db_name  # Resolves relative to current working directory
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Establishes connection to the SQLite database."""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        # Return rows as dictionaries (e.g., row['username'])
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Creates the necessary tables if they don't exist."""
        # 1. Config Table: Stores system settings (Salt, Lockout Timers, etc.)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value BLOB
            )
        ''')

        # 2. Entries Table: Stores the encrypted password data.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT,
                username TEXT,
                ciphertext BLOB,
                nonce BLOB,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migration: Add context column if it does not exist
        try:
            self.cursor.execute('ALTER TABLE entries ADD COLUMN context TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Migration: Add category column if it does not exist
        try:
            self.cursor.execute('ALTER TABLE entries ADD COLUMN category TEXT DEFAULT "General"')
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Migration: Add updated_at column if it does not exist
        try:
            self.cursor.execute('ALTER TABLE entries ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        # 3. Breach Cache Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS breach_cache (
                prefix TEXT PRIMARY KEY,
                response TEXT,
                timestamp REAL
            )
        ''')
            
        self.conn.commit()

    # --- CONFIGURATION & SESSION HANDLING ---
    def set_config(self, key: str, value: bytes):
        """Sets or updates a configuration value in the database."""
        self.cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()

    def get_config(self, key: str) -> bytes:
        """Retrieves a configuration value from the database."""
        self.cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        result = self.cursor.fetchone()
        return result['value'] if result else None

    # --- MASTER AUTH HANDLING (Wrappers for Config) ---
    def save_salt(self, salt: bytes):
        self.set_config('master_salt', salt)

    def get_salt(self) -> bytes:
        return self.get_config('master_salt')

    def save_verifier(self, verifier: bytes):
        self.set_config('master_verifier', verifier)

    def get_verifier(self) -> bytes:
        return self.get_config('master_verifier')

    # --- PASSWORD ENTRY HANDLING ---
    def add_entry(self, website: str, username: str, ciphertext: bytes, nonce: bytes, context: str = "", category: str = "General"):
        """Saves a new encrypted entry to the vault."""
        try:
            self.cursor.execute('''
                INSERT INTO entries (website, username, ciphertext, nonce, context, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (website, username, ciphertext, nonce, context, category))
        except Exception:
            self.cursor.execute('''
                INSERT INTO entries (website, username, ciphertext, nonce, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (website, username, ciphertext, nonce, context))
        self.conn.commit()

    def get_all_entries(self):
        """Retrieves all encrypted entries ordered by website name."""
        self.cursor.execute('SELECT * FROM entries ORDER BY website COLLATE NOCASE')
        return self.cursor.fetchall()

    def get_entries_by_category(self, category: str):
        """Retrieves all entries for a specific category."""
        self.cursor.execute('SELECT * FROM entries WHERE category = ? ORDER BY website COLLATE NOCASE', (category,))
        return self.cursor.fetchall()

    def get_all_categories(self):
        """Returns a sorted list of all distinct categories in use."""
        try:
            self.cursor.execute('SELECT DISTINCT category FROM entries WHERE category IS NOT NULL ORDER BY category COLLATE NOCASE')
            rows = self.cursor.fetchall()
            return [r['category'] for r in rows if r['category']]
        except Exception:
            return ["General"]

    def get_entries_paginated(self, limit: int, offset: int):
        self.cursor.execute('SELECT * FROM entries ORDER BY website COLLATE NOCASE LIMIT ? OFFSET ?', (limit, offset))
        return self.cursor.fetchall()

    def count_entries(self) -> int:
        self.cursor.execute('SELECT COUNT(*) as cnt FROM entries')
        row = self.cursor.fetchone()
        return row['cnt'] if row else 0

    def delete_entry(self, entry_id: int):
        """Deletes a specific entry by its ID."""
        self.cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        self.conn.commit()

    def update_entry(self, entry_id: int, website: str, username: str,
                     ciphertext: bytes, nonce: bytes, context: str = "", category: str = "General"):
        """Updates an existing encrypted entry in-place, preserving its ID."""
        # Try to update with category; fall back if column doesn't exist yet
        try:
            self.cursor.execute('''
                UPDATE entries
                SET website=?, username=?, ciphertext=?, nonce=?, context=?, category=?
                WHERE id=?
            ''', (website, username, ciphertext, nonce, context, category, entry_id))
        except Exception:
            # Fallback: category column may not exist yet (migration pending)
            self.cursor.execute('''
                UPDATE entries
                SET website=?, username=?, ciphertext=?, nonce=?, context=?
                WHERE id=?
            ''', (website, username, ciphertext, nonce, context, entry_id))
        self.conn.commit()

    # --- BREACH CACHE HANDLING ---
    def set_breach_cache(self, prefix: str, response: str, timestamp: float):
        self.cursor.execute('INSERT OR REPLACE INTO breach_cache (prefix, response, timestamp) VALUES (?, ?, ?)', (prefix, response, timestamp))
        self.conn.commit()

    def get_breach_cache(self, prefix: str):
        self.cursor.execute('SELECT response, timestamp FROM breach_cache WHERE prefix = ?', (prefix,))
        return self.cursor.fetchone()

    def close(self):
        if self.conn:
            self.conn.close()
