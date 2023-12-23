from flask import Flask, request, g
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

app = Flask(__name__)

DATABASE = 'your_database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                rfid_card TEXT
            )
        ''')
        db.commit()

init_db()

TELEGRAM_TOKEN = 'your_telegram_token'
TELEGRAM_CHAT_ID = 'your_chat_id'
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

RFID, NAME, UPDATE_CONFIRMATION, UPDATE_DATA, CONFIRMATION, REVOKE_CONFIRMATION, LIST_USERS = range(7)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the Access Control Bot! Use /grant_access to grant access, /revoke_access to revoke access, or /list_users to list all users.")
    return ConversationHandler.END

def grant_access_start(update: Update, context: CallbackContext):
    with app.app_context():
        update.message.reply_text("Please provide the RFID number for the new user.")
    return RFID

def grant_access_rfid(update: Update, context: CallbackContext):
    with app.app_context():
        context.user_data['rfid'] = update.message.text

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT name FROM user_data WHERE rfid_card = ?', (context.user_data['rfid'],))
        result = cursor.fetchone()

        if result:
            context.user_data['name'] = result[0]
            update.message.reply_text(f"RFID already associated with user: {context.user_data['name']}. Do you want to update their data?",
                                    reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
            return UPDATE_CONFIRMATION
        else:
            update.message.reply_text("Great! Now, please provide the name for the new user.")
            return NAME

def grant_access_name(update: Update, context: CallbackContext):
    with app.app_context():
        context.user_data['name'] = update.message.text

        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO user_data (name, rfid_card) VALUES (?, ?)', (context.user_data['name'], context.user_data['rfid']))
        db.commit()

        send_notification_to_admin(f"Access granted for {context.user_data['name']} with RFID card: {context.user_data['rfid']}.")

    return ConversationHandler.END

def update_confirmation(update: Update, context: CallbackContext):
    with app.app_context():
        if update.message.text.lower() == 'yes':
            update.message.reply_text("Please provide the new name for the user.")
            return UPDATE_DATA
        else:
            update.message.reply_text("Operation canceled.")
            return ConversationHandler.END

def update_data(update: Update, context: CallbackContext):
    with app.app_context():
        new_name = update.message.text
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE user_data SET name = ? WHERE rfid_card = ?', (new_name, context.user_data['rfid']))
        db.commit()

        send_notification_to_admin(f"Data updated for {new_name} with RFID card: {context.user_data['rfid']}.")

    return ConversationHandler.END

def revoke_access_start(update: Update, context: CallbackContext):
    with app.app_context():
        update.message.reply_text("Please provide the name of the user to revoke access.")
    return CONFIRMATION

def revoke_access_confirmation(update: Update, context: CallbackContext):
    with app.app_context():
        context.user_data['name'] = update.message.text

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT rfid_card FROM user_data WHERE name = ?', (context.user_data['name'],))
        result = cursor.fetchone()

        if result:
            rfid_card = result[0]
            context.user_data['rfid'] = rfid_card
            update.message.reply_text(f"Do you want to revoke access for {context.user_data['name']} with RFID card: {rfid_card}?",
                                      reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
            return REVOKE_CONFIRMATION
        else:
            update.message.reply_text(f"No user found with the name: {context.user_data['name']}.")
            return ConversationHandler.END

def revoke_confirmation(update: Update, context: CallbackContext):
    with app.app_context():
        if update.message.text.lower() == 'yes':
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM user_data WHERE name = ?', (context.user_data['name'],))
            db.commit()

            send_notification_to_admin(f"Access revoked for {context.user_data['name']} with RFID card: {context.user_data['rfid']}.")
        else:
            update.message.reply_text("Operation canceled.")

        return ConversationHandler.END

def list_users(update: Update, context: CallbackContext):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT name, rfid_card FROM user_data')
        users = cursor.fetchall()

    if users:
        user_list = "\n".join([f"- {user[0]} with RFID card: {user[1]}" for user in users])
        update.message.reply_text(f"List of granted users:\n{user_list}")
    else:
        update.message.reply_text("No users with access found.")

def send_notification_to_admin(message):
    updater.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def error(update: Update, context: CallbackContext):
    update.message.reply_text(f"An error occurred: {context.error}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("list_users", list_users))

grant_access_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('grant_access', grant_access_start)],
    states={
        RFID: [MessageHandler(Filters.text, grant_access_rfid)],
        NAME: [MessageHandler(Filters.text, grant_access_name)],
        UPDATE_CONFIRMATION: [MessageHandler(Filters.regex('^(Yes|No)$'), update_confirmation)],
        UPDATE_DATA: [MessageHandler(Filters.text, update_data)],
    },
    fallbacks=[]
)

revoke_access_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('revoke_access', revoke_access_start)],
    states={
        CONFIRMATION: [MessageHandler(Filters.text, revoke_access_confirmation)],
        REVOKE_CONFIRMATION: [MessageHandler(Filters.regex('^(Yes|No)$'), revoke_confirmation)],
    },
    fallbacks=[]
)

dispatcher.add_handler(grant_access_conv_handler)
dispatcher.add_handler(revoke_access_conv_handler)
dispatcher.add_error_handler(error)

updater.start_polling()

@app.route('/process_data', methods=['POST'])
def process_data():
    with app.app_context():
        data = request.form['data']
        
        rfid_card = data.split('&')[0].split('=')[1]
        action = data.split('&')[1].split('=')[1]

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT name FROM user_data WHERE rfid_card = ?', (rfid_card,))
        result = cursor.fetchone()

        if result:
            name = result[0]
            response = f"1 {name}"
            message = f"{name} is {action}ing the building."
            send_notification_to_admin(message)
        else:
            response = "0"
            message = f"Unauthorized access attempt with RFID card: {rfid_card}."
            send_notification_to_admin(message)

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
