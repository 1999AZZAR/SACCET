# Telegram Access Control Bot

This Python script creates a Telegram-based Access Control Bot with SQLite database integration. Users can grant or revoke access using commands, and the bot sends notifications to an admin for access-related activities.

## Setup

1. Replace `your_database.db` with the desired SQLite database filename.
2. Set `your_telegram_token` and `your_chat_id` with your Telegram bot credentials.
3. Install required Python packages: `flask`, `python-telegram-bot`.

## Usage

1. Run the script to start the Telegram bot.
2. Use Telegram commands: `/grant_access`, `/revoke_access`, `/list_users`.
3. Follow the bot's prompts to add or update user data.

## Commands

- `/grant_access`: Start the process to grant access.
- `/revoke_access`: Start the process to revoke access.
- `/list_users`: List all users with access.

## Database

The SQLite database (`your_database.db`) stores user data, including name and associated RFID cards.

## Notifications

The bot sends notifications to the specified Telegram chat for access-related events.

## Notes

- Ensure proper network connectivity for the Telegram bot to function.
- Adjust bot commands, database, and notifications as needed.
- Customize the script for additional features or integration.

Feel free to tailor this Telegram Access Control Bot to suit your specific requirements.
