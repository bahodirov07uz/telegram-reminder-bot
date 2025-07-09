import asyncio
import json
import os
import logging
from datetime import datetime, time
from typing import List, Dict, Optional
from aiogram import Bot

logger = logging.getLogger(__name__)

class ReminderHandler:
    """Handles reminder storage, scheduling, and delivery"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.storage_file = "storage.json"
        self.reminders = self.load_reminders()
        self.next_id = self.get_next_id()
        
    def load_reminders(self) -> Dict:
        """Load reminders from JSON file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"reminders": []}
        except Exception as e:
            logger.error(f"Error loading reminders: {e}")
            return {"reminders": []}
    
    def save_reminders(self):
        """Save reminders to JSON file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving reminders: {e}")
    
    def get_next_id(self) -> int:
        """Get the next available ID for reminders"""
        if not self.reminders["reminders"]:
            return 1
        return max(reminder["id"] for reminder in self.reminders["reminders"]) + 1
    
    def validate_time_format(self, time_str: str) -> bool:
        """Validate time format HH:MM"""
        try:
            time_parts = time_str.split(':')
            if len(time_parts) != 2:
                return False
            
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            
            # Validate ranges
            if not (0 <= hours <= 23):
                return False
            if not (0 <= minutes <= 59):
                return False
            
            return True
        except (ValueError, IndexError):
            return False
    
    async def add_reminder(self, user_id: int, time_str: str, reminder_text: str) -> int:
        """Add a new reminder"""
        reminder = {
            "id": self.next_id,
            "user_id": user_id,
            "time": time_str,
            "text": reminder_text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "active": True
        }
        
        self.reminders["reminders"].append(reminder)
        self.next_id += 1
        self.save_reminders()
        
        logger.info(f"Added reminder {reminder['id']} for user {user_id}")
        return reminder["id"]
    
    async def get_user_reminders(self, user_id: int) -> List[Dict]:
        """Get all active reminders for a user"""
        return [
            reminder for reminder in self.reminders["reminders"]
            if reminder["user_id"] == user_id and reminder["active"]
        ]
    
    async def cancel_reminder(self, user_id: int, reminder_id: int) -> bool:
        """Cancel a reminder by ID"""
        for reminder in self.reminders["reminders"]:
            if (reminder["id"] == reminder_id and 
                reminder["user_id"] == user_id and 
                reminder["active"]):
                
                reminder["active"] = False
                self.save_reminders()
                logger.info(f"Cancelled reminder {reminder_id} for user {user_id}")
                return True
        
        return False
    
    async def get_due_reminders(self) -> List[Dict]:
        """Get reminders that are due at the current time"""
        current_time = datetime.now().strftime("%H:%M")
        
        due_reminders = []
        for reminder in self.reminders["reminders"]:
            if reminder["active"] and reminder["time"] == current_time:
                due_reminders.append(reminder)
        
        return due_reminders
    
    async def send_reminder(self, reminder: Dict):
        """Send a reminder to the user"""
        try:
            message = f"🔔 **Eslatma:** {reminder['text']}"
            await self.bot.send_message(
                chat_id=reminder["user_id"],
                text=message,
                parse_mode="Markdown"
            )
            logger.info(f"Sent reminder {reminder['id']} to user {reminder['user_id']}")
            
        except Exception as e:
            logger.error(f"Error sending reminder {reminder['id']} to user {reminder['user_id']}: {e}")
    
    async def check_and_send_reminders(self):
        """Check for due reminders and send them"""
        try:
            due_reminders = await self.get_due_reminders()
            
            if due_reminders:
                logger.info(f"Found {len(due_reminders)} due reminders")
                
                for reminder in due_reminders:
                    await self.send_reminder(reminder)
                    
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")
    
    async def start_reminder_checker(self):
        """Start the background task to check reminders every minute"""
        logger.info("Eslatma tekshiruvchi ishga tushdi...")
        
        while True:
            try:
                await self.check_and_send_reminders()
                
                # Wait until the next minute
                current_time = datetime.now()
                seconds_to_wait = 60 - current_time.second
                await asyncio.sleep(seconds_to_wait)
                
            except Exception as e:
                logger.error(f"Error in reminder checker: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def get_stats(self) -> Dict:
        """Get statistics about reminders"""
        active_reminders = [r for r in self.reminders["reminders"] if r["active"]]
        total_users = len(set(r["user_id"] for r in active_reminders))
        
        return {
            "total_reminders": len(self.reminders["reminders"]),
            "active_reminders": len(active_reminders),
            "total_users": total_users
        }
