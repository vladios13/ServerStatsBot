#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tokens import *
import matplotlib
matplotlib.use("Agg") # has to be before any other matplotlibs imports to set a "headless" backend
import matplotlib.pyplot as plt
import psutil
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import operator
import collections
# import sys
import time
# import threading
# import random
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
# from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent



memorythreshold = 85  # Если потребляется больше памяти, то этот % равен:
poll = 300  # значения в секундах

shellexecution = []
timelist = []
memlist = []
xaxis = []
settingmemth = []
setpolling = []
graphstart = datetime.now()

stopmarkup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Stop Shell")]],resize_keyboard=True)
# stopmarkup = {'keyboard': [['Stop']]}
hide_keyboard = {'hide_keyboard': True}

def clearall(chat_id):
    if chat_id in shellexecution:
        shellexecution.remove(chat_id)
    if chat_id in settingmemth:
        settingmemth.remove(chat_id)
    if chat_id in setpolling:
        setpolling.remove(chat_id)

def plotmemgraph(memlist, xaxis, tmperiod):
    # print(memlist)
    # print(xaxis)
    plt.xlabel(tmperiod)
    plt.ylabel('% использовано')
    plt.title('График использования ОЗУ')
    plt.text(0.1*len(xaxis), memorythreshold+2, 'Порог: '+str(memorythreshold)+ ' %')
    memthresholdarr = []
    for xas in xaxis:
        memthresholdarr.append(memorythreshold)
    plt.plot(xaxis, memlist, 'b-', xaxis, memthresholdarr, 'r--')
    plt.axis([0, len(xaxis)-1, 0, 100])
    plt.savefig('/tmp/graph.png')
    plt.close()
    f = open('/tmp/graph.png', 'rb')  # файл изображние на локальном диске
    return f


