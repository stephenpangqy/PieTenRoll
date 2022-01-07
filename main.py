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
    section = db.Column(db.String(100), nullable=False)
    
class Looking_For_Members(db.Model):
    __tablename__ = 'looking_for_members'
    
    chat_id = db.Column(db.Integer, nullable=False, primary_key=True)
    school = db.Column(db.String(100), nullable=False, primary_key=True)
    module_code = db.Column(db.String(100), nullable=False, primary_key=True)
    semester = db.Column(db.Integer, nullable=False,primary_key=True)
    section = db.Column(db.String(100), nullable=False)
    num_members_need = db.Column(db.Integer, nullable=False)
    
class Match_Found(db.Model):
    __tablename__ = 'match_found'
    
    finder_chat_id = db.Column(db.Integer,nullable=False,primary_key=True)
    looker_chat_id = db.Column(db.Integer,nullable=False,primary_key=True)
    school = db.Column(db.String(100), nullable=False, primary_key=True)
    module_code = db.Column(db.String(100), nullable=False, primary_key=True)
    semester = db.Column(db.Integer, nullable=False,primary_key=True)
    section = db.Column(db.String(100), nullable=False)
    accepted = db.Column(db.String(1), nullable=False)
    
def idExists(chat_id):
    # FUNCTION TO CHECK IF USER"S CHAT ID IS IN DATABASE
    users = Users.query.filter_by(chat_id=chat_id)
    for user in users:
        return True
    return False

temp_find_group_dict = {}
temp_find_member_dict = {}
conversation_dict = {}
accept_dict = {}

class Temp_Find_Group:
    def __init__(self,school):
        self.school = school
        self.module_code = None
        self.semester = None
        self.section = None
        
    def setModuleCode(self,module_code):
        self.module_code = module_code
    def setSemester(self,sem):
        self.semester = sem
    def setSection(self,section):
        self.section = section
    def getSchool(self):
        return self.school
    def getModuleCode(self):
        return self.module_code
    def getSemester(self):
        return self.semester
    def getSection(self):
        return self.section

class Temp_Find_Member:
    def __init__(self,school):
        self.school = school
        self.module_code = None
        self.semester = None
        self.section = None
        self.num_members_needed = None
        
    def setModuleCode(self,module_code):
        self.module_code = module_code
    def setSemester(self,sem):
        self.semester = sem
    def setSection(self,section):
        self.section = section
    def setNumMembersNeeded(self,num_members_needed):
        self.num_members_needed = num_members_needed
    def getSchool(self):
        return self.school
    def getModuleCode(self):
        return self.module_code
    def getSemester(self):
        return self.semester
    def getSection(self):
        return self.section
    def getNumMembersNeeded(self):
        return self.num_members_needed

bot.set_my_commands([
    BotCommand('start', 'Start finding your groupmates now!'),
    BotCommand('view', 'View your list of groups/members you are finding!'),
])

@bot.message_handler(commands=['start'])
def start(message):
    """
    Command that welcomes the user and configures the initial setup
    """
    chat_id = message.chat.id
    id_exist = idExists(chat_id)
    if not id_exist:
        bot.send_message(chat_id,"Welcome to GroupTogether, I can help make your project group searching life a breeze.")
        msg = bot.send_message(chat_id,"It looks like it is your first time using me. Please enter your name in the next chat bubble. This name will be saved and used to identify yourself to others.")
        bot.register_next_step_handler(msg,register)
        return
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
    message_text = f'Welcome back , Please select if you are finding a group member or looking for a group.'
    bot.send_message(chat_id, message_text, reply_markup = keyboard)
    #### TEST #################################
    other_chat_id = 839535647
    keyboard = [[InlineKeyboardButton("Accept",callback_data='converse:yes:' + str(other_chat_id)),InlineKeyboardButton("reject",callback_data='converse:no:' + str(other_chat_id))]]
    markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id,"Would you like convo Ben?",reply_markup=markup)
    
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
    
