import os

import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

API_KEY = "5047659649:AAHxljzEetaON7tXSqaCiFbNXckHFoHnIrg"
bot = telebot.TeleBot(API_KEY)

bot.set_my_commands([
<<<<<<< Updated upstream
    BotCommand('start', 'Get a welcoming introduction from the bot'),
])
=======
    BotCommand('start', 'Start finding your groupmates now!'),
])

@bot.message_handler(commands=['start'])
def start(message):
    """
    Command that welcomes the user and configures the initial setup
    """
    chat_id = message.chat.id

    if message.chat.type == 'private':
        chat_user = message.chat.first_name
    else:
        chat_user = message.chat.title
    
    bot.send_sticker(
        chat_id=chat_id, 
        data='CAACAgUAAxkBAAEDoRJh1y0KgigTU87x7QYrbKJNbfDavQACawMAAlobywF60Koi6G4EECME'
    )

    buttons = [
        InlineKeyboardButton(
        text = "Find groupmates",
        callback_data = "Find_groupmates"
    ),
        InlineKeyboardButton(
        text = "Find group",
        callback_data = "Find_group"
    )]

    message_text = f'Hello {chat_user}, welcome to GroupTogether bot. Please select if you are finding a group member or looking for a group.'
    bot.send_message(chat_id, message_text, reply_markup = InlineKeyboardMarkup(buttons))

bot.infinity_polling()
>>>>>>> Stashed changes
