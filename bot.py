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

yes = {'yes': 0}
no = {'no': 0}

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

def create_button(text1, text2):
    button = types.InlineKeyboardMarkup()
    button.add(types.InlineKeyboardButton(text = text1, callback_data = 'yes'), types.InlineKeyboardButton(text = text2, callback_data = 'no'))
    return button

@bot.message_handler(commands = ['request', 'Запрос', 'запрос'])
def send_request(message):
    
    global user_data
    global delete

    try:
        
        user_data = message.from_user

        cursor.execute(f'SELECT user_id FROM public."main_BD" WHERE user_id = \'{user_data.id}\';')
        userinbd = cursor.fetchone()
        conn.commit()

        #поміняти айди чата на той який буде
        if message.chat.id != -1001366701849 and userinbd is None:
            delete = bot.send_message(-1001366701849, f''' 
        Запрос на вступ в групу від чмиря @{message.from_user.username}

    Поганяло: {message.from_user.first_name}

На роздуплення 10 хв.''', reply_markup = create_button('Хай буде','Пашол нахуй'))

            bot.send_message(message.chat.id, '''
            Заявка на вступления была направлена на рассмотрение. Ожидайте!
            ''')
            cursor.execute(f'INSERT INTO public."main_BD"(user_id) VALUES (\'{user_data.id}\');')
            conn.commit()
            
            Timer(600, check).start()
            
        else:
            bot.send_message(message.chat.id, '''Ви вже відправили заявку''')
    
    except Exception as e:
        bot.send_message(618042376, f'Ошибка в send_request: {e}')
    

@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):

    global user_data

    if call.data == 'yes':
        yes.update({'yes': yes['yes'] + 1})
        y1 = yes['yes']
        n1 = no['no']
        
        bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = f''' 
        Запрос на вступ в групу від чмиря @{user_data.username}

    Поганяло: {user_data.first_name}

На роздуплення 10 хв.''',
            reply_markup = create_button(f'Хай буде {y1}', f'Пашол нахуй {n1}'),
            parse_mode = 'Markdown')
        

    elif call.data == 'no':
        no.update({'no': no['no'] + 1})
        y2 = yes['yes']
        n2 = no['no']

        bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = f''' 
        Запрос на вступ в групу від чмиря @{user_data.username}

    Поганяло: {user_data.first_name}

На роздуплення 10 хв.''',
            reply_markup = create_button(f'Хай буде {y2}', f'Пашол нахуй {n2}'),
            parse_mode = 'Markdown')
    
    #print('Y', yes)
    #print('N', no)

def check():
    try:
        if yes['yes'] > no['no']:
        
            bot.send_message(user_data.id, f'🎉 Вітаю 🎉\nБагато не вийобуйся бо кікнемо 🤡🤡🤡\nПроявляйте актив.\n\n[Тикай сюда долбоеб](https://t.me/joinchat/KkYqCRiVvkdluMTmPY7kIQ)', parse_mode = 'Markdown')
            bot.delete_message(-1001366701849, message_id = delete.id) #поміняти айди чата на той який буде 
        
            yes.clear()
            no.clear()
            yes.update({'yes': 0})
            no.update({'no': 0})
    
        elif yes['yes'] < no['no']:
        
            bot.send_message(user_data.id, 'Ех... Ви пішли нахуй!!!')
            bot.delete_message(-1001366701849, message_id = delete.id) #поміняти айди чата на той який буде 
        
            yes.clear()
            no.clear()
            yes.update({'yes': 0})
            no.update({'no': 0})
    
        elif yes['yes'] == no['no']:
        
            bot.delete_message(-1001366701849, message_id = delete.id) #поміняти айди чата на той який буде 
            bot.send_message(user_data.id, 'Міша, всьо хуйня, давай поновой')
            
            yes.clear()
            no.clear()
            yes.update({'yes': 0})
            no.update({'no': 0})
            
            cursor.execute(f'DELETE FROM public."main_BD" WHERE user_id = \'{user_data.id}\';')
            conn.commit()
    
    except Exception as e:
        print(f'Ошибка в check: {e}')
        

if __name__ == "__main__":
    bot.polling(none_stop = True, interval = 0)
