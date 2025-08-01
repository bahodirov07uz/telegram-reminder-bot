import asyncio
import logging
from datetime import datetime, time
from typing import List, Dict, Optional
from aiogram import Bot
from db_handler import DatabaseHandler

logger = logging.getLogger(__name__)

class ReminderHandler:
    """Handles reminder storage, scheduling, and delivery"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = DatabaseHandler()

    
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
        return self.db.add_reminder(user_id, time_str, reminder_text)
    
    async def get_user_reminders(self, user_id: int) -> List[Dict]:
        """Get all active reminders for a user"""
        return self.db.get_user_reminders(user_id)
    
    async def cancel_reminder(self, user_id: int, reminder_id: int) -> bool:
        """Cancel a reminder by ID"""
        return self.db.cancel_reminder(user_id, reminder_id)
    
    async def get_due_reminders(self) -> List[Dict]:
        """Get reminders that are due at the current time"""
        return self.db.get_due_reminders()
    
    async def send_reminder(self, reminder: Dict):
        """Send a reminder to the user"""
        try:
            message = f"🔔 **Напоминание:** {reminder['text']}"
            await self.bot.send_message(
                chat_id=reminder["user_id"],
                text=message,
                parse_mode="Markdown"
            )
            logger.info(f"Sent reminder {reminder['id']} to user {reminder['user_id']}")
            
            # Mark reminder as sent in database
            self.db.mark_reminder_sent(reminder["id"])
            
        except Exception as e:
            logger.error(f"Error sending reminder {reminder['id']} to user {reminder['user_id']}: {e}")
    
    async def check_and_send_reminders(self):
        """Check for due reminders and send them"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            due_reminders = await self.get_due_reminders()
            
            logger.info(f"Checking reminders at {current_time}")
            
            if due_reminders:
                logger.info(f"Found {len(due_reminders)} due reminders")
                
                for reminder in due_reminders:
                    await self.send_reminder(reminder)
            else:
                # Log active reminders for debugging
                active_reminders = self.db.get_all_active_reminders()
                logger.info(f"No due reminders. Active reminders: {len(active_reminders)}")
                if active_reminders:
                    for r in active_reminders:
                        logger.info(f"Active reminder: ID={r['id']}, time={r['time']}, current={current_time}")
                    
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
        return self.db.get_stats()
