# Telegram Reminder Bot

## Overview

This is a Telegram bot application built with Python that provides reminder functionality to users. The bot allows users to set time-based reminders and manages them through a simple command interface. The application uses the aiogram framework for Telegram bot development and implements a custom reminder handler with JSON-based storage.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with separation of concerns:

- **main.py**: Entry point and bot initialization with command handlers
- **reminder_handler.py**: Core business logic for reminder management
- **storage.json**: Persistent data storage using JSON format

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
- **Format**: JSON file-based storage (storage.json)
- **Structure**: Simple array of reminder objects with ID, time, and message
- **Persistence**: File-based storage ensures reminders survive bot restarts

## Data Flow

1. **User Input**: Users send commands through Telegram
2. **Command Processing**: aiogram dispatcher routes commands to appropriate handlers
3. **Business Logic**: ReminderHandler processes reminder operations
4. **Data Persistence**: Reminders saved to/loaded from JSON storage
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
- **No database dependency**: Uses local JSON file storage

## Deployment Strategy

### Current Setup
- **Storage**: Local file system (storage.json)
- **Configuration**: Environment variable for bot token
- **Logging**: Console-based logging with configurable levels

### Considerations
- **Scalability**: Current JSON storage suitable for single-user or small-scale usage
- **State Management**: In-memory reminder tracking with file persistence
- **Error Handling**: Basic exception handling for file operations and API calls

### Potential Enhancements
- Could migrate to database storage (PostgreSQL) for multi-user scenarios
- Could add user authentication and multi-tenant support
- Could implement more sophisticated scheduling mechanisms

The architecture prioritizes simplicity and ease of deployment while maintaining essential functionality for reminder management.