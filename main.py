from pytube import YouTube
from aiogram import Bot, types, Dispatcher, executor
from googleapiclient.discovery import build

API_TOKEN = '6003037192:AAHOSdVfOUkMsQgNzMbebR0dFzXeP36PHoc'
YT_TOKEN = 'AIzaSyD6-8PNOZ6_rC1j78Br7A0VgAyt6UcrP1g'

bot = Bot(API_TOKEN)

dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Bip bop...')

@dp.message_handler(commands=[''])
async def inline(message: types.Message):
    buttons = [
        [types.KeyboardButton(text='/start')],
        [types.KeyboardButton(text='/help')],
    ]
    keyboard = types.reply_keyboard(keyboard=buttons)
    await message.answer(reply_markup=keyboard)


@dp.message_handler(commands=['help'])
async def inline(message: types.Message):
    text = "Use /download <YouTube URL> command to download video and comments both\n"
    await message.answer(text)

@dp.message_handler(commands=['download'])
async def download(message: types.Message):
    await message.answer(text='Please wait for a minute for downloading video!')
    url = message.text.split(' ')[1]
    title = download_video(url)
    await message.answer(text='You downloaded ' + f'"{title}"' + ' video')
    await bot.send_video(message.chat.id, open(title + '.mp4', 'rb'))

    await message.answer('Please wait for a minute for downloading comments!')
    video_id = message.text.split('=')[1]
    replies = []
    youtube = build('youtube', 'v3', developerKey=YT_TOKEN)

    video_response = youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id
    ).execute()

    while video_response:
        for item in video_response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            replies.append(f'Author: ${author} Comment: ${comment}')
        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id
            ).execute()
        else:
            break
    with open('temp.txt', 'w') as file:
        file.write('\n'.join(replies))
    await message.answer(text='Here is video comments!')
    await bot.send_document(message.chat.id, open('temp.txt', 'rb'))

def download_video(url):
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
    streams = yt.streams.filter(file_extension='mp4')
    streams.first().download()
    return yt.title

executor.start_polling(dp)
