#!/usr/bin/python

# -*- coding: utf8 -*-

from mysql.connector import MySQLConnection, Error
import mysql.connector
from config import TOKEN, price_1
import telebot
from telebot import types
import datetime
from pprint import pprint
from config import client, host, USER, passwd, database, port, ADMIN
import time


month = 600
six_month = 3240
one_year = 5760



def get_user_info(tlg_id):
    print(tlg_id)
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    cursor.execute("SELECT * from users WHERE telegram_id=" + str(tlg_id))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def listener(messages):

    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) +
                  " [" + str(m.chat.id) + "]: " + m.text)

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
bot.set_update_listener(listener)





def add_new_referer(main_ref,invited_ref, level ):
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    select = 'SELECT * from refers WHERE main_ref ='+str(main_ref)+' and invited_ref=' + str(invited_ref)
    cursor.execute(select)
    users = cursor.fetchall()
    if not users:
        sql = 'INSERT INTO refers (main_ref, invited_ref, level) VALUES (%s, %s, %s)'
        val = (main_ref,invited_ref, level)
        cursor.execute(sql, val)
        conn.commit()
        add_subrefers(main_ref, invited_ref)
    cursor.close()
    conn.close()


def if_main_ref_is_referer(main_ref):

    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    # print('main_ref=',main_ref)
    if main_ref:
        select = 'SELECT * from refers WHERE invited_ref='+str(main_ref)
        cursor.execute(select)
        users = cursor.fetchall()
        # print('users=', users)
    else:
        users= []
    cursor.close()
    conn.close()
    return users



def add_subrefers(user, invited_ref):
    user1 = []
    user1.append(if_main_ref_is_referer(user))
    # print('user1')
    # pprint(user1)

    user2 = []
    user3 = []
    user4 = []
    user5 = []
    user6 = []
    for u1 in user1:
        for u in u1:
            m1 = if_main_ref_is_referer(u[1])
            user2.append(m1)  # +2
    # print('user2',)
    # pprint(user2)

    for u2 in user2:
        for u in u2:
            user3.append(if_main_ref_is_referer(u[1]))
    # pprint(user3)

    for u3 in user3:
        for u in u3:
            user4.append(if_main_ref_is_referer(u[1]))
    # pprint(user4)

    for u4 in user4:
        for u in u4:
            user5.append(if_main_ref_is_referer(u[1]))
    # pprint(user5)

    for u5 in user5:
        for u in u5:
            user6.append(if_main_ref_is_referer(u[1]))
    pprint(user6)

    insert_subrefer(user1, invited_ref,1)
    insert_subrefer(user2, invited_ref,2)
    insert_subrefer(user3, invited_ref,3)
    insert_subrefer(user4, invited_ref,4)
    insert_subrefer(user5, invited_ref,5)
    insert_subrefer(user6, invited_ref,6)



def insert_subrefer(users, invited_ref, plus):
    if len(users)>0:
        conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
        cursor = conn.cursor()
        for refer in users:
           for r in refer:
               if r[1]!=None:
                    sql = 'SELECt * from refers WHERE main_ref='+str(r[1])+' and invited_ref='+str(invited_ref)
                    cursor.execute(sql)
                    s = cursor.fetchall()
                    if len(s)==0:
                        insert = 'INSERT INTO refers (main_ref, invited_ref, level) VALUES (%s, %s, %s)'
                        val = (r[1], invited_ref, int(r[3])+plus)
                        cursor.execute(insert, val)
                        conn.commit()
        cursor.close()
        conn.close()


@bot.message_handler(commands=['start'])
def command_start(m):

    cid = m.chat.id
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id=" + str(cid))
    users = cursor.fetchall()
    now = datetime.datetime.now()
    if len(users) == 0:
        sql = 'INSERT INTO users (telegram_id, data_reg) VALUES (%s, %s)'
        val = (m.chat.id, now)
        cursor.execute(sql, val)
        conn.commit()

        if ' ' in  m.text:
            referrer_id = m.text.split(' ')[1]
            add_new_referer(referrer_id, m.chat.id, 1)
        else:
            sql = 'INSERT INTO refers (invited_ref) VALUES ('+str(m.chat.id)+')'

            cursor.execute(sql)
            conn.commit()


    hello_text = """Привет, @""" + str(get_username(m)) + """!
Рады тебя приветствовать в нашем боте IZZZZZI. 

Простой сервис с подсказками и поддержкой 24/7 позволит тебе сформировать готовый инвестиционный портфель (набор акций), собранный из активов различных компаний. Более того, мы с тобой будем формировать не только портфель, но и получать дивиденды от этих самых компаний!

Для того, чтобы тебе было легче инвестировать нужную сумму, у нас есть партнерская программа. 

При покупке подписки мы делимся с тобой, твоими друзьями и другими приглашенными пользователями процентом от стоимости тарифа нашего бота, распределяя его на 7 уровней в глубину. Переходи в меню и знакомься с каждым пунктом подробнее, а если будут вопросы смело пиши @izzzzzi_support_bot 
"""

    bot.send_message(m.chat.id, text=hello_text, reply_markup=key_start(),parse_mode='html' )

