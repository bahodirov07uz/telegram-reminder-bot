import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F
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
🤖 **Добро пожаловать в Бот Напоминаний!**

📋 **Как работает бот:**
• Вы отправляете мне время и текст напоминания
• Я автоматически отправлю вам напоминание в указанное время

🔧 **Доступные команды:**
• `/remind 22:30 Не забыть прочитать книгу` - добавить напоминание
• `/list` - показать все активные напоминания
• `/cancel` - удалить напоминание (по ID)

⏰ **Формат времени:** ЧЧ:ММ (например: 14:30, 09:15)

Используйте `/remind` для добавления напоминания!
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
                "❌ **Неверный формат!**\n"
                "Используйте: `/remind 22:30 Текст напоминания`",
                parse_mode="Markdown"
            )
            return
        
        time_str = command_parts[1]
        reminder_text = command_parts[2]
        
        # Validate time format
        if not reminder_handler.validate_time_format(time_str):
            await message.reply(
                "❌ **Неверный формат времени!**\n"
                "Используйте: ЧЧ:ММ (например: 09:30, 14:15, 22:00)",
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
            f"✅ **Напоминание добавлено!**\n"
            f"🆔 ID: `{reminder_id}`\n"
            f"⏰ Время: `{time_str}`\n"
            f"📝 {reminder_text}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in remind_command: {e}")
        await message.answer(
            "❌ **Произошла ошибка!**\n\n"
            "Пожалуйста, попробуйте снова или обратитесь к администратору."
        )

@dp.message(Command("list"))
async def list_command(message: Message):
    """Handle /list command"""
    try:
        reminders = await reminder_handler.get_user_reminders(message.from_user.id)
        
        if not reminders:
            await message.answer(
                "📭 **У вас пока нет активных напоминаний.**\n\n"
                "Используйте команду `/remind` для добавления нового напоминания."
            )
            return
        
        reminder_list = "📋 **Ваши активные напоминания:**\n\n"
        
        for reminder in reminders:
            reminder_list += (
                f"🆔 ID: `{reminder['id']}`\n"
                f"⏰ Время: `{reminder['time']}`\n"
                f"📝 Текст: {reminder['text']}\n"
                f"📅 Добавлено: {reminder['created_at']}\n"
                f"{'─' * 30}\n"
            )
        
        reminder_list += f"\n💡 Для удаления напоминания: `/cancel ID`"
        
        await message.reply(reminder_list, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in list_command: {e}")
        await message.answer(
            "❌ **Произошла ошибка!**\n\n"
            "Проблема при получении списка напоминаний."
        )

@dp.message(Command("cancel"))
async def cancel_command(message: Message):
    """Handle /cancel command"""
    try:
        command_parts = message.text.split()
        
        if len(command_parts) != 2:
            await message.answer(
                "❌ **Неверный формат!**\n\n"
                "Правильный формат: `/cancel ID`\n"
                "Например: `/cancel 123`\n\n"
                "Используйте `/list` для просмотра ID напоминаний."
            )
            return
        
        try:
            reminder_id = int(command_parts[1])
        except ValueError:
            await message.answer(
                "❌ **ID должен быть числом!**\n\n"
                "Например: `/cancel 123`"
            )
            return
        
        success = await reminder_handler.cancel_reminder(
            user_id=message.from_user.id,
            reminder_id=reminder_id
        )
        
        if success:
            await message.reply(
                f"✅ **Напоминание удалено!**\n"
                f"🆔 ID: `{reminder_id}`",
                parse_mode="Markdown"
            )
        else:
            await message.reply(
                f"❌ **Напоминание не найдено!**\n"
                f"ID `{reminder_id}` не существует. Используйте `/list`",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error in cancel_command: {e}")
        await message.answer(
            "❌ **Произошла ошибка!**\n\n"
            "Проблема при удалении напоминания."
        )

@dp.message()
async def handle_other_messages(message: Message):
    """Handle all other messages"""
    await message.reply(
        "🤔 **Не понимаю...**\n\n"
        "Доступные команды:\n"
        "• `/start` - информация о боте\n"
        "• `/remind 22:30 текст` - добавить напоминание\n"
        "• `/list` - список напоминаний\n"
        "• `/cancel ID` - удалить напоминание"
    )

async def main():
    """Main function to run the bot"""
    try:
        logger.info("Bot ishga tushmoqda...")
        
        # Start the reminder checker task
        asyncio.create_task(reminder_handler.start_reminder_checker())
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Bot ishga tushishda xatolik: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
