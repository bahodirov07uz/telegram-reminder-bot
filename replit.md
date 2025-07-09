# Telegram Reminder Bot

## Overview

This is a Telegram bot application built with Python that provides reminder functionality to users. The bot allows users to set time-based reminders and manages them through a simple command interface. The application uses the aiogram framework for Telegram bot development and implements a custom reminder handler with JSON-based storage.

## User Preferences

- Preferred communication style: Simple, everyday language
- Bot interface language: Russian (messages should be in Russian for faster user comprehension)
- Performance preference: Fast response times, concise messages

## System Architecture

The application follows a modular architecture with separation of concerns:

- **main.py**: Entry point and bot initialization with command handlers
- **reminder_handler.py**: Core business logic for reminder management
- **db_handler.py**: Database operations and SQLite management
- **reminders.db**: SQLite database for persistent data storage

The architecture is event-driven, responding to Telegram commands and managing scheduled reminders through asynchronous operations.

## Key Components

### Bot Framework
- **Technology**: aiogram (Python Telegram Bot API wrapper)
- **Rationale**: Provides async/await support and modern Python patterns for handling Telegram interactions
- **Features**: Command filtering, message handling, and bot state management

### Reminder Management System
- **ReminderHandler Class**: Centralized logic for reminder operations
- **Capabilities**: Create, list, validate, and manage reminders
- **Time Validation**: Ensures proper HH:MM format for reminder times

### Command Interface
- **/start**: Welcome message and bot instructions
- **/remind**: Create new reminders with time and message
- **/list**: Display active reminders
- **/cancel**: Remove specific reminders by ID

### Data Storage
- **Format**: SQLite database (reminders.db)
- **Structure**: Relational database with proper indexing for performance
- **Migration**: Automatic migration from JSON to SQLite with backup
- **Persistence**: Database storage ensures reminders survive bot restarts

## Data Flow

1. **User Input**: Users send commands through Telegram
2. **Command Processing**: aiogram dispatcher routes commands to appropriate handlers
3. **Business Logic**: ReminderHandler processes reminder operations
4. **Data Persistence**: Reminders saved to/loaded from SQLite database
5. **Scheduled Delivery**: Bot delivers reminders at specified times
6. **Response**: User receives confirmation or reminder messages

## External Dependencies

### Required Libraries
- **aiogram**: Telegram Bot API framework
- **asyncio**: Asynchronous programming support (built-in)
- **json**: Data serialization (built-in)
- **datetime**: Time handling (built-in)
- **logging**: Application logging (built-in)

### Environment Variables
- **BOT_TOKEN**: Telegram bot authentication token (required)

### Third-party Services
- **Telegram API**: Primary interface for bot communication
- **SQLite database**: Embedded database for reliable storage

## Deployment Strategy

### Current Setup
- **Storage**: SQLite database (reminders.db)
- **Configuration**: Environment variable for bot token
- **Logging**: Console-based logging with configurable levels
- **Migration**: Automatic JSON-to-SQLite migration with backup

### Considerations
- **Scalability**: SQLite storage suitable for moderate usage with proper indexing
- **State Management**: Database-backed reminder tracking with transaction support
- **Error Handling**: Comprehensive exception handling for database operations and API calls
- **Performance**: Indexed queries for efficient reminder retrieval

### Recent Enhancements
- **Database Migration**: Successfully migrated from JSON to SQLite (July 2025)
- **Performance Optimization**: Added database indexing for faster queries
- **Data Integrity**: Improved reminder tracking with proper timestamps
- **Backup System**: Automatic backup of old JSON data during migration

The architecture prioritizes scalability and performance while maintaining simplicity for deployment and essential functionality for reminder management.