def key_start():
    keyboard_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_start.row(types.KeyboardButton(text='Обучение'), types.KeyboardButton(text='Баланс'))
    keyboard_start.row(types.KeyboardButton(text='Пригласить друзей'), types.KeyboardButton(text='Структура'))
    keyboard_start.row(types.KeyboardButton(text='Вывод средств'), types.KeyboardButton(text='Марафон'))
    return keyboard_start


def get_username(m):
    print(m)
    if m.chat.username == None:
        username = m.chat.first_name
    else:
        username = m.chat.username
    return username


@bot.message_handler(commands=['marathon'])
def marafon(m):
    marathon(m)


@bot.message_handler(func=lambda message: message.text == "Марафон")
def marathon(m):
    message_text='''
    Наш сервис ежемесячно проводит марафон по количеству приглашенных друзей среди пользователей нашего бота и награждает дополнительно лучшую 10-ку пользователей денежными призами. 

С 10 по 4 место - 200 рублей
3 место - 500 рублей
2 место - 800 рублей
1 место - 1000 рублей.

Приглашая своих друзей в бот, ты автоматически становишься участником марафона. Считаются только друзья с оплаченной подпиской. Тебе нужно пригласить как можно больше новых пользователей по персональной ссылке.

Имена лучших ты видишь ниже по списку в режиме реального времени. Награждаем каждый месяц 1 числа, затем 2 числа счетчик обновляет список и марафон начинается заново.

1 место @name 100 друзей
2 место @name 99 друзей
3 место @name 80 друзей
4 место @name 10 друзей
5 место @name 6 друзей
6 место @name 5 друзей
7 место @name 1 друзей
8 место @name 1 друзей 
9 место @name 0 друзей
10 место @name 0 друзей

Внимание! Мы не просим пользователей делать никаких переводов перед получением денежного подарка. Этим занимаются только мошенники. 1 числа каждого месяца @Izzzzzi_admin пишет победителям и переводит денежные подарки. Будьте внимательнее!
    '''
    bot.send_message(m.chat.id, text=message_text)


@bot.message_handler(commands=['training'])
def training(m):
    study(m)


@bot.message_handler(func=lambda message: message.text == "Обучение")
def study(m):

        # print('hello')
        message_text = """@"""+str(get_username(m))+""", Перед началом предлагаем ознакомиться с основными функциями нашего бота.  Переходи по ссылке - там все подробно рассказали. https://izzzzzi.tb.ru/ 

Ссылка на оплату в платёжную систему, Оплатить 600 рублей.
Добро пожаловать к нам в команду! Теперь внимательно следи за нашими инвестиционными сигналами в боте, приглашай друзей и следуй нашим рекомендациям, подробнее о которых мы написали на сайте.
"""
        bot.send_message(
            m.chat.id, text=message_text, reply_markup=key_pay(), parse_mode='html')

@bot.message_handler(commands=['balance'])
def balance(m):
    get_balance(m)


@bot.message_handler(func=lambda message: message.text == "Баланс")
def get_balance(m):
   # print(m.chat.id)
    pays = get_user_info(m.chat.id)
    # print(pays)
    for pay in pays:
        b = pay[4]
    message_text = 'Твой баланс ' + str(b) + ' ₽'
    bot.send_message(m.chat.id, text=message_text,  parse_mode='html')

@bot.message_handler(commands=['structure'])
def structura(m):
    get_strctur(m)


