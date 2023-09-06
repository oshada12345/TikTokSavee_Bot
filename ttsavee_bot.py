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
from ast import literal_eval
import re
import sys
import random
from base64 import b64decode
try:
    import requests
    import bs4
except ImportError:
    sys.exit('- module not installed !')


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
        await bot.send_message(admin_id,f'👤 New user : {message.chat.id}')
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
        testing = tiktok_downloader()
        if testing.musicaldown(message.text, "video") is True:
            print("Видео загружено")
        video = open('video.mp4','rb')
        try:

            await bot.send_video(message.chat.id, video, caption='🎉 Поздравляю, видео успешно скачено!\n\n😊 Скачано с помощью <b>@saving_tt_video_bot</b>',parse_mode='html')
            await bot.delete_message(message.chat.id, loading.message_id)
            await bot.delete_message(message.chat.id, sticker.message_id)


        except:
            await bot.delete_message(message.chat.id, loading.message_id)
            await bot.delete_message(message.chat.id, sticker.message_id)
            await bot.send_sticker(message.chat.id,
                                             "CAACAgIAAxkBAAEKPMZk-KebbYWGOpgXZStXyiM8SUjfLgACZwAD5KDOB6GjeJZ2Piz9MAQ")
            await bot.send_message(message.chat.id, '🥺 Ошибка при скачивания видео ,попробуйте снова...')
            # os.remove("video.mp4")

    else:
        await bot.send_message(message.chat.id,
                               '⛔️ В данный момент возможность загрузки видео доступна только из <b>TikTok</b>',
                               parse_mode='html')
    os.remove("video.mp4")

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


class tiktok_downloader:
    def __init__(self):
        pass

    def musicaldown(self, url, output_name):
        try:
            """url: tiktok video url
            output_name: output video (.mp4). Example : video.mp4
            """
            ses = requests.Session()
            server_url = 'https://musicaldown.com/'
            headers = {
                "Host": "musicaldown.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "TE": "trailers"
            }
            ses.headers.update(headers)
            req = ses.get(server_url)
            data = {}
            parse = bs4.BeautifulSoup(req.text, 'html.parser')
            get_all_input = parse.findAll('input')
            for i in get_all_input:
                if i.get("id") == "link_url":
                    data[i.get("name")] = url
                else:
                    data[i.get("name")] = i.get("value")
            post_url = server_url + "id/download"
            req_post = ses.post(post_url, data=data, allow_redirects=True)
            if req_post.status_code == 302 or 'This video is currently not available' in req_post.text or 'Video is private or removed!' in req_post.text:
                print('- video private or remove')
                return 'private/remove'
            elif 'Submitted Url is Invalid, Try Again' in req_post.text:
                print('- url is invalid')
                return 'url-invalid'
            get_all_blank = bs4.BeautifulSoup(req_post.text, 'html.parser').findAll(
                'a', attrs={'target': '_blank'})

            download_link = get_all_blank[0].get('href')
            get_content = requests.get(download_link)

            with open(output_name + ".mp4", 'wb') as fd:
                fd.write(get_content.content)
            return True
        except IndexError:
            return False


# testing = tiktok_downloader()
#
# if testing.musicaldown("https://vm.tiktok.com/ZMj8HCaM1/", "video") is True:
#     print("Видео загружено")

asyncio.run(bot.polling(non_stop=True))