@bot.message_handler(commands=['view'])
def view(message):
    chat_id = message.chat.id
    id_exist = idExists(chat_id)
    
    flag1 = False
    flag2 = False
    
    if not id_exist:
        start(message)
    else:
        output = ""
        groups = Looking_For_Group.query.filter_by(chat_id = chat_id)
        
        for group in groups:
            flag1 = True
            break
        
        if flag1:
            output += "*Looking for Groups* :\n\n"
            for group in groups:
                school = group.school
                module_code = group.module_code
                semester = group.semester
                section = group.section
                # output += school + " Semester " + str(semester) + " " + module_code +  " " + section + "\n"
                output += " Semester: *" + str(semester) + "* Module: *" + module_code +  "* Section:* " + section + "*\n"
        
        members = Looking_For_Members.query.filter_by(chat_id = chat_id)
        
        for memb in members:
            flag2 = True
            break
        
        if flag2:
            output += "\n *Looking for Members* :\n\n"
            for memb in members:
                school = memb.school
                module_code = memb.module_code
                semester = memb.semester
                section = memb.section
                num_mem_need = memb.num_members_need
                
                # output += school + " semester " + str(semester) + " " + module_code +  " " + section + ": " + str(num_mem_need) + "\n"
                output += " Semester: *" + str(semester) + "* Module: *" + module_code +  "* Section:* " + section + "* Num remaining: *"+ str(num_mem_need) + "* \n"

        if not flag1 and not flag2:
            bot.send_message(chat_id, "~ Nothing to view ~")
        else:
            bot.send_message(chat_id, output, parse_mode= 'Markdown')


@bot.callback_query_handler(lambda query: query.data == 'Find_groupmates')
def handle_callback(call):
    """
    Handles the execution of the respective functions upon receipt of the callback query
    """
    chat_id = call.message.chat.id
    msg = bot.send_message(chat_id, "Please type in your school name (Eg: NUS)")
    bot.register_next_step_handler(msg, enter_school2)

@bot.callback_query_handler(lambda query: query.data == 'Find_group')
def handle_callback(call):
    """
    Handles the execution of the respective functions upon receipt of the callback query
    """
    chat_id = call.message.chat.id
    msg = bot.send_message(chat_id, "Please type in your school name (Eg: NUS)")
    bot.register_next_step_handler(msg, enter_school1)
    
    

def enter_school1(message):
    chat_id = message.chat.id
    school = message.text.upper().strip()
    school_list = ['NUS','NTU','SMU']
    if school not in school_list: 
        msg = bot.reply_to(message,'School is invalid, please try again!')
        bot.register_next_step_handler(msg,enter_school1)
        return
    else:
        # new_record = Looking_For_Group(chat_id=chat_id,school=school)
        # db.session.add(new_record)
        # db.session.commit()
        temp_find_group = Temp_Find_Group(school)
        temp_find_group_dict[chat_id] = temp_find_group
        msg = bot.send_message(chat_id, "Please type in your module code (Eg: IS216)")
        bot.register_next_step_handler(msg, enter_module1)


def enter_school2(message):
    chat_id = message.chat.id
    school = message.text.upper().strip()
    school_list = ['NUS','NTU','SMU']
    if school not in school_list: 
        msg = bot.reply_to(message,'School is invalid, please try again!')
        bot.register_next_step_handler(msg,enter_school2)
        return
    else:
        # new_record = Looking_For_Group(chat_id=chat_id,school=school)
        # db.session.add(new_record)
        # db.session.commit()
        temp_find_member = Temp_Find_Member(school)
        temp_find_member_dict[chat_id] = temp_find_member
        msg = bot.send_message(chat_id, "Please type in your module code (Eg: IS216)")
        bot.register_next_step_handler(msg, enter_module2)


def enter_module1(message):
    chat_id = message.chat.id
    module = message.text.strip()
    temp_find_group = temp_find_group_dict[chat_id]
    temp_find_group.setModuleCode(module)
    msg = bot.send_message(chat_id, "Please type in your section (Eg: G11)")
    bot.register_next_step_handler(msg, enter_section1)

def enter_module2(message):
    chat_id = message.chat.id
    module = message.text.strip()
    temp_find_member = temp_find_member_dict[chat_id]
    temp_find_member.setModuleCode(module)
    msg = bot.send_message(chat_id, "Please type in your section (Eg: G11)")
    bot.register_next_step_handler(msg, enter_section2)

    
