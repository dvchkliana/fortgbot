import telebot
import json
from flask import Flask, request
import os
import sys
import requests
import logging

logging.basicConfig(level=logging.INFO)
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    sys.exit("Ошибка: API-токен не задан в переменных окружения")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот запущен"

@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    try:
        json_str = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_str)
        if update:
            bot.process_new_updates([update])
    except Exception as e:
        app.logger.exception(f"Webhook error: {str(e)}")
    return '', 200

def load_db():
    try:
        with open('db.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(data):
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()

@bot.message_handler(commands=['start'])
def start(message):
    user_id =str(message.from_user.id)

    if user_id not in db:
        db[user_id] = {"name": 'awaiting_name', "age": None, "money": 10000, "state": "awaiting_name"}
        save_db(db)
        bot.send_message(message.chat.id, "Привет! Как тебя зовут?")
        return 0

    db[user_id]["money"] = 10000

    keyboardReply = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    helpButton = telebot.types.KeyboardButton("Помощь")
    infoButton = telebot.types.KeyboardButton("Инфо")
    aboutButton = telebot.types.KeyboardButton("О боте")
    linkButton = telebot.types.KeyboardButton("Ссылка на чат")
    slowMachineButton = telebot.types.KeyboardButton("Игровой автомат")
    diceButton = telebot.types.KeyboardButton("Игра в кубик")
    gameButton = telebot.types.KeyboardButton("Кто хочет стать миллионером")

    keyboardReply.add(helpButton, infoButton, aboutButton, linkButton, slowMachineButton, diceButton, gameButton)

    bot.send_message(message.chat.id, "Привет", reply_markup=keyboardReply)

@bot.message_handler(content_types=['text'])
def text_event(message):
    user_id = str(message.from_user.id)

    if "awaiting_name" == db.get(user_id, {}).get("state"):
        name = message.text.strip()
        db[user_id]["name"] = name
        db[user_id]["state"] = None
        save_db(db)
        bot.send_message(message.chat.id, f"Приятно познакомиться, {name}")
        bot.send_message(message.chat.id, "Сколько тебе лет?")
        return
    elif db.get(user_id, {}).get("state") == "awaiting_name":
        try:
            age = int(message.text.strip())
            db[user_id]["age"] = age
            db[user_id]["state"] = None
            save_db(db)
            start(message)
            return
        except:
            bot.send_message(message.chat.id, "Ты ввел значение возраста некорректно")
            return

    if message.text == "Помощь":
        bot.send_message(message.chat.id, "Привет! Чем я могу помочь?")
    elif message.text == "Как меня зовут?":
        user_name = db[user_id]["name"]
        bot.send_message(message.chat.id, f"Тебя зовут {user_name}")
    elif message.text == "Инфо":
        bot.send_message(message.chat.id, "Админ: @dvchkliana")
    elif message.text == "О боте":
        bot.send_message(message.chat.id, "Бот для общения")
    elif message.text == "Игра в кубик":
        inlineKeyboard = telebot.types.InlineKeyboardMarkup(row_width=3)

        btn1 = telebot.types.InlineKeyboardButton("1", callback_data='1')
        btn2 = telebot.types.InlineKeyboardButton("2", callback_data='2')
        btn3 = telebot.types.InlineKeyboardButton("3", callback_data='3')
        btn4 = telebot.types.InlineKeyboardButton("4", callback_data='4')
        btn5 = telebot.types.InlineKeyboardButton("5", callback_data='5')
        btn6 = telebot.types.InlineKeyboardButton("6", callback_data='6')

        inlineKeyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)

        bot.send_message(message.chat.id, "Угадай число на кубике", reply_markup=inlineKeyboard)

    elif message.text == "Кто хочет стать миллионером":
        if db[user_id]["money"] >= 10000:
            inlineKeyboard = telebot.types.InlineKeyboardMarkup(row_width=2)

            bttn1 = telebot.types.InlineKeyboardButton("170", callback_data='170')
            bttn2 = telebot.types.InlineKeyboardButton("130", callback_data='130')
            bttn3 = telebot.types.InlineKeyboardButton("169", callback_data='169')
            bttn4 = telebot.types.InlineKeyboardButton("26", callback_data='26')

            inlineKeyboard.add(bttn1, bttn2, bttn3, bttn4)

        bot.send_message(message.chat.id, "Сколько будет 13 в квадрате?", reply_markup=inlineKeyboard)
    elif message.text == "Игровой автомат":
        if db[user_id]["money"] >= 10000:
            value = bot.send_dice(message.chat.id, emoji='🎰').dice.value

            if value in (1, 22, 43):
                db[user_id]["money"] += 2000
                bot.send_message(message.chat.id, f"Победа! Твой выигрыш составил 2000. Твой баланс: {db[user_id]['money']}")
            elif value in (16, 32, 48):
                db[user_id]["money"] += 1000
                bot.send_message(message.chat.id, f"Тебе везет! Твой выигрыш составил 2000. Твой баланс: {db[user_id]['money']}")
            elif value == 64:
                db[user_id]["money"] += 4000
                bot.send_message(message.chat.id, f"Джекпот! Твой выигрыш составил 2000. Твой баланс: {db[user_id]['money']}")
            else:
                db[user_id]["money"] -= 1000
                bot.send_message(message.chat.id, f"Ты проиграл! Ты потерял 1000. Твой баланс: {db[user_id]['money']}")
        else:
                bot.send_message(message.chat.id, f"У тебя недостаточно средств на балансе.")

