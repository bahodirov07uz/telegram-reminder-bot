import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseHandler:
    """Handles SQLite database operations for reminders"""
    
    def __init__(self, db_path: str = "reminders.db"):
        self.db_path = db_path
        self.init_database()
        self.migrate_from_json()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create reminders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    time TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_sent DATE,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_active 
                ON reminders(user_id, active)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_time_active 
                ON reminders(time, active)
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def migrate_from_json(self):
        """Migrate existing data from JSON file to SQLite"""
        json_file = "storage.json"
        
        if not os.path.exists(json_file):
            logger.info("No JSON file found, skipping migration")
            return
        
        # Check if migration already done
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM reminders")
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.info("Database already contains data, skipping migration")
                return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for reminder in data.get("reminders", []):
                    cursor.execute('''
                        INSERT INTO reminders (user_id, time, text, created_at, last_sent, active)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        reminder["user_id"],
                        reminder["time"],
                        reminder["text"],
                        reminder["created_at"],
                        reminder.get("last_sent"),
                        reminder["active"]
                    ))
                
                conn.commit()
                logger.info(f"Migrated {len(data.get('reminders', []))} reminders from JSON to SQLite")
            
            # Backup and remove JSON file
            backup_name = f"storage_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.rename(json_file, backup_name)
            logger.info(f"JSON file backed up as {backup_name}")
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
    
    def add_reminder(self, user_id: int, time_str: str, reminder_text: str) -> int:
        """Add a new reminder"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO reminders (user_id, time, text)
                VALUES (?, ?, ?)
            ''', (user_id, time_str, reminder_text))
            
            reminder_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Added reminder {reminder_id} for user {user_id}")
            return reminder_id
    
    def get_user_reminders(self, user_id: int) -> List[Dict]:
        """Get all active reminders for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, time, text, created_at, last_sent, active
                FROM reminders
                WHERE user_id = ? AND active = TRUE
                ORDER BY time
            ''', (user_id,))
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    "id": row[0],
                    "user_id": row[1],
                    "time": row[2],
                    "text": row[3],
                    "created_at": row[4],
                    "last_sent": row[5],
                    "active": row[6]
                })
            
            return reminders
    
    def cancel_reminder(self, user_id: int, reminder_id: int) -> bool:
        """Cancel a reminder by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE reminders 
                SET active = FALSE 
                WHERE id = ? AND user_id = ? AND active = TRUE
            ''', (reminder_id, user_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                logger.info(f"Cancelled reminder {reminder_id} for user {user_id}")
            
            return success
    
    def get_due_reminders(self) -> List[Dict]:
        """Get reminders that are due at the current time"""
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, time, text, created_at, last_sent, active
                FROM reminders
                WHERE active = TRUE 
                AND time = ? 
                AND (last_sent IS NULL OR last_sent != ?)
            ''', (current_time, current_date))
            
            due_reminders = []
            for row in cursor.fetchall():
                due_reminders.append({
                    "id": row[0],
                    "user_id": row[1],
                    "time": row[2],
                    "text": row[3],
                    "created_at": row[4],
                    "last_sent": row[5],
                    "active": row[6]
                })
            
            return due_reminders
    
    def mark_reminder_sent(self, reminder_id: int):
        """Mark a reminder as sent for today"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE reminders 
                SET last_sent = ? 
                WHERE id = ?
            ''', (current_date, reminder_id))
            
            conn.commit()
            logger.info(f"Marked reminder {reminder_id} as sent for {current_date}")
    
    def get_stats(self) -> Dict:
        """Get statistics about reminders"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total reminders
            cursor.execute("SELECT COUNT(*) FROM reminders")
            total_reminders = cursor.fetchone()[0]
            
            # Active reminders
            cursor.execute("SELECT COUNT(*) FROM reminders WHERE active = TRUE")
            active_reminders = cursor.fetchone()[0]
            
            # Total users
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM reminders WHERE active = TRUE")
            total_users = cursor.fetchone()[0]
            
            return {
                "total_reminders": total_reminders,
                "active_reminders": active_reminders,
                "total_users": total_users
            }
    
    def get_all_active_reminders(self) -> List[Dict]:
        """Get all active reminders for debugging"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, time, text, created_at, last_sent, active
                FROM reminders
                WHERE active = TRUE
                ORDER BY time
            ''')
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    "id": row[0],
                    "user_id": row[1],
                    "time": row[2],
                    "text": row[3],
                    "created_at": row[4],
                    "last_sent": row[5],
                    "active": row[6]
                })
            
            return reminders