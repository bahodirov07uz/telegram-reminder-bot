# ⏰ tele-reminder-bot

> A modular and efficient Telegram bot built with Python + aiogram to help users schedule and receive time-based reminders. Now powered by SQLite for persistent storage and scalable performance.

---

## 🧭 Overview

**tele-reminder-bot** is a Telegram bot that lets users schedule personal reminders using simple commands. It supports time-based notifications and ensures persistence with SQLite storage.

- Built with **Python** and **aiogram**
- Asynchronous, event-driven architecture
- Persistent data storage with **SQLite**
- Clear, short commands and messages (in **Russian** for fast comprehension)

---

## 🌐 User Preferences

- 🗣️ Language: Russian
- 💬 Style: Simple, everyday language
- ⚡ Performance: Fast responses, short confirmations

---

## 🏗️ System Architecture

This bot follows a modular design with clear separation of concerns:

📁 tele_reminder_bot/
├── main.py # Bot initialization and command handling
├── reminder_handler.py # Business logic for managing reminders
├── db_handler.py # SQLite-based storage layer
└── reminders.db # SQLite database for all user data

markdown
Copy
Edit

Architecture is event-driven, reacting to Telegram commands using asynchronous functions.

---

## 🧠 Key Components

### 🤖 Bot Framework

- **Library**: [aiogram](https://aiogram.dev/)
- **Why aiogram?** Modern `async/await` support, clean structure, fast
- **Features**: Command handling, state management, middleware support

### 📅 Reminder Management

- **Class**: `ReminderHandler`
- **Functions**: Create, list, cancel reminders; validate time format (HH:MM)
- **Scheduler**: Checks every minute using `asyncio` loop

### 💾 Data Storage

- **Type**: SQLite database (`reminders.db`)
- **Schema**: Reminder table with fields: `id`, `user_id`, `time`, `message`
- **Migration**: Automatic migration from JSON to SQLite with JSON backup
- **Advantages**: Durable, performant, suitable for moderate usage

---

## 💬 Command Interface

| Command     | Description                                                 |
|-------------|-------------------------------------------------------------|
| `/start`    | Shows a welcome message and how to use the bot              |
| `/remind`   | Adds a new reminder — `/remind 22:30 Read a book`           |
| `/list`     | Shows active reminders for the user                         |
| `/cancel`   | Cancels a reminder using its ID                             |

---

## 🔄 Data Flow

1. **User Command** → Bot receives Telegram command
2. **Routing** → aiogram dispatcher calls correct handler
3. **Processing** → ReminderHandler creates or updates reminders
4. **Persistence** → Data stored in `reminders.db`
5. **Scheduler** → Background loop checks for due reminders
6. **Notification** → Sends messages like:
🔔 Reminder: Read a book

yaml
Copy
Edit

---

## 📦 Dependencies

### 🧰 Required Libraries

- `aiogram` – Telegram Bot API wrapper
- `asyncio`, `datetime`, `logging` – Standard Python libs
- `sqlite3` – Built-in database module

### 🔐 Environment Variable

- `BOT_TOKEN` – Telegram bot token from @BotFather

---

## 🚀 Deployment Strategy

- **Storage**: Uses `SQLite` for persistent reminders
- **Configuration**: Token via `BOT_TOKEN` environment variable
- **Logging**: Console-based, easily extendable
- **Background Task**: Runs infinite loop with 1-minute check

### ✔️ Current Setup

- Local deployment or VPS-friendly
- Ready for 24/7 operation
- Backup system in place for old JSON files

---

## 📈 Performance & Scalability

- ✅ Indexed database fields for fast lookup
- ✅ Handles hundreds of reminders without issues
- ✅ Durable across restarts and exceptions

---

## 🆕 Recent Enhancements

- 🔁 **Migration**: JSON ➝ SQLite (2025-07)
- ⚡ **Performance**: Indexing for faster queries
- 🛡️ **Reliability**: Timestamps & validations added
- 📦 **Backup**: Old JSON data saved on first run

---

## 🧩 Future Improvements

- Add time zone support
- PostgreSQL backend for large deployments
- Web UI for visual management
- Multilingual support (English, Uzbek, etc.)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📢 Keywords (SEO)

`telegram reminder bot`, `aiogram scheduler`, `python telegram notification`,  
`sqlite reminder storage`, `daily task reminder`, `telegram bot for time alerts`

---

## 🌟 Support

If you find this project helpful:

- ⭐️ Star this repo
- 🍴 Fork to contribute
- 📣 Share with others

Made with ❤️ using Python and aiogram.