@bot.callback_query_handler(func=lambda call: call.data in ('170', '130', '169', '26'))
def game_callback(call):
    user_id = str(call.from_user.id)
    value = call.data
    if str(value) == '169':
        inlineKeyboard = telebot.types.InlineKeyboardMarkup(row_width=2)

        btt1 = telebot.types.InlineKeyboardButton("Кристаллизация", callback_data='a')
        btt2 = telebot.types.InlineKeyboardButton("Испарение", callback_data='b')
        btt3 = telebot.types.InlineKeyboardButton("Плавление", callback_data='c')
        btt4 = telebot.types.InlineKeyboardButton("Конвекция", callback_data='d')

        inlineKeyboard.add(btt1, btt2, btt3, btt4)
        db[user_id]["money"] += 2000
        bot.send_message(call.message.chat.id, f"Ты угадал! Твой выигрыш составил 2000. Твой баланс: {db[user_id]['money']}")
        bot.send_message(call.message.chat.id, "Как называется переход тела из жидкого состояния в твердое?", reply_markup=inlineKeyboard)

    else:
        bot.send_message(call.message.chat.id, "Попробуй еще раз")

@bot.callback_query_handler(func=lambda call: call.data in ('a', 'b', 'c', 'd'))
def g_callback(call):
    user_id = str(call.from_user.id)
    value = call.data
    if str(value) == 'a':
        inlineKeyboard = telebot.types.InlineKeyboardMarkup(row_width=2)

        btt1 = telebot.types.InlineKeyboardButton("5", callback_data='1a')
        btt2 = telebot.types.InlineKeyboardButton("1", callback_data='2b')
        btt3 = telebot.types.InlineKeyboardButton("3", callback_data='3c')
        btt4 = telebot.types.InlineKeyboardButton("2", callback_data='4d')

        inlineKeyboard.add(btt1, btt2, btt3, btt4)
        db[user_id]["money"] += 2000
        bot.send_message(call.message.chat.id, f"Ты угадал! Твой выигрыш составил 2000. Твой баланс: {db[user_id]['money']}")
        bot.send_message(call.message.chat.id, "Сколько атомов водорода в воде?", reply_markup=inlineKeyboard)

    else:
        bot.send_message(call.message.chat.id, "Попробуй еще раз")

@bot.callback_query_handler(func=lambda call: call.data in ('1a', '2b', '3c', '4d'))
def a_callback(call):
    user_id = str(call.from_user.id)
    value = call.data
    if str(value) == '4d':
        inlineKeyboard = telebot.types.InlineKeyboardMarkup(row_width=2)

        b1 = telebot.types.InlineKeyboardButton("Республика Татарстан", callback_data='r')
        b2 = telebot.types.InlineKeyboardButton("Республика Саха", callback_data='s')
        b3 = telebot.types.InlineKeyboardButton("Московская область", callback_data='m')
        b4 = telebot.types.InlineKeyboardButton("Красноярский край", callback_data='k')

        inlineKeyboard.add(b1, b2, b3, b4)
        db[user_id]["money"] += 2000
        bot.send_message(call.message.chat.id, f"Ты угадал! Твой выигрыш составил 2000. Твой баланс: {db[user_id]['money']}")
        bot.send_message(call.message.chat.id, "Какой самый большой субъект РФ?", reply_markup=inlineKeyboard)

    else:
        bot.send_message(call.message.chat.id, "Попробуй еще раз!")

@bot.callback_query_handler(func=lambda call: call.data in ('r', 's', 'm', 'k'))
def m_callback(call):
    user_id = str(call.from_user.id)
    value = call.data
    if str(value) == 's':
        db[user_id]["money"] += 2000
        bot.send_message(call.message.chat.id, f"Ты победил! Твой выигрыш составил 2000. Твой баланс: {db[user_id]['money']}")
    else:
        bot.send_message(call.message.chat.id, "Ты проиграл! Попробуй еще раз.")

@bot.callback_query_handler(func=lambda call: call.data in ('1', '2', '3', '4', '5', '6'))
def dice_callback(call):
    value = bot.send_dice(call.message.chat.id, emoji='🎲').dice.value
    if str(value) == call.data:
        bot.send_message(call.message.chat.id, "Ты угадал!")
    else:
        bot.send_message(call.message.chat.id, "Попробуй еще раз")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Инструкция по использованию ботом")

if __name__ == '__main__':
    server_url = os.getenv("RENDER_EXTERNAL_URL")
    if server_url and API_TOKEN:
        webhook_url = f"{server_url.rstrip('/')}/{API_TOKEN}"

        try:
            r = requests.get(f"https://api.telegram.org/bot{API_TOKEN}/setWebhook",
                             params={"url": webhook_url}, timeout=10)
            logging.info(f"Вебхук установлен: {r.text}")
        except Exception:
            logging.exception("Ошибка при установке webhook")

        port = int(os.getenv("PORT", 10000))
        logging.info(f"Запуск на порте {port}")
        app.run(host='0.0.0.0', port=port)
    else:
        logging.info("Запуск бота в режиме pooling")
        bot.remove_webhook()
        bot.infinity_polling(timeout=60)