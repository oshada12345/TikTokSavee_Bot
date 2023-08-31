import re
import sqlite3
import asyncio
import os
import aiohttp
import datetime
import requests
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from dotenv import load_dotenv, find_dotenv
from typing import Optional, Generator

load_dotenv(find_dotenv())
bot = AsyncTeleBot(os.getenv('TOKEN_BOT'))

db = sqlite3.connect('db/ttsavee.db', check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users(
    id integer PRIMARY KEY AUTOINCREMENT,
    tg_id integer,
    date date
)""")

admin_id = 1900666417

CHANNELS = [["✍🏻 Подписаться", "-1001717313870", "https://t.me/maruvsss"],
            ["✍🏻 Подписаться", "-1001253161726", "https://t.me/+YJ0_aG9JyKNjN2Fi"]]

keyboard = types.InlineKeyboardMarkup()

for channel in CHANNELS:
    btn = types.InlineKeyboardButton(text=channel[0], url=channel[2])
    keyboard.add(btn)
button_done_sub = types.InlineKeyboardButton(text='♻️ Проверить', callback_data='subchanneldone')
keyboard.add(button_done_sub)


async def check_sub_channels(channels, user_id):
    for channel in channels:
        chat_member = await bot.get_chat_member(chat_id=channel[1], user_id=user_id)
        if chat_member.status == 'left':
            return False
    return True


@bot.message_handler(commands=['sendall'])
async def send_all_message(message: types.Message):
    sql.execute("SELECT tg_id FROM users;")
    users = sql.fetchall()
    if message.chat.id == admin_id:
        await bot.send_message(message.chat.id, '💌 Starting')
        for i in users:
            try:
                print("Send to: ", str(i[0]))
                await bot.send_message(i[0], message.text[message.text.find(' '):], parse_mode='html')
            except Exception as error:
                print("Blocked bot: ", str(i[0]))
            # await bot.send_message(i[0],message.text[message.text.find(' '):],parse_mode='html')
        await bot.send_message(message.chat.id, '✅ Successfully')
    else:
        await bot.send_message(message.chat.id, 'Вы не являетесь администратором!')


async def download(url):
    async with aiohttp.ClientSession() as session:
        request_url = f'https://api.douyin.wtf/api?url={url}'
        async with session.get(request_url) as response:
            data = await response.json()
            video = data['video_data']['nwm_video_url_HQ']
            return video




@bot.message_handler(commands=['start'])
async def command_start(message):
    # if await check_sub_channels(CHANNELS, message.chat.id):
    date = datetime.datetime.now()
    tg_id = message.from_user.id

    sql.execute(f"SELECT tg_id FROM users WHERE tg_id={tg_id}")
    data = sql.fetchone()
    if data is None:
        sql.execute("INSERT INTO users VALUES (?,?,?)", (None, tg_id, date))
        db.commit()
    img = open("img/start.png", "rb")
    await bot.send_photo(message.chat.id, img,
                         caption='<b>Привет! Добро пожаловать к нам в видеобот TikTokSavee!👋</b>\n\nМы рады видеть тебя здесь. Просто дайте мне ссылку на видео с TikTok, и я отправлю вам это видео без водяных знаков.\n\n<b>Наслаждайтесь просмотром! 🎉</b>\n Если у тебя есть какие-либо вопросы или запросы, не стесняйся спрашивать: <b>@maruvvvs</b> 😊📹',
                         parse_mode='html')


# else:
#     await bot.send_message(message.chat.id, '👻 Для доступа к боту,необходимо подписаться на канал',
#                            reply_markup=keyboard)


@bot.message_handler()
async def process(message):
    if re.compile('https://[a-zA-Z]+.tiktok.com/').match(message.text):
        sticker = await bot.send_sticker(message.chat.id,
                                         "CAACAgIAAxkBAAEKIxtk6pqNbeyXirz3RDS4vp2oXIjzyQACeQAD5KDOB6RRas-jTv2HMAQ")
        loading = await bot.send_message(message.chat.id, '🕗 Ожидайте видео скачивается...')
        video = await download(message.text)

        try:

            await bot.delete_message(message.chat.id, loading.message_id)
            await bot.delete_message(message.chat.id, sticker.message_id)
            await bot.send_video(message.chat.id, video, caption='🎉 Поздравляю, видео успешно скачено!')

        except:
            sticker = await bot.send_sticker(message.chat.id,
                                             "CAACAgIAAxkBAAEKKWhk7fzCtX_iaxOxfrN345XD23_65QACbwAD5KDOBwj7OOarOaTFMAQ")
            loading = await bot.send_message(message.chat.id, '😅 Ого ,тяжеленький, ожидайте видео скачивается...')
            response = requests.get(video)
            with open("ttsavee.mp4", "wb") as file:
                file.write(response.content)
            result = open("ttsavee.mp4", 'rb')

            await bot.send_document(message.chat.id, result, caption='🎉 Поздравляю, видео успешно скачено!')
            await bot.delete_message(message.chat.id, loading.message_id)
            await bot.delete_message(message.chat.id, sticker.message_id)
            os.remove("ttsavee.mp4")

    else:
        await bot.send_message(message.chat.id,
                               '⛔️ В данный момент возможность загрузки видео доступна только из <b>TikTok</b>',
                               parse_mode='html')


@bot.callback_query_handler(func=lambda callback: callback.data == "subchanneldone")
async def callback_handler(callback):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if await check_sub_channels(CHANNELS, callback.message.chat.id):
        await bot.send_message(callback.message.chat.id,
                               '<b>Привет! Добро пожаловать к нам в видеобот TikTok! 🎉</b>\n\nМы рады видеть тебя здесь. Просто дайте мне ссылку на видео с TikTok, и я отправлю вам это видео без водяных знаков отправителя. Наслаждайтесь просмотром! Если у тебя есть какие-либо вопросы или запросы, не стесняйся спрашивать. 😊📹',
                               parse_mode='html')
    else:
        await bot.send_message(callback.message.chat.id,
                               '👻 Для доступа к боту,необходимо подписаться на канал',
                               reply_markup=keyboard)


asyncio.run(bot.polling(non_stop=True))
