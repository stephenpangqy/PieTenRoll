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
    id_Exists = idExists(chat_id)
    if id_Exists:
        username = Users.query.filter_by(chat_id=chat_id).first().name
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
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(button)
        message_text = f'Welcome back {username}, Please select if you are finding a group member or looking for a group.'
        bot.send_message(chat_id, message_text, reply_markup = keyboard)
    else:
        bot.send_message(chat_id, f'Welcome to GroupTogether bot, We help you find your teammates with ease!')
        msg = bot.send_message(message.chat.id,"It looks like this is your first time using me. Please enter your name in the next chat bubble; make sure your instructors can recognize your name.")
        bot.register_next_step_handler(msg, register)

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
        bot.reply_to(message,"Thank you, " + name + ", you have successfully registered.")
        
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
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(button)
        message_text = f'Now, Please select if you are finding a group member or looking for a group.'
        bot.send_message(chat_id, message_text, reply_markup = keyboard)

@bot.callback_query_handler(lambda query: query.data == 'Find_groupmates')
def handle_callback(call):
    """
    Handles the execution of the respective functions upon receipt of the callback query
    """
    chat_id = call.message.chat.id

    #bot.register_next_step_handler(msg,confirmEvent)
    pass

@bot.callback_query_handler(lambda query: query.data == 'Find_group')
def handle_callback(call):
    """
    Handles the execution of the respective functions upon receipt of the callback query
    """
    chat_id = call.message.chat.id
    
    pass

def enter_school(chat_id):
    bot.send_message(chat_id, "Please type in your school name (Eg: NUS)")

def enter_module(chat_id):
    bot.send_message(chat_id, "Please type in your module code")
    
def enter_section(chat_id):
    bot.send_message(chat_id, "Please type in your section")

def enter_semester(chat_id):
    bot.send_message(chat_id, "Please type in your semester")

def enter_avail(chat_id):
    bot.send_message(chat_id, "Please type in the number of available slots")
    
bot.infinity_polling()
