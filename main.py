import os
from flask import Flask, redirect, url_for, request
import requests
from flask_sqlalchemy import SQLAlchemy
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

API_KEY = "5047659649:AAHxljzEetaON7tXSqaCiFbNXckHFoHnIrg"
bot = telebot.TeleBot(API_KEY)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/grouptogetherdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
class Users(db.Model):
    __tablename__ = 'users'

    chat_id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class Looking_For_Group(db.Model):
    __tablename__ = 'looking_for_group'
    
    chat_id = db.Column(db.Integer, nullable=False, primary_key=True)
    school = db.Column(db.String(100), nullable=False, primary_key=True)
    module_code = db.Column(db.String(100), nullable=False, primary_key=True)
    semester = db.Column(db.Integer, nullable=False,primary_key=True)
    
class Looking_For_Members(db.Model):
    __tablename__ = 'looking_for_members'
    
    chat_id = db.Column(db.Integer, nullable=False, primary_key=True)
    school = db.Column(db.String(100), nullable=False, primary_key=True)
    module_code = db.Column(db.String(100), nullable=False, primary_key=True)
    semester = db.Column(db.Integer, nullable=False,primary_key=True)
    num_members_need = db.Column(db.Integer, nullable=False)
    
class Match_Found(db.Model):
    __tablename__ = 'match_found'
    
    finder_chat_id = db.Column(db.Integer,nullable=False,primary_key=True)
    looker_chat_id = db.Column(db.Integer,nullable=False,primary_key=True)
    school = db.Column(db.String(100), nullable=False, primary_key=True)
    module_code = db.Column(db.String(100), nullable=False, primary_key=True)
    semester = db.Column(db.Integer, nullable=False,primary_key=True)
    accepted = db.Column(db.String(1), nullable=False)
    
def idExists(chat_id):
    # FUNCTION TO CHECK IF USER"S CHAT ID IS IN DATABASE
    users = Users.query.filter_by(chat_id=chat_id)
    for user in users:
        return True
    return False

bot.set_my_commands([
    BotCommand('start', 'Start finding your groupmates now!'),
])

@bot.message_handler(commands=['start'])
def start(message):
    """
    Command that welcomes the user and configures the initial setup
    """
    chat_id = message.chat.id
    already_registered = idExists(chat_id)
    if not already_registered:
        message_text = f'Hello, welcome to GroupTogether bot. It looks like this is your first time, Please enter your name in the next bubble.\n\nThis name will be used to identify yourself to others.'
        msg = bot.send_message(chat_id,message_text)
        bot.register_next_step_handler(msg,register)
    else:
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

        message_text = f'Welcome back {chat_user}, Please select if you are finding a group member or looking for a group.'
        bot.send_message(chat_id, message_text, reply_markup = InlineKeyboardMarkup(buttons))

def register(message):
    chat_id = message.chat.id
    name = message.text.strip()
    if name == "":
        msg = bot.reply_to(message,'Your name cannot be empty. Please enter your name again!')
        bot.register_next_step_handler(msg,register)
        return
    elif len(name) > 100:
        msg = bot.reply_to(message,"Your name cannot be longer than 100 characters. Please enter your name again!")
        bot.register_next_step_handler(msg,register)
        return
    else:
        new_user = Users(chat_id=chat_id,name=name)
        db.session.add(new_user)
        db.session.commit()
        buttons = [
            InlineKeyboardButton(
            text = "Find groupmates",
            callback_data = "Find_groupmates"
        ),
            InlineKeyboardButton(
            text = "Find group",
            callback_data = "Find_group"
        )]
        bot.reply_to(message, "Thank you " + name + ", you have been registered on our bot.")
        message_text = f'Now, Please select if you are finding a group member or looking for a group.'
        bot.send_message(chat_id, message_text, reply_markup = InlineKeyboardMarkup(buttons))
        



bot.infinity_polling()