class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        # Do your stuff according to `content_type` ...
        print("Ваш chat_id:" + str(chat_id)) # узнать chat_id
        if chat_id in adminchatid:  # Переменная adminchatid хранится в tokens.py
            if content_type == 'text':
                if msg['text'] == '/stats' and chat_id not in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    cpuget = psutil.getloadavg()
                    сpu_countF = psutil.cpu_count(logical=False)
                    сpu_countL = psutil.cpu_count(logical=True)
                    cpufr = psutil.cpu_freq(percpu=False)
                    boottime = datetime.fromtimestamp(psutil.boot_time())
                    now = datetime.now()
                    cpuget = "<b>Средняя нагрузка CPU</b>: " + str(cpuget)
                    cpufr = "<b>Текущая частота CPU</b>: " + str(cpufr.current) + "Mhz"
                    сpu_countF = "<b>Физических ядер</b>: " + str(сpu_countF)
                    сpu_countL = "<b>Логических ядер</b>: " + str(сpu_countL)
                    timedif = "<b>Сервер работает уже</b>: %.1f часов" % (((now - boottime).total_seconds()) / 3600)
                    memtotal = "<b>Всего ОЗУ</b>: %.2f GB " % (memory.total / 1000000000)
                    memavail = "<b>Свободно ОЗУ</b>: %.2f GB" % (memory.available / 1000000000)
                    memuseperc = "<b>Используется ОЗУ</b>: " + str(memory.percent) + " %"
                    diskused = "<b>Использовано HDD</b>: " + str(disk.percent) + " %"
                    pidsinf = "<u>Текущие процессы:</u>"

                    pids = psutil.pids()
                    pidsreply = ''
                    procs = {}
                    for pid in pids:
                        p = psutil.Process(pid)
                        try:
                            pmem = p.memory_percent()
                            if pmem > 0.5:
                                if p.name() in procs:
                                    procs[p.name()] += pmem
                                else:
                                    procs[p.name()] = pmem
                        except:
                            print("ХМ?")
                    sortedprocs = sorted(procs.items(), key=operator.itemgetter(1), reverse=True)
                    for proc in sortedprocs:
                        pidsreply += proc[0] + " " + ("%.2f" % proc[1]) + " %\n"
                    reply = timedif + "\n" + \
                            cpuget + "\n" + \
                            cpufr + "\n" + \
                            memtotal + "\n" + \
                            сpu_countF + "\n" + \
                            сpu_countL + "\n" + \
                            memavail + "\n" + \
                            memuseperc + "\n" + \
                            diskused + "\n\n" + \
                            pidsinf + "\n" + \
                            pidsreply
                    bot.sendMessage(chat_id, reply, disable_web_page_preview=True, parse_mode='HTML')
                elif msg['text'] == "Stop":
                    clearall(chat_id)
                    bot.sendMessage(chat_id, "Все операции остановлены", reply_markup=hide_keyboard)
                elif msg['text'] == '/setpoll' and chat_id not in setpolling:
                    bot.sendChatAction(chat_id, 'typing')
                    setpolling.append(chat_id)
                    bot.sendMessage(chat_id, "Отправьте мне новый интервал проверки в секундах? (выше 10)", reply_markup=stopmarkup)
                elif chat_id in setpolling:
                    bot.sendChatAction(chat_id, 'typing')
                    try:
                        global poll
                        poll = int(msg['text'])
                        if poll > 10:
                            bot.sendMessage(chat_id, "All set!")
                            clearall(chat_id)
                        else:
                            1/0
                    except:
                        bot.sendMessage(chat_id, "Отправьте числовое значение выше 10.")
                elif msg['text'] == "/shell" and chat_id not in shellexecution:
                    bot.sendMessage(chat_id, "Отправьте мне Shell-комманду", reply_markup=stopmarkup)
                    shellexecution.append(chat_id)
                elif msg['text'] == "/setmem" and chat_id not in settingmemth:
                    bot.sendChatAction(chat_id, 'typing')
                    settingmemth.append(chat_id)
                    bot.sendMessage(chat_id, "Установите новый порог памяти для мониторинга", reply_markup=stopmarkup)
                elif chat_id in settingmemth:
                    bot.sendChatAction(chat_id, 'typing')
                    try:
                        global memorythreshold
                        memorythreshold = int(msg['text'])
                        if memorythreshold < 100:
                            bot.sendMessage(chat_id, "Все получилось!")
                            clearall(chat_id)
                        else:
                            1/0
                    except:
                        bot.sendMessage(chat_id, "Пожалуйста, отправьте числовое значение ниже 100.")

                elif chat_id in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    p = Popen(msg['text'], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    output = p.stdout.read()
                    if output != b'':
                        bot.sendMessage(chat_id, output, disable_web_page_preview=True)
                    else:
                        bot.sendMessage(chat_id, "Упс.", disable_web_page_preview=True)
                elif msg['text'] == '/memgraph':
                    bot.sendChatAction(chat_id, 'upload_photo')
                    tmperiod = "За %.2f часа" % ((datetime.now() - graphstart).total_seconds() / 3600)
                    bot.sendPhoto(chat_id, plotmemgraph(memlist, xaxis, tmperiod))

TOKEN = telegrambot

bot = YourBot(TOKEN)
bot.message_loop()
tr = 0
xx = 0
# Keep the program running.
while 1:
    if tr == poll:
        tr = 0
        timenow = datetime.now()
        memck = psutil.virtual_memory()
        mempercent = memck.percent
        if len(memlist) > 300:
            memq = collections.deque(memlist)
            memq.append(mempercent)
            memq.popleft()
            memlist = memq
            memlist = list(memlist)
        else:
            xaxis.append(xx)
            xx += 1
            memlist.append(mempercent)
        memfree = memck.available / 1000000
        if mempercent > memorythreshold:
            memavail = "Доступно ОЗУ: %.2f GB" % (memck.available / 1000000000)
            graphend = datetime.now()
            tmperiod = "За последние %.2f часов" % ((graphend - graphstart).total_seconds() / 3600)
            for adminid in adminchatid:
                bot.sendMessage(adminid, "ВНИМАНИЕ! МАЛО ОПЕРАТИВНОЙ ПАМЯТИ!\n" + memavail)
                bot.sendPhoto(adminid, plotmemgraph(memlist, xaxis, tmperiod))
    time.sleep(10)  # 10 seconds
    tr += 10