@bot.message_handler(func=lambda message: message.text == "Структура")
def get_strctur(m):
    sql = 'SELECT * FROM refers WHERE main_ref='+str(m.chat.id)
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    cursor.execute(sql)
    struct = cursor.fetchall()
    cursor.close()
    conn.close()
    s1=0
    s2=0
    s3=0
    s4=0
    s5=0
    s6=0
    s7=0
    for s in struct:
        if s[3] == 1:
            s1=s1+1
        if s[3]==2:
            s2=s2+1
        if s[3]==3:
            s3=s3+1
        if s[3]==4:
            s4=s4+1
        if s[3]==5:
            s5=s5+1
        if s[3]==6:
            s6=s6+1
        if s[3]==7:
            s7=s7+1

    msg_text = 'Это твоя структура. Здесь отображаются все приглашенные тобой и твоими друзьями пользователи до 7 уровня.'
    msg_text = msg_text + '\n \n Твои друзья - '+str(s1)+'\n 2 Уровень - ' +str(s2)+'\n 3 Уровень - ' +str(s3) + '\n 4 Уровень - ' + str(s4) + '\n 5 Уровень - ' +str(s5)+'\n 6 Уровень - ' +str(s6) + '\n 7 Уровень - ' +str(s7)
    balance = get_user_info(m.chat.id)
    for b in balance:
        bal = b[4]
    msg_text = msg_text + '\n \n  Кстати, за все время тобой заработано в нашем боте - '+ str(bal) +' ₽ '
    bot.send_message(m.chat.id, text=msg_text,  parse_mode='html')
    pprint(struct)

@bot.message_handler(commands=['invite'])
def share(m):
    get_link(m)

@bot.message_handler(func=lambda message: message.text == "Пригласить друзей")
def get_link(m):
    sql = 'SELECT * from refers WHERE main_ref = '+str(m.chat.id)+' and level=1'
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    link = '<a href = "t.me/qwwedebot?start='+str(m.chat.id)+'">ссылка</a>'
    message_text = 'Твоя ссылка ' + link + ' чтобы пригласить друзей, ты можешь поделиться ей в любых социальных сетях. Важно, чтобы в нашего бота перешли именно по твоей персональной ссылке. Для этого необходимо, чтобы у друга был установлен Telegram.'

    message_text = message_text + '\n \n Сейчас ты пригласил ' +str(len(data)) + 'друзей 🙂. '

    friends_list =''
    for d in data:
        userid = int(d[2])
        UsrInfo = bot.get_chat_member(userid, userid).user
        print(UsrInfo.username)
        friends_list = friends_list + ' @' + str(UsrInfo.username)
    message_text = message_text + '\n\n Здесь отображаются приглашенные лично тобой друзья, которые активировали бота, оплатив подписку. \n' +friends_list
    bot.send_message(
            m.chat.id, text=message_text,  parse_mode='html')

@bot.message_handler(commands=['withdrawal'])
def withdrawal(m):
    get_money(m)

@bot.message_handler(func=lambda message: message.text == "Вывод средств")
def get_money(m):
    data = get_user_info(m.chat.id)
    # print(data)
    for d in data:
        balance = d[4]
        card = d[6]
    message_text = '''Наш сервис выводит весь баланс, который у тебя есть на данный момент. Ограничение платежной системы по выводу от 100 рублей. Если баланс меньше 100 рублей, мы не сможем выполнить вывод.
Если твой баланс больше 100 рублей, нажимай подтвердить "Да".  Если ты выводишь средства в первый раз, тебе необходимо написать в диалог с ботом номер своей карты. Подойдут  Visa/MasterCard/MIR.
Перевод осуществляется в ручном режиме с 10.00 до 21.00 по МСК в течение первых двух часов с момента подтверждения заявки.
Сервис не несет ответственности за перевод по неправильным реквизитам.'''


    if balance < 100:
        message_text += '\n\n Ваш баланс составляет менее 100 ₽, пока нечего выводить'
        bot.send_message(m.chat.id, text=message_text, parse_mode='html')
    else:
        if card == None:
            message_text += '\n\nВаш баланс составляет '+str(balance)+' ₽ \n К вашему аккаунту не привязана пока еще ни одна карта.\n Хотите привязать?'
            bot.send_message(m.chat.id, text=message_text, parse_mode='html', reply_markup=add_card())

        else:
            message_text += '\n\nВаш баланс составляет '+str(balance)+'₽ \n К Вашему номеру привязана карта № '+str(card)+'\n Все верно?'
            bot.send_message(m.chat.id, text=message_text, reply_markup=send_money())


def send_money():
    keyboard_send = types.InlineKeyboardMarkup()
    send_yes = types.InlineKeyboardButton(text='Да', callback_data='send_pay_data')
    send_correct = types.InlineKeyboardButton(text='Изменить данные карты', callback_data='get_user_card')
    keyboard_send.add(send_yes,send_correct)
    return (keyboard_send)



