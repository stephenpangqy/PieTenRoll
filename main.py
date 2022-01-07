import os
from flask import Flask, redirect, url_for, request
import requests
from flask_sqlalchemy import SQLAlchemy
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice

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
    


bot.set_my_commands([
    BotCommand('start', 'Get a welcoming introduction from the bot'),
])