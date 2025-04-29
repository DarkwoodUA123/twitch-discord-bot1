import discord
import os
import requests
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

# Получаем данные из переменных окружения (настроены в Railway)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
TWITCH_USERNAME = os.getenv('TWITCH_USERNAME')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# URL гифки
GIF_URL = "https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif"

# Переменная для отслеживания статуса стрима
stream_announced = False

# Получение токена доступа для Twitch
def get_twitch_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print("Ошибка при получении токена:", response.status_code, response.text)
        return None

# Получение информации о стриме
def get_stream_info():
    access_token = get_twitch_access_token()
    if not access_token:
        return None

    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get('data')
        if data:
            return data[0]  # Стрим активен
        return None  # Стрим не идёт
    else:
        print("Ошибка при получении данных о стриме:", response.status_code, response.text)
        return None

# Проверка стрима каждые 10 секунд
async def check_stream_loop():
    global stream_announced
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    while not bot.is_closed():
        stream_info = get_stream_info()
        if stream_info and not stream_announced:
            game = stream_info.get('game_name', 'Неизвестно')
            viewers = stream_info.get('viewer_count', 'Неизвестно')

            embed = discord.Embed(
                title=f"{TWITCH_USERNAME} в эфире! 🔴",
                description=f"[Смотреть стрим](https://www.twitch.tv/{TWITCH_USERNAME})",
                color=discord.Color.red()
            )
            embed.add_field(name="Игра", value=game, inline=True)
            embed.add_field(name="Зрителей", value=viewers, inline=True)
            embed.set_image(url=GIF_URL)
            embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/twitch_profile_image.png")
            embed.set_footer(text="Создано для Twitch оповещений")

            await channel.send("@everyone", embed=embed)
            stream_announced = True

        elif not stream_info:
            stream_announced = False  # Стрим закончился

        await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    bot.loop.create_task(check_stream_loop())

bot.run(DISCORD_TOKEN)