def enter_section1(message):
    chat_id = message.chat.id
    section = message.text.strip()
    temp_find_group = temp_find_group_dict[chat_id]
    temp_find_group.setSection(section)
    msg = bot.send_message(chat_id, "Please type in your semester (1 or 2)")
    bot.register_next_step_handler(msg, enter_semester1)

def enter_section2(message):
    chat_id = message.chat.id
    section = message.text.strip()
    temp_find_member = temp_find_member_dict[chat_id]
    temp_find_member.setSection(section)
    msg = bot.send_message(chat_id, "Please type in your semester (1 or 2)")
    bot.register_next_step_handler(msg, enter_semester2)


def enter_semester1(message):
    chat_id = message.chat.id
    semester = message.text.strip()
    temp_find_group = temp_find_group_dict[chat_id]
    temp_find_group.setSemester(semester)
    # Add to DB
    new_record = Looking_For_Group(chat_id=chat_id,school=temp_find_group.getSchool(),module_code=temp_find_group.getModuleCode(),semester=temp_find_group.getSemester(),section=temp_find_group.getSection())
    db.session.add(new_record)
    db.session.commit()
    
    msg = bot.send_message(chat_id, "Your group search request has been successfully created. We will search for available groups for you...")
    bot.register_next_step_handler(msg, search1(chat_id))

def enter_semester2(message):
    chat_id = message.chat.id
    semester = message.text.strip()
    temp_find_member = temp_find_member_dict[chat_id]
    temp_find_member.setSemester(semester)
    msg = bot.send_message(chat_id, "Please type how many more members you need to find")
    bot.register_next_step_handler(msg, enter_avail)

def enter_avail(message):
    chat_id = message.chat.id
    avail = message.text.strip()
    # Add to DB
    temp_find_member = temp_find_member_dict[chat_id]
    temp_find_member.setNumMembersNeeded(avail)
    new_record = Looking_For_Members(chat_id=chat_id,school=temp_find_member.getSchool(),module_code=temp_find_member.getModuleCode(),semester=temp_find_member.getSemester(),section=temp_find_member.getSection(), num_members_need=temp_find_member.getNumMembersNeeded())
    db.session.add(new_record)
    db.session.commit()
    
    msg = bot.send_message(chat_id, "Your group search request has been successfully created. We will search for available members for you...")
    bot.register_next_step_handler(msg, search2(chat_id))
    
    

@bot.callback_query_handler(lambda query: query.data.split(":")[0] == 'converse')
def start_convo(query):
    response = query.data.split(":")[1]
    other_chat_id = int(query.data.split(":")[2])
    match_string = query.data.split(":")[3]
    name = Users.query.filter_by(chat_id=other_chat_id)
    chat_id = query.from_user.id
    message_id = query.message.id
    new_markup = InlineKeyboardMarkup([])
    bot.edit_message_reply_markup(chat_id,message_id,reply_markup=new_markup)
    if response == "no":
        # Dont start convo
        bot.send_message(chat_id,"You decided not to have the conversation with " + name + ".")
        new_markup = InlineKeyboardMarkup([])
        bot.edit_message_reply_markup(chat_id,message_id,reply_markup=new_markup)
    else:
        # Check if ongoing convo
        if chat_id in conversation_dict:
            bot.send_message(chat_id,"You are currently in an ongoing conversation, please end this one before continuing another.")
            return
        
        conversation_dict[chat_id] = other_chat_id
        conversation_dict[other_chat_id] = chat_id
        keyboard = [[InlineKeyboardButton("Accept",callback_data='end_convo:accept:' + str(other_chat_id) + ":" + match_string),InlineKeyboardButton("Reject",callback_data='end_convo:reject:' + str(other_chat_id) + ":" + match_string)]]
        markup = InlineKeyboardMarkup(keyboard)
        name = Users.query.filter_by(chat_id=chat_id).first().name
        other_name = Users.query.filter_by(chat_id=other_chat_id).first().name
        msg = bot.send_message(chat_id,'You are now in a conversation with '+ other_name +', Any text you type from here on will be sent to the other person.\n\nIf you have made a decision on whether to team up with the person, click on Accept or Reject to end the conversation.',reply_markup=markup)
        url = 'https://api.telegram.org/bot' + API_KEY + '/sendMessage'
        data = {'chat_id': other_chat_id, 'text': 'We have found a match for you with ' + name + '. To start talking to them, type the command /converse'}
        requests.post(url,data).json()
        bot.register_next_step_handler(msg, converse)

