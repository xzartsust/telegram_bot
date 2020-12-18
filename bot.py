import asyncio
import logging
import os
import time
from threading import Timer

import telebot
from prettyprinter import pprint
from telebot import types

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

token = os.environ.get('TOKEN')

bot = telebot.TeleBot(token)

@bot.message_handler(commands = ['start'], content_types = ['text'])
def send_welcome(message):
    print(message.chat.id)
    if message.chat.id != -1001438428804: #поміняти айди чата на той який буде 
        bot.send_message(message.chat.id, '''
        Привет! Напиши команду /request что бы подать заявку на вступления 
        ''')

@bot.message_handler(commands = ['admin'])
def admin(message):
    if message.from_user.id == 618042376:
        print(message)
    else:
        bot.send_message(message.chat.id, "Эту команду может использовать только создатель")

@bot.message_handler(commands = ['request'])
def send_request(message):
    
    global user_id
    global delete
    user_id = message.from_user.id



    markup_inline = types.InlineKeyboardMarkup()
    item_yes = types.InlineKeyboardButton(text = 'Принять', callback_data = 'yes')
    item_no = types.InlineKeyboardButton(text = 'Отказать', callback_data = 'no')
    markup_inline.add(item_yes, item_no)

    data = time.ctime(message.date)
        
        #поміняти айди чата на той який буде
    delete = bot.send_message(-1001438428804, f''' 
    Запрос на вступелния в групу от пользователя @{message.from_user.username}

ID: {message.from_user.id}
Name: {message.from_user.first_name}
Дата запроса: {data}

На голосование 20 мин.
    ''', 
    reply_markup = markup_inline
        )
    if message.chat.id != -1001438428804: #поміняти айди чата на той який буде 
        bot.send_message(message.chat.id, '''
        Заявка на вступления была направлена на рассмотрение. Ожидайте!
        ''')
    
    Timer(10, check).start()
    
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
    
    print('Y', yes)
    print('N', no)

def check():
    
    if yes['yes'] > no['no']:
        
        bot.send_message(user_id, f'Поздравляем, Вас приняли в группу, вот ваша ссылка на присоидинения:\n\nhttps://t.me/joinchat/JNaUCFW8roRlP7to1nfM5A')
        bot.delete_message(-1001438428804, message_id = delete.id) #поміняти айди чата на той який буде 
        
        yes.clear()
        no.clear()
        yes.update({'yes': 0})
        no.update({'no': 0})

        print('Y', yes)
        print('N', no)
    
    elif yes['yes'] < no['no']:
        
        bot.send_message(user_id, 'Ех... Вам отказали')
        bot.delete_message(-1001438428804, message_id = delete.id) #поміняти айди чата на той який буде 
        
        yes.clear()
        no.clear()
        yes.update({'yes': 0})
        no.update({'no': 0})

        print('Y', yes)
        print('N', no)
    
    elif yes['yes'] == no['no']:
        
        bot.delete_message(-1001438428804, message_id = delete.id) #поміняти айди чата на той який буде 
        bot.send_message(user_id, 'Голосующие не приняли единое мнение, попробуйте еще раз направить запрос')
    
        

if __name__ == "__main__":
    bot.polling(none_stop = True, interval = 0)