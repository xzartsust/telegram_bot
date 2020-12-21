import asyncio
import logging
import os
import time
from threading import Timer

import asyncpg
import psycopg2
import telebot
from prettyprinter import pprint
from telebot import types

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

token = os.environ.get('TOKEN')

bot = telebot.TeleBot(token)

database = os.environ.get('DATABASE')
user = os.environ.get('USER')
password = os.environ.get('PASSWORD')
host = os.environ.get('HOST')
port = os.environ.get('PORT')

conn = psycopg2.connect(
    database = f"{database}", 
    user = f"{user}", 
    password = f"{password}", 
    host = f"{host}", 
    port = "5432"
)

cursor = conn.cursor()

@bot.message_handler(commands = ['start', 'старт', 'Старт'], content_types = ['text'])
def send_welcome(message):
    
    if message.chat.id != -1001366701849: #поміняти айди чата на той який буде 
        bot.send_message(message.chat.id, '''
        Привет! Напиши команду /request что бы подать заявку на вступления 
        ''')

@bot.message_handler(commands = ['admin'])
def admin(message):
    
    if message.from_user.id == 618042376:
        print(f'\nMessage.chat: {message.chat}\n')
        print(f'Message: {message}\n')
    else:
        bot.send_message(message.chat.id, "Эту команду может использовать только создатель")

@bot.message_handler(commands = ['request', 'Запрос', 'запрос'])
def send_request(message):
    
    global user_id
    global delete
    
    try:
        user_id = message.from_user.id

        markup_inline = types.InlineKeyboardMarkup()
        item_yes = types.InlineKeyboardButton(text = 'Хай буде', callback_data = 'yes')
        item_no = types.InlineKeyboardButton(text = 'Пашол нахуй', callback_data = 'no')
        markup_inline.add(item_yes, item_no)
        
        #поміняти айди чата на той який буде
        if message.chat.id != -1001366701849:
            delete = bot.send_message(-1001366701849, f''' 
        Запрос на вступ в групу від чмиря @{message.from_user.username}

    Поганяло: {message.from_user.first_name}

На роздуплення 10 хв.
''', # змітини потом в Timer час на той який скажуть так само в описі поставити
            reply_markup = markup_inline
                )

        if message.chat.id != -1001366701849: #поміняти айди чата на той який буде 
            bot.send_message(message.chat.id, '''
            Заявка на вступления была направлена на рассмотрение. Ожидайте!
            ''')
    
        Timer(600, check).start()
    
    except Exception as e:
        bot.send_message(618042376, f'Ошибка в send_request: {e}')
    
    #bot.send_message(-1001438428804, "Вы уже отправили запрос, ждите!")
    #print('Mass users:', users)
    
yes = {'yes': 0}
no = {'no': 0}

@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
    
    if call.data == 'yes':
        yes.update({'yes': yes['yes'] + 1})

    elif call.data == 'no':
        no.update({'no': no['no'] + 1})
    
    #print('Y', yes)
    #print('N', no)

def check():
    try:
        if yes['yes'] > no['no']:
        
            bot.send_message(user_id, f'🎉 Вітаю 🎉\nБагато не вийобуйся бо кікнемо 🤡🤡🤡\nПроявляйте актив.\n\n[Тикай сюда долбоеб](https://t.me/joinchat/KkYqCRiVvkdluMTmPY7kIQ)', parse_mode = 'Markdown')
            bot.delete_message(-1001366701849, message_id = delete.id) #поміняти айди чата на той який буде 
        
            yes.clear()
            no.clear()
            yes.update({'yes': 0})
            no.update({'no': 0})
    
        elif yes['yes'] < no['no']:
        
            bot.send_message(user_id, 'Ех... Ви пішли нахуй!!!')
            bot.delete_message(-1001366701849, message_id = delete.id) #поміняти айди чата на той який буде 
        
            yes.clear()
            no.clear()
            yes.update({'yes': 0})
            no.update({'no': 0})
    
        elif yes['yes'] == no['no']:
        
            bot.delete_message(-1001366701849, message_id = delete.id) #поміняти айди чата на той який буде 
            bot.send_message(user_id, 'Міша, всьо хуйня, давай поновой')
    
    except Exception as e:
        print(f'Ошибка в check: {e}')
        

if __name__ == "__main__":
    bot.polling(none_stop = True, interval = 0)
