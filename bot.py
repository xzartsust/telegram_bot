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
        
    Також можете після команди /request написати повідомлення яке побачать всі в чаті
    Приклад: /request прийміть будь ласка!
        ''')

@bot.message_handler(commands = ['admin'])
def admin(message):
    
    if message.from_user.id == 618042376:
        print(f'\nMessage.chat: {message.chat}\n')
        print(f'Message: {message}\n')
    else:
        bot.send_message(message.chat.id, 'Эту команду может использовать только создатель')

def create_button(text1, text2):
    button = types.InlineKeyboardMarkup()
    button.add(types.InlineKeyboardButton(text = text1, callback_data = 'yes'), types.InlineKeyboardButton(text = text2, callback_data = 'no'))
    return button

@bot.message_handler(commands = ['request', 'Запрос', 'запрос'])
def send_request(message):
    
    global user_data
    global delete
    global text
    global l

    try:
        
        user_data = message.from_user

        cursor.execute(f'SELECT user_id FROM public."main_BD" WHERE user_id = \'{user_data.id}\';')
        userinbd = cursor.fetchone()
        conn.commit()

        text = message.text.split()
        l = int(len(text))
        
        if message.chat.id != -1001366701849 and userinbd is None and len(text) != 1:
            delete = bot.send_message(-1001366701849, f''' 
        Запрос на вступ в групу від чмиря @{message.from_user.username}

    Поганяло: {message.from_user.first_name}
    Пизданув: {' '.join(text[1:l])}

На роздуплення 10 хв.''', reply_markup = create_button('Хай буде','Пашол нахуй'))

            bot.send_message(message.chat.id, 'Заявка на вступления была направлена на рассмотрение. Ожидайте!')
            cursor.execute(f'INSERT INTO public."main_BD"(user_id) VALUES (\'{user_data.id}\');')
            conn.commit()
            
            Timer(600, check).start()
            
            bot.send_message(618042376, f''' 
        Запрос на вступ в групу від чмиря @{message.from_user.username}

    Поганяло: {message.from_user.first_name}''')

            bot.send_message(message.chat.id, '''
            Заявка на вступления была направлена на рассмотрение. Ожидайте!
            ''')
        elif len(text) == 1 and userinbd is None:

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
            
            bot.send_message(message.chat.id, 'Ви вже відправили заявку')
            bot.send_message(618042376, f'Питається знову надіслати запрос @{message.from_user.username}')
    
    except Exception as e:
        bot.send_message(618042376, f'Ошибка в send_request: {e}')
    

@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):

    global user_data

    if call.data == 'yes':
        
        cursor.execute(f'SELECT user_id_vote_yes FROM public."vote" WHERE user_id_vote_yes = \'{call.from_user.id}\';')
        y = cursor.fetchone()
        conn.commit()
        
        cursor.execute(f'SELECT user_id_vote_no FROM public."vote" WHERE user_id_vote_no = \'{call.from_user.id}\';')
        n = cursor.fetchone()
        conn.commit()


        if y is None and n is None and len(text) != 1:
            yes.update({'yes': yes['yes'] + 1})
            y1 = yes['yes']
            n1 = no['no']
        
            bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                text = f''' 
        Запрос на вступ в групу від чмиря @{user_data.username}

    Поганяло: {user_data.first_name}
    Пизданув: {' '.join(text[1:l])}

На роздуплення 10 хв.''',
                reply_markup = create_button(f'Хай буде {y1}', f'Пашол нахуй {n1}'))
            
            cursor.execute(f'INSERT INTO public."vote" (user_id_vote_yes) VALUES (\'{call.from_user.id}\');')
            conn.commit()
        
        elif y is None and n is None and len(text) == 1:

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
                reply_markup = create_button(f'Хай буде {y1}', f'Пашол нахуй {n1}'))
            
            cursor.execute(f'INSERT INTO public."vote" (user_id_vote_yes) VALUES (\'{call.from_user.id}\');')
            conn.commit()
        
        else:
            bot.answer_callback_query(call.id, text = 'Ееее, куда нах ти вже проголосував', show_alert = True)
    
    elif call.data == 'no':
        
        cursor.execute(f'SELECT user_id_vote_yes FROM public."vote" WHERE user_id_vote_yes = \'{call.from_user.id}\';')
        y1 = cursor.fetchone()
        conn.commit()
        
        cursor.execute(f'SELECT user_id_vote_no FROM public."vote" WHERE user_id_vote_no = \'{call.from_user.id}\';')
        n1 = cursor.fetchone()
        conn.commit()
        
        if y1 is None and n1 is None and len(text) != 1:
            
            no.update({'no': no['no'] + 1})
            y2 = yes['yes']
            n2 = no['no']

            bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                text = f''' 
        Запрос на вступ в групу від чмиря @{user_data.username}

    Поганяло: {user_data.first_name}
    Пизданув: {' '.join(text[1:l])}

На роздуплення 10 хв.''',
                reply_markup = create_button(f'Хай буде {y2}', f'Пашол нахуй {n2}'))
            
            cursor.execute(f'INSERT INTO public."vote" (user_id_vote_no) VALUES (\'{call.from_user.id}\');')
            conn.commit()
        
        elif y1 is None and n1 is None and len(text) == 1:
            
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
                reply_markup = create_button(f'Хай буде {y2}', f'Пашол нахуй {n2}'))
            
            cursor.execute(f'INSERT INTO public."vote" (user_id_vote_no) VALUES (\'{call.from_user.id}\');')
            conn.commit()
        
        else:
            bot.answer_callback_query(call.id, text = 'Ееее, куда нах ти вже проголосував', show_alert = True)


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

            cursor.execute(f'DELETE FROM public."vote";')
            conn.commit()            
    
        elif yes['yes'] < no['no']:
        
            bot.send_message(user_data.id, 'Ех... Ви пішли нахуй!!!')
            bot.delete_message(-1001366701849, message_id = delete.id) #поміняти айди чата на той який буде 
        
            yes.clear()
            no.clear()
            yes.update({'yes': 0})
            no.update({'no': 0})

            cursor.execute(f'DELETE FROM public."vote";')
            conn.commit()
    
        elif yes['yes'] == no['no']:
        
            bot.delete_message(-1001366701849, message_id = delete.id) #поміняти айди чата на той який буде 
            bot.send_message(user_data.id, 'Міша, всьо хуйня, давай поновой')
            
            yes.clear()
            no.clear()
            yes.update({'yes': 0})
            no.update({'no': 0})

            cursor.execute(f'DELETE FROM public."vote";')
            conn.commit()
            
            cursor.execute(f'DELETE FROM public."main_BD" WHERE user_id = \'{user_data.id}\';')
            conn.commit()
    
    except Exception as e:
        print(f'Ошибка в check: {e}')
        

if __name__ == "__main__":
    bot.polling(none_stop = True, interval = 0)