def add_card():
    keyboard_card = types.InlineKeyboardMarkup()
    card_yes = types.InlineKeyboardButton(text='да', callback_data='get_user_card')
    card_no = types.InlineKeyboardButton(text='нет', callback_data='not_add_card_number')
    keyboard_card.add(card_yes,card_no)
    return  keyboard_card




def key_pay():
    keyboard_pay = types.InlineKeyboardMarkup(row_width=1)
    pay1 = types.InlineKeyboardButton(
        text='Подписка на месяц 600₽', callback_data='addpay_month')
    pay2 = types.InlineKeyboardButton(
        text='Подписка на пол года  3240 (скидка 10%', callback_data='addpay_6month')
    pay3 = types.InlineKeyboardButton(
        text='Подписка на год  5760 (скидка 20%', callback_data='addpay_year')
    keyboard_pay.add(pay1,pay2).row(pay3)

    return keyboard_pay


def send_user_money():
    keyboard_send_money = types.InlineKeyboardMarkup()
    send = types.InlineKeyboardButton(text='Выслал, обнулить баланс', callback_data='выслал')


def payment_link( desc, chat_id, summ):

    keyboard_pay_link = types.InlineKeyboardMarkup()
    link = types.InlineKeyboardButton(text='оплатить '+str(summ), url=client.generate_payment_link(
        order_id=desc, summ=summ,  description=chat_id))
    keyboard_pay_link.add(link)
    return keyboard_pay_link


def add_pay_history(u_id_pay, pay_sum):
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    sql = 'INSERT INTO pay_history (u_id_pay, pay_sum) VALUES ('+u_id_pay+', '+pay_sum+')'
    cursor.execute(sql)
    conn.commit()


def select_max_pay_id():
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    cursor.execute("SELECT max(id) FROM pay_history")
    desc = cursor.fetchone()
    desc = desc[0]
    return desc

def clear_balance(tlg_id):
    sql = "UPDATE users SET  balance = 0 WHERE telegram_id =" + tlg_id
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()


#call-answers################################################################################################################
@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()

    if call.data == 'send_pay_data':
        # print(call.message)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,  text='Спасибо, получили твои данные. Ожидай выплату!')
        # print(call.message.chat.username)

        data = get_user_info(call.message.chat.id)
        for dat in data:
            balance = dat[4]
            cart = dat[6]
            tlg_id = dat[1]
        bot.send_message(ADMIN, text='@'+get_username(call.message)+', tlg№ '+str(tlg_id)+' хочет вывести средства, на его счету '+str(balance)+'₽. К аккаунту привязана карта № '+str(cart)+'')
        clear_balance(tlg_id)

    if call.data == 'addpay_month':
        add_pay_history(call.message.chat.id, month)
        desc = select_max_pay_id()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=payment_link(desc, call.message.chat.id, month))

    if call.data == 'addpay_six_month':
        add_pay_history(call.message.chat.id, six_month)
        desc = select_max_pay_id()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=payment_link(desc, call.message.chat.id, six_month))

    if call.data == 'addpay_year':
        add_pay_history(call.message.chat.id, one_year)
        desc = select_max_pay_id()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=payment_link(desc, call.message.chat.id, six_month))

    if call.data == 'get_user_card':
        message_text = 'Введите номер карты и нажмите отправить'

        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id, text=message_text, parse_mode='MarkDown')
        # print('msg = ',msg)
        bot.register_next_step_handler(msg, add_user_card)


    cursor.close()
    conn.close()


def add_user_card(m):
    # print(m.chat.id)
    n_cart = m.text
    conn = mysql.connector.connect(host=host, user=USER, passwd=passwd, port=port, database=database)
    cursor = conn.cursor()
    sql = "UPDATE users SET  card = '" + str(n_cart) + "' WHERE telegram_id =" + str(m.chat.id)
    cursor.execute(sql)
    conn.commit()
    message_text = 'Ваша карта №' + n_cart + ' добавлена, можно выводить'
    bot.send_message(m.chat.id, text=message_text, parse_mode='MarkDown')


# if __name__ == '__main__':
#
#     while True:
#         try:
#             bot.polling(none_stop=True)
#         except Exception as e:
#             time.sleep(3)
#             print(e)

if __name__ == '__main__':

    while True:
        bot.polling(none_stop=True)