@bot.callback_query_handler(lambda query: query.data.split(":")[0] == 'end_convo')
def endConvo(query):
    response = query.data.split(":")[1]
    other_chat_id = int(query.data.split(":")[2])
    other_name = Users.query.filter_by(chat_id=other_chat_id).first().name
    match_string = query.data.split(":")[3]
    chat_id = query.from_user.id
    name = Users.query.filter_by(chat_id=chat_id).first().name
    message_id = query.message.id
    new_markup = InlineKeyboardMarkup([])
    bot.edit_message_reply_markup(chat_id,message_id,reply_markup=new_markup)
    
    if response == "accept":
        # Process acceptance
        match_list = match_string.split("-")
        match_found = Match_Found.query.filter_by(finder_chat_id=int(match_list[0]),looker_chat_id=int(match_list[1]),school=match_list[2],module_code=match_list[3],semester=int(match_list[4]),section=match_list[5]).first()
        match_found.accepted = 'A'
        db.session.commit()
        looking_for_member = Looking_For_Members.query.filter_by(chat_id=int(match_list[0]),school=match_list[2],module_code=match_list[3],semester=int(match_list[4])).first()
        looking_for_member.num_members_need -= 1
        db.session.commit()
        url = 'https://api.telegram.org/bot' + API_KEY + '/sendMessage'
        data = {'chat_id': other_chat_id, 'text': 'Hooray, ' + name + ' has agreed to group together with you for the project. Ending the private conversation.'}
        requests.post(url,data).json()
        bot.send_message(chat_id,"Congratulations! You and " + other_name + " have agreed to group together. Ending private conversation.")
        del conversation_dict[chat_id]
        del conversation_dict[other_chat_id]
    else:
        match_list = match_string.split("-")
        match_found = Match_Found.query.filter_by(finder_chat_id=int(match_list[0]),looker_chat_id=int(match_list[1]),school=match_list[2],module_code=match_list[3],semester=int(match_list[4]),section=match_list[5]).first()
        match_found.accepted = 'R'
        db.session.commit()
        url = 'https://api.telegram.org/bot' + API_KEY + '/sendMessage'
        data = {'chat_id': other_chat_id, 'text': 'Aww, it looks like ' + name + ' has decided to reject your partnership. Better luck with another person! Ending the private conversation.'}
        requests.post(url,data).json()
        bot.send_message(chat_id,"Awww... It looks like you and  " + other_name + " were just not mean't to be together...in the same group. Ending private conversation.")
        del conversation_dict[chat_id]
        del conversation_dict[other_chat_id]

def converse(message):
    chat_id = message.chat.id
    chat_message = message.text
    if chat_id not in conversation_dict:
        bot.send_message(chat_id,"You are not in a conversation!")
    else:
        other_chat_id = conversation_dict[chat_id]
        url = 'https://api.telegram.org/bot' + API_KEY + '/sendMessage'
        data = {'chat_id': other_chat_id, 'text': chat_message}
        requests.post(url,data).json()
        msg = bot.reply_to(message,"Message sent!")
        print(conversation_dict)
        bot.register_next_step_handler(msg, converse)
        
@bot.message_handler(commands=['converse'])
def startConvo(message):
    chat_id = message.chat.id
    if chat_id not in conversation_dict:
        bot.send_message(chat_id,"You are not in a conversation!")
    else:
        other_chat_id = conversation_dict[chat_id]
        keyboard = [[InlineKeyboardButton("Accept",callback_data='end_convo:accept:' + str(other_chat_id)),InlineKeyboardButton("reject",callback_data='end_convo:reject:' + str(other_chat_id))]]
        markup = InlineKeyboardMarkup(keyboard)
        name = Users.query.filter_by(chat_id=chat_id).first().name
        other_name = Users.query.filter_by(chat_id=other_chat_id).first().name
        msg = bot.send_message(chat_id,'You are now in a conversation with '+ other_name +', Any text you type from here on will be sent to the other person.\n\nIf you have made a decision on whether to team up with the person, click on Accept or Reject to end the conversation.',reply_markup=markup)
        url = 'https://api.telegram.org/bot' + API_KEY + '/sendMessage'
        data = {'chat_id': other_chat_id, 'text': name + ' is now online. You can start talking to them.'}
        requests.post(url,data).json()
        bot.register_next_step_handler(msg,converse)

