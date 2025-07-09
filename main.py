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
🤖 **Eslatma Bot**ga xush kelibsiz!

📋 **Bot qanday ishlaydi:**
• Siz menga vaqt va eslatma matnini yuborasiz
• Men belgilangan vaqtda sizga avtomatik eslatma yuboraman

🔧 **Mavjud buyruqlar:**
• `/remind 22:30 Kitob o'qishni unutmang` - yangi eslatma qo'shish
• `/list` - barcha aktiv eslatmalarni ko'rish
• `/cancel` - eslatmani o'chirish (ID bo'yicha)

⏰ **Vaqt formati:** HH:MM (masalan: 14:30, 09:15)

Eslatma qo'shish uchun `/remind` buyrug'idan foydalaning!
    """
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(Command("remind"))
async def remind_command(message: Message):
    """Handle /remind command"""
    try:
        # Parse the command: /remind HH:MM reminder_text
        command_parts = message.text.split(' ', 2)
        
        if len(command_parts) < 3:
            await message.answer(
                "❌ **Xato format!**\n\n"
                "To'g'ri format: `/remind 22:30 Eslatma matni`\n"
                "Masalan: `/remind 14:30 Dori ichishni unutmang`",
                parse_mode="Markdown"
            )
            return
        
        time_str = command_parts[1]
        reminder_text = command_parts[2]
        
        # Validate time format
        if not reminder_handler.validate_time_format(time_str):
            await message.answer(
                "❌ **Vaqt formati noto'g'ri!**\n\n"
                "To'g'ri format: HH:MM (24 soat formatida)\n"
                "Masalan: 09:30, 14:15, 22:00",
                parse_mode="Markdown"
            )
            return
        
        # Add reminder
        reminder_id = await reminder_handler.add_reminder(
            user_id=message.from_user.id,
            time_str=time_str,
            reminder_text=reminder_text
        )
        
        await message.answer(
            f"✅ **Eslatma muvaffaqiyatli qo'shildi!**\n\n"
            f"🆔 ID: `{reminder_id}`\n"
            f"⏰ Vaqt: `{time_str}`\n"
            f"📝 Matn: {reminder_text}\n\n"
            f"Men sizga har kuni soat {time_str}da eslatma yuboraman.",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in remind_command: {e}")
        await message.answer(
            "❌ **Xatolik yuz berdi!**\n\n"
            "Iltimos, qaytadan urinib ko'ring yoki admin bilan bog'laning."
        )

@dp.message(Command("list"))
async def list_command(message: Message):
    """Handle /list command"""
    try:
        reminders = await reminder_handler.get_user_reminders(message.from_user.id)
        
        if not reminders:
            await message.answer(
                "📭 **Sizda hozircha aktiv eslatmalar yo'q.**\n\n"
                "Yangi eslatma qo'shish uchun `/remind` buyrug'idan foydalaning."
            )
            return
        
        reminder_list = "📋 **Sizning aktiv eslatmalaringiz:**\n\n"
        
        for reminder in reminders:
            reminder_list += (
                f"🆔 ID: `{reminder['id']}`\n"
                f"⏰ Vaqt: `{reminder['time']}`\n"
                f"📝 Matn: {reminder['text']}\n"
                f"📅 Qo'shilgan: {reminder['created_at']}\n"
                f"{'─' * 30}\n"
            )
        
        reminder_list += f"\n💡 Eslatmani o'chirish uchun: `/cancel ID`"
        
        await message.answer(reminder_list, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in list_command: {e}")
        await message.answer(
            "❌ **Xatolik yuz berdi!**\n\n"
            "Eslatmalar ro'yxatini olishda muammo."
        )

@dp.message(Command("cancel"))
async def cancel_command(message: Message):
    """Handle /cancel command"""
    try:
        command_parts = message.text.split()
        
        if len(command_parts) != 2:
            await message.answer(
                "❌ **Xato format!**\n\n"
                "To'g'ri format: `/cancel ID`\n"
                "Masalan: `/cancel 123`\n\n"
                "Eslatma ID sini bilish uchun `/list` buyrug'idan foydalaning."
            )
            return
        
        try:
            reminder_id = int(command_parts[1])
        except ValueError:
            await message.answer(
                "❌ **ID raqam bo'lishi kerak!**\n\n"
                "Masalan: `/cancel 123`"
            )
            return
        
        success = await reminder_handler.cancel_reminder(
            user_id=message.from_user.id,
            reminder_id=reminder_id
        )
        
        if success:
            await message.answer(
                f"✅ **Eslatma muvaffaqiyatli o'chirildi!**\n\n"
                f"🆔 ID: `{reminder_id}`",
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                f"❌ **Eslatma topilmadi!**\n\n"
                f"ID `{reminder_id}` bo'yicha eslatma mavjud emas yoki u sizga tegishli emas.\n\n"
                f"Mavjud eslatmalarni ko'rish uchun `/list` buyrug'idan foydalaning.",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error in cancel_command: {e}")
        await message.answer(
            "❌ **Xatolik yuz berdi!**\n\n"
            "Eslatmani o'chirishda muammo."
        )

@dp.message()
async def handle_other_messages(message: Message):
    """Handle all other messages"""
    await message.answer(
        "🤔 **Tushunmadim...**\n\n"
        "Mavjud buyruqlar:\n"
        "• `/start` - bot haqida ma'lumot\n"
        "• `/remind 22:30 matn` - eslatma qo'shish\n"
        "• `/list` - eslatmalar ro'yxati\n"
        "• `/cancel ID` - eslatmani o'chirish"
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
