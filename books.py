import os
import sqlite3
import logging
import telebot
from telebot import apihelper
from os import system as cmd

'''
Make sure to install the modified uploadgram package in superuser mode 
just hit " pip3 install https://github.com/konichiwa55115/uplsd5asd165/archive/refs/heads/master.zip " 
if you would make a docker image for bot to run it as a container on a platform , just add the same command in DockerFile prefixed by "RUN"
by : @AbuMarhtad
'''

BOT_TOKEN = '7161213878:AAEmTchEaToD8NgEBy_eZi6VDxVQ7lIu278'
apihelper.API_URL = 'http://api.telegram.org/bot{0}/{1}'
bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect('books.db', check_same_thread=False, timeout=10)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS books
             (id INTEGER PRIMARY KEY, bookid TEXT,book_unique_id TEXT, bookname TEXT)''')
conn.commit()



@bot.message_handler(commands=['start', 'hello'])
def start(message):
    bot.reply_to(message, "السلام عليكم ورحمة الله وبركاته \n أنا بوت البحث عن الكتب \n فقط أرسل اسم الكتاب  \n لبقية البوتات \n https://t.me/sunnaybots/2",disable_web_page_preview=True)

@bot.message_handler(commands=['bakcup'])
def start(message):
    cmd(f'''sudo uploadgram -1001821573758 books.db''')


@bot.message_handler(content_types=['text','document'])
@bot.message_handler(func=lambda message: True)
def echo(message):
        global user_id,messagetobedeleted
        user_id = message.from_user.id
        if message.text and user_id != 6234365091 :
            conn_local = sqlite3.connect('books.db', check_same_thread=False)
            c_local = conn_local.cursor()
            if not c_local.execute('SELECT * FROM books WHERE bookname LIKE ?', (f"%{message.text}%",)).fetchall() :
                bot.reply_to(message, "لا يوجد الكتاب في قاعدة البيانات , أرسله فضلاً هنا")
                sentmessage = message.text + " 👇"
                bot.send_message(-1001821573758,  message.text)
            else :
                bookresult = c.execute('SELECT book_unique_id FROM books WHERE bookname LIKE ? ',(f"%{message.text}%",)).fetchall()
                markup = telebot.types.InlineKeyboardMarkup()
                for book_data in bookresult:
                    book_unique_id = book_data[0]
                    book_name = c.execute('SELECT bookname FROM books WHERE book_unique_id=?',(book_unique_id,)).fetchone()[0]
                    markup.add(telebot.types.InlineKeyboardButton(book_name, callback_data=book_unique_id))
                messagetobedeleted = bot.send_message(message.chat.id, "نتائج البحث", reply_markup=markup)


        elif message.text and user_id == 6234365091 :
            conn_local = sqlite3.connect('books.db', check_same_thread=False)
            c_local = conn_local.cursor()
            if not c_local.execute('SELECT * FROM books WHERE bookname LIKE ?', (f"%{message.text}%",)).fetchall() :
                bot.reply_to(message, "لا يوجد الكتاب في قاعدة البيانات , أرسله فضلاً هنا")
            else :
                bookresult = c.execute('SELECT book_unique_id FROM books WHERE bookname LIKE ? ',(f"%{message.text}%",)).fetchall()
                markup = telebot.types.InlineKeyboardMarkup()
                for book_data in bookresult:
                    book_unique_id = book_data[0]
                    book_name = c.execute('SELECT bookname FROM books WHERE book_unique_id=?',(book_unique_id,)).fetchone()[0]
                    markup.add(telebot.types.InlineKeyboardButton(book_name, callback_data=book_unique_id))
                messagetobedeleted = bot.send_message(message.chat.id, "نتائج البحث", reply_markup=markup)
        

        elif message.document and user_id != 6234365091 :
            bot.reply_to(message, "سيتم إضافة الكتاب في أقرب وقت إن شاء الله ")
            bot.send_document(-1001821573758,  message.document.file_id)

        elif message.document and user_id == 6234365091 :
            bot.reply_to(message,'الآن أرسل اسم الكتاب')
            global booktobeadded
            booktobeadded = message
            bot.register_next_step_handler(message, add_book)
            


def add_book(message):
    if check_exist(message.text):
        bot.reply_to(message, "الكتاب موجود بالفعل")
        return
    book_id =  booktobeadded.document.file_id
    book_unique_id =  booktobeadded.document.file_unique_id
    book_name = message.text
    bot.send_document(-1002148408911, book_id)
    c.execute('INSERT INTO books (bookid,book_unique_id,bookname) VALUES (?,?,?)', (book_id,book_unique_id,book_name))
    conn.commit()
    bot.reply_to(message," تمت إضافة الكتاب بنجاح   ")

def check_exist(book_name):
    try:
        res = c.execute('SELECT * FROM books WHERE bookname=?', (book_name,)).fetchone()
        if res:
            return True
        return False
    except Exception as e:
        logging.error(e)
        return False


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    conn_local = sqlite3.connect('books.db', check_same_thread=False)
    c_local = conn_local.cursor()
    book_id = c.execute('SELECT bookid FROM books WHERE book_unique_id=?',(call.data,)).fetchone()[0]
    bot.edit_message_text("تم الإرسال",messagetobedeleted.chat.id,messagetobedeleted.message_id) 
    bot.send_document(user_id, book_id)


bot.polling(non_stop=True, skip_pending=True)
