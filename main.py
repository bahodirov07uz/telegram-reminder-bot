import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from reminder_handler import ReminderHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Initialize reminder handler
reminder_handler = ReminderHandler(bot)

@dp.message(Command("start"))
async def start_command(message: Message):
    """Handle /start command"""
    welcome_text = """
🤖 **Welcome to the Reminder Bot!**

📋 **How this bot works:**
• Send me a time and reminder text
• I will automatically send you the reminder at the specified time

🔧 **Available commands:**
• `/remind 22:30 Don't forget to read a book` - add a reminder
• `/list` - show all active reminders
• `/cancel` - delete a reminder by ID

⏰ **Time format:** HH:MM (e.g., 14:30, 09:15)

Use `/remind` to add a new reminder!
    """
    await message.reply(welcome_text, parse_mode="Markdown")

@dp.message(Command("remind"))
async def remind_command(message: Message):
    """Handle /remind command"""
    try:
        # Parse the command: /remind HH:MM reminder_text
        command_parts = message.text.split(' ', 2)
        
        if len(command_parts) < 3:
            await message.reply(
                "❌ **Invalid format!**\n"
                "Use: `/remind 22:30 Reminder text here`",
                parse_mode="Markdown"
            )
            return
        
        time_str = command_parts[1]
        reminder_text = command_parts[2]
        
        # Validate time format
        if not reminder_handler.validate_time_format(time_str):
            await message.reply(
                "❌ **Invalid time format!**\n"
                "Use: HH:MM (e.g., 09:30, 14:15, 22:00)",
                parse_mode="Markdown"
            )
            return
        
        # Add reminder
        reminder_id = await reminder_handler.add_reminder(
            user_id=message.from_user.id,
            time_str=time_str,
            reminder_text=reminder_text
        )
        
        await message.reply(
            f"✅ **Reminder added!**\n"
            f"🆔 ID: `{reminder_id}`\n"
            f"⏰ Time: `{time_str}`\n"
            f"📝 {reminder_text}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in remind_command: {e}")
        await message.answer(
            "❌ **An error occurred!**\n\n"
            "Please try again or contact the administrator."
        )

@dp.message(Command("list"))
async def list_command(message: Message):
    """Handle /list command"""
    try:
        reminders = await reminder_handler.get_user_reminders(message.from_user.id)
        
        if not reminders:
            await message.answer(
                "📭 **You have no active reminders.**\n\n"
                "Use `/remind` to add a new reminder."
            )
            return
        
        reminder_list = "📋 **Your active reminders:**\n\n"
        
        for reminder in reminders:
            reminder_list += (
                f"🆔 ID: `{reminder['id']}`\n"
                f"⏰ Time: `{reminder['time']}`\n"
                f"📝 Text: {reminder['text']}\n"
                f"📅 Added: {reminder['created_at']}\n"
                f"{'─' * 30}\n"
            )
        
        reminder_list += f"\n💡 To delete a reminder: `/cancel ID`"
        
        await message.reply(reminder_list, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in list_command: {e}")
        await message.answer(
            "❌ **An error occurred!**\n\n"
            "There was a problem retrieving your reminders."
        )

@dp.message(Command("cancel"))
async def cancel_command(message: Message):
    """Handle /cancel command"""
    try:
        command_parts = message.text.split()
        
        if len(command_parts) != 2:
            await message.answer(
                "❌ **Invalid format!**\n\n"
                "Correct format: `/cancel ID`\n"
                "Example: `/cancel 123`\n\n"
                "Use `/list` to see reminder IDs."
            )
            return
        
        try:
            reminder_id = int(command_parts[1])
        except ValueError:
            await message.answer(
                "❌ **ID must be a number!**\n\n"
                "Example: `/cancel 123`"
            )
            return
        
        success = await reminder_handler.cancel_reminder(
            user_id=message.from_user.id,
            reminder_id=reminder_id
        )
        
        if success:
            await message.reply(
                f"✅ **Reminder deleted!**\n"
                f"🆔 ID: `{reminder_id}`",
                parse_mode="Markdown"
            )
        else:
            await message.reply(
                f"❌ **Reminder not found!**\n"
                f"ID `{reminder_id}` does not exist. Use `/list`",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error in cancel_command: {e}")
        await message.answer(
            "❌ **An error occurred!**\n\n"
            "There was a problem deleting the reminder."
        )

@dp.message()
async def handle_other_messages(message: Message):
    """Handle all other messages"""
    await message.reply(
        "🤔 **I don't understand...**\n\n"
        "Available commands:\n"
        "• `/start` - bot information\n"
        "• `/remind 22:30 text` - add a reminder\n"
        "• `/list` - list your reminders\n"
        "• `/cancel ID` - delete a reminder"
    )

async def main():
    """Main function to run the bot"""
    try:
        logger.info("Bot is starting...")
        
        # Start the reminder checker task
        asyncio.create_task(reminder_handler.start_reminder_checker())
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error while starting bot: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
