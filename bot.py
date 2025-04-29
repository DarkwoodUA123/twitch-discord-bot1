import discord
import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем данные из .env файла
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
TWITCH_USERNAME = os.getenv('TWITCH_USERNAME')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

# Настройки клиента
intents = discord.Intents.default()
intents.message_content = True   # Чтобы читать текст сообщений
client = discord.Client(intents=intents)

# Переменная для хранения ID первого сообщения
message_id = None

# Получение токена доступа для Twitch API
def get_twitch_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print("Ошибка при получении токена:", response.status_code)
        return None

# Получение информации о стриме
def get_stream_info():
    access_token = get_twitch_access_token()
    if access_token is None:
        return None

    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json()['data']:
        stream_data = response.json()['data'][0]
        game_name = stream_data['game_name']
        viewer_count = stream_data['viewer_count']
        return game_name, viewer_count
    else:
        print("Ошибка при получении данных о стриме:", response.status_code)
        return None, None

@client.event
async def on_ready():
    print(f"Зашёл как {client.user}")

@client.event
async def on_message(message):
    global message_id  # Добавили объявление переменной как глобальной
    
    # Игнорируем собственные сообщения
    if message.author.id == client.user.id:
        return

    # Тестовая команда для проверки уведомлений
    if message.content == "!test":
        channel = client.get_channel(CHANNEL_ID)

        # Получаем информацию о стриме
        game_name, viewer_count = get_stream_info()
        
        if game_name is None:
            game_name = "Неизвестно"
            viewer_count = "Нет данных"

        # Создаем красивое сообщение с использованием Embed
        embed = discord.Embed(
            title=f"🎮 {TWITCH_USERNAME} в эфире! 🔴",
            description=f"Присоединяйтесь к стриму {TWITCH_USERNAME} на Twitch.",
            color=discord.Color.red()
        )

        # Добавляем поля с информацией
        embed.add_field(name="Ссылка на стрим:", value=f"[Перейти на Twitch](https://www.twitch.tv/{TWITCH_USERNAME})", inline=False)
        embed.add_field(name="Игра:", value=game_name, inline=True)
        embed.add_field(name="Зрители:", value=viewer_count, inline=True)

        # Устанавливаем миниатюру и подпись
        embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/twitch_profile_image.png")  # Логотип Twitch
        embed.set_footer(text="Created by stupa | Discord: stupapupa___", icon_url="https://cdn.discordapp.com/icons/your_icon.png")

        # Если сообщение не отправлялось раньше, отправляем его
        if message_id is None:
            msg = await channel.send(
                f"@everyone",  # Уведомление для всех участников сервера
                embed=embed
            )
            message_id = msg.id  # Сохраняем ID первого сообщения
        else:
            # Если сообщение уже было отправлено, обновляем его
            msg = await channel.fetch_message(message_id)
            await msg.edit(
                embed=embed
            )

# Этот блок кода будет выполнен, если бот запускается как основной файл
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
