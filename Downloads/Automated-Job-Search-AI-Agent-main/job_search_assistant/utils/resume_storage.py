import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class ResumeStorage:
    """
    Handles persistence of resume analysis results using SQLite.
    Prevents data loss when switching tabs and provides history.
    """
    
    def __init__(self, db_path: str = "resumes.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create the resumes table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE,
                file_name TEXT,
                parsed_data TEXT,
                keyword_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_resume(self, file_hash: str, file_name: str, parsed_data: Dict, keyword_data: Optional[Dict] = None) -> bool:
        """
        Save a new resume or update existing one.
        
        Args:
            file_hash: Unique hash of the file content
            file_name: Original filename
            parsed_data: The JSON output from ResumeParser
            keyword_data: The JSON output from ResumeKeywordExtractor (optional)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert dicts to JSON strings
            parsed_json = json.dumps(parsed_data)
            keyword_json = json.dumps(keyword_data) if keyword_data else None

            cursor.execute('''
                INSERT INTO resumes (file_hash, file_name, parsed_data, keyword_data, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(file_hash) DO UPDATE SET
                    parsed_data=excluded.parsed_data,
                    keyword_data=excluded.keyword_data,
                    created_at=excluded.created_at
            ''', (file_hash, file_name, parsed_json, keyword_json, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving resume to DB: {e}")
            return False

    def get_resume(self, file_hash: str) -> Optional[Dict]:
        """Retrieve a specific resume by its content hash."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM resumes WHERE file_hash = ?', (file_hash,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "parsed_data": json.loads(row['parsed_data']),
                    "keyword_data": json.loads(row['keyword_data']) if row['keyword_data'] else None,
                    "file_name": row['file_name'],
                    "created_at": row['created_at']
                }
            return None
        except Exception as e:
            print(f"Error loading resume from DB: {e}")
            return None

    def get_all_resumes(self) -> List[Dict]:
        """Get list of all saved resumes for history view."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, file_name, file_hash, created_at FROM resumes ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()

            history = []
            for row in rows:
                history.append({
                    "id": row['id'],
                    "file_name": row['file_name'],
                    "file_hash": row['file_hash'],
                    "created_at": row['created_at']
                })
            return history
        except Exception as e:
            print(f"Error fetching resume history: {e}")
            return []
