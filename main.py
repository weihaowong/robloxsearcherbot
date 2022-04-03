import os
import telebot, requests, json
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
from keep_alive import keep_alive


my_secret = os.environ['apitoken']

API_TOKEN = f'{my_secret}' 

bot = telebot.TeleBot(API_TOKEN)

# registers the user id in users.txt
@bot.message_handler(commands=['start'])
def start(m):
  bot.reply_to(m, f"Hi {m.from_user.first_name}! Welcome. This bot helps you to search for users, friends, avatar etc in Roblox. Send me /help to start!")
  names = open("names.txt", "a+")
  if m.from_user.last_name != None:
    names.write(f"\n({m.from_user.first_name} {m.from_user.last_name}, @{m.from_user.username}, {m.from_user.id})")
  else:
    names.write(f"\n({m.from_user.first_name}, @{m.from_user.username}, {m.from_user.id})")
  names.close()

@bot.message_handler(commands='help')
def help(m):
  bot.send_message(m.chat.id, """
List of commands:
                  
/avatar -- Get the avatar of a user
/status -- Check if a user is online
/getid -- Get the user ID of a user
/friends -- Get a short list of friends of a user
/game -- Sends you a game created by a user""")


@bot.message_handler(commands='avatar')
def usersearch(m):
  msg = bot.send_message(m.chat.id, "Send me a user's username to get the user's avatar.")
  bot.register_next_step_handler(msg, username)
  
def username(m):
  try:
    url = requests.get(f'https://api.roblox.com/users/get-by-username?username={m.text}')
    text = url.text
    data = json.loads(text)
    user = data
    userid = user['Id']
    url = requests.get(f'https://www.roblox.com/bust-thumbnail/json?userId={userid}&height=512&width=512')
    text = url.text
    data = json.loads(text)
    largeavatar = data['Url']
    bot.send_photo(m.chat.id, f'{largeavatar}', caption=f'Avatar of {m.text}')
  except:
    bot.send_message(m.chat.id, 'An error occured. Please send the correct username in the correct format.')

@bot.message_handler(commands='status')
def info(m):
  msg = bot.send_message(m.chat.id, "Send me the user's username to check!")
  bot.register_next_step_handler(msg, status)
def status(m):
  try:
    url = requests.get(f'https://api.roblox.com/users/get-by-username?username={m.text}')
    text = url.text
    data = json.loads(text)
    user = data
    userid = user['Id']
    url = requests.get(f'https://api.roblox.com/Users/{userid}/OnlineStatus')
    text = url.text
    data = json.loads(text)
    isonline = data['IsOnline']
    lastonline = data['LastOnline']
    Date = lastonline.rpartition('T')[0]
    Time = lastonline.rpartition('T')[2]
    timeETZ = Time.rpartition('-')[0]
    ETZ = Time.rpartition('-')[2]
    if isonline == False:
      bot.send_message(m.chat.id, f"""
{m.text} status:

Currently offline
Last online: {Date} {timeETZ} UTC-{ETZ}""")
    else:
      bot.send_message(m.chat.id, f"""
{m.text} status:

Currently online in Roblox!!""")
  except:
    bot.send_message(m.chat.id, 'An error occured. Please send the correct username in the correct format.')    

@bot.message_handler(commands='friends')
def friends(m):
  msg = bot.send_message(m.chat.id, "Send me the user's username to get the list of friends")
  bot.register_next_step_handler(msg, list)
def list(m):
  try:
    url = requests.get(f'https://api.roblox.com/users/get-by-username?username={m.text}')
    text = url.text
    data = json.loads(text)
    user = data
    userid = user['Id']
    url = requests.get(f'https://api.roblox.com/users/{userid}/friends')
    text = url.text
    data = json.loads(text)
    usernames = ''
    for i in data:
      usernames = f"{usernames}\n{i['Username']}"
    bot.send_message(m.chat.id, f"<b>List of friends of {m.text}</b>\n{usernames}", parse_mode = 'HTML')
  except:
    bot.send_message(m.chat.id, 'An error occured. Please send the correct username in the correct format.')
    

@bot.message_handler(commands='getid')
def getid(m):
  msg = bot.send_message(m.chat.id, "Send me the user's username to get the user ID!")
  bot.register_next_step_handler(msg, userid)
def userid(m):
  try: 
    url = requests.get(f'https://api.roblox.com/users/get-by-username?username={m.text}')
    text = url.text
    data = json.loads(text)
    userid = data['Id']
    bot.send_message(m.chat.id, f'User ID of {m.text} is {userid}')
  except:
    bot.send_message(m.chat.id, 'An error occured. Please send the correct username in the correct format.')  

@bot.message_handler(commands='game')
def games(m):
  msg = bot.send_message(m.chat.id, "Send me the user's username to search for a game created by the user.")
  bot.register_next_step_handler(msg, searchgames)
def searchgames(m):
  url = requests.get(f'https://api.roblox.com/users/get-by-username?username={m.text}')
  text = url.text
  data = json.loads(text)
  user = data
  userid = user['Id']
  url = requests.get(f'https://games.roblox.com/v2/users/{userid}/games')
  text = url.text
  data = json.loads(text)
  name = data['data'][0]['name']
  description = data['data'][0]['description']
  visits = data['data'][0]['placeVisits']
  bot.send_message(m.chat.id, f"Here's a game created by {m.text}\n\n<b>{name}</b>\n<i>{description}</i>\n\nVisits: {visits}", parse_mode='HTML')
   
@bot.message_handler(commands='reply')
def reply(m):
  if m.chat.id == -1001789761801:
    msg = bot.send_message(-1001789761801, 'Send the ID followed by message with an underscore between them.')
    bot.register_next_step_handler(msg, replytouser)
  else:
    bot.send_message(m.chat.id, "Sorry, you can't use this command.")
def replytouser(m):
  text = m.text
  ID = text.rpartition('_')[0]
  message = text.rpartition('_')[2]
  bot.send_message(int(ID), f'{message}')
  bot.send_message(-1001789761801, 'Message has been sent.')

@bot.message_handler(func=lambda message: True)
def get(m):
  bot.send_message(-1001789761801, 
f"{m.chat.id} \n{m.from_user.first_name} sent a message:")
  bot.send_message(-1001789761801, m.text)
    
keep_alive()
bot.infinity_polling()