# Search Code Here
def search1(chat_id):
    
    temp_find_group = temp_find_group_dict[chat_id]
    avl_groups = Looking_For_Members.query.filter_by(school=temp_find_group.getSchool(),module_code=temp_find_group.getModuleCode(),semester=temp_find_group.getSemester(), section=temp_find_group.getSection())
    found = False
    for avl_group in avl_groups:
        found = True
    if not found:
        bot.send_message(chat_id,"Unfortunately, there are currently no matching groups with availability. Please use the /search command again after waiting for some time.")
    else:
        for group in avl_groups:
            other_chat_id = group.chat_id
            name = Users.query.filter_by(chat_id=other_chat_id).first().name
            new_match_found = Match_Found(finder_chat_id=other_chat_id,looker_chat_id=chat_id,school=temp_find_group.getSchool(),module_code=temp_find_group.getModuleCode(),semester=temp_find_group.getSemester(), section=temp_find_group.getSection(),accepted='P')
            db.session.add(new_match_found)
            db.session.commit()
            match_string = '-'.join([str(new_match_found.finder_chat_id),str(new_match_found.looker_chat_id),new_match_found.school,new_match_found.module_code,str(new_match_found.semester),new_match_found.section])
            keyboard = [[InlineKeyboardButton("Yes",callback_data='converse:yes:' + str(other_chat_id) + ":" + match_string),InlineKeyboardButton("No",callback_data='converse:no:' + str(other_chat_id))]]
            markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id,"We have found an available group for your following group search:\n\nSchool: "+ temp_find_group.getSchool() + "\nModule: " + temp_find_group.getModuleCode() + "\nSemester: " + temp_find_group.getSemester() + "\nSection: " + temp_find_group.getSection() + "\n\nHere are the group details:\n\nContact Person: " + name + "\nAvailable slots: " + str(group.num_members_need) + "\n\nWould you like to start a conversation?" ,reply_markup=markup)

    del temp_find_group_dict[chat_id]
            


def search2(chat_id):
    
    temp_find_member = temp_find_member_dict[chat_id]
    avl_members = Looking_For_Group.query.filter_by(school=temp_find_member.getSchool(),module_code=temp_find_member.getModuleCode(),semester=temp_find_member.getSemester(), section=temp_find_member.getSection())
    found = False
    for avl_mem in avl_members:
        found = True
    if not found:
        bot.send_message(chat_id,"Unfortunately, there are currently no matching users looking for a group. Please use the /search command again after waiting for some time.")
    else:
        for member in avl_members:
            other_chat_id = member.chat_id
            name = Users.query.filter_by(chat_id=other_chat_id).first().name
            new_match_found = Match_Found(finder_chat_id=chat_id,looker_chat_id=other_chat_id,school=temp_find_member.getSchool(),module_code=temp_find_member.getModuleCode(),semester=temp_find_member.getSemester(), section=temp_find_member.getSection(),accepted='P')
            db.session.add(new_match_found)
            db.session.commit()
            match_string = '-'.join([str(new_match_found.finder_chat_id),str(new_match_found.looker_chat_id),new_match_found.school,new_match_found.module_code,str(new_match_found.semester),new_match_found.section])
            keyboard = [[InlineKeyboardButton("Yes",callback_data='converse:yes:' + str(other_chat_id) + ":" + match_string),InlineKeyboardButton("No",callback_data='converse:no:' + str(other_chat_id))]]
            markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id,"We have found an available member for your following member search:\n\nSchool: "+ temp_find_member.getSchool() + "\nModule: " + temp_find_member.getModuleCode() + "\nSemester: " + temp_find_member.getSemester() + "\nSection: " + temp_find_member.getSection() + "\n\nHere are the group details:\n\nContact Person: " + name + "\n\nWould you like to start a conversation?" ,reply_markup=markup)
        
    del temp_find_member_dict[chat_id]
bot.infinity_polling()
