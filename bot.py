import discord
import asyncio
import os
import time

# Ваши переменные и настройки
TWITCH_USERNAME = "your_twitch_username"  # Убедитесь, что имя стримера правильное
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID канала Discord
GIF_URL = "https://media.giphy.com/media/your_gif_url_here.gif"  # Замените на ваш URL для гифки

# Инициализация клиента Discord
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# Переменные для отслеживания состояния стрима
stream_live = False
stream_start_time = None
stream_end_time = None
message_count = 0  # Счётчик сообщений

# Обработчик события при запуске бота
@bot.event
async def on_ready():
    print(f"Зашёл как {bot.user}")
    bot.loop.create_task(check_stream_loop())

# Основной цикл проверки стрима
async def check_stream_loop():
    global stream_live, stream_start_time, stream_end_time, message_count
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        stream_info = get_stream_info()  # Функция получения информации о стриме

        if stream_info:
            if not stream_live:
                stream_live = True
                stream_start_time = time.time()  # Записываем время начала стрима
                game_name, viewer_count = stream_info
                embed = discord.Embed(
                    title=f"🎮 {TWITCH_USERNAME} в эфире! 🔴",
                    description=f"Присоединяйтесь к стриму {TWITCH_USERNAME} на Twitch.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Ссылка на стрим:", value=f"[Перейти на Twitch](https://www.twitch.tv/{TWITCH_USERNAME})", inline=False)
                embed.add_field(name="Игра:", value=game_name, inline=True)
                embed.add_field(name="Зрители:", value=viewer_count, inline=True)
                embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/twitch_profile_image.png")
                embed.set_footer(text="Created by stupa | Discord: stupapupa___")
                embed.set_image(url=GIF_URL)
                msg = await channel.send("@everyone", embed=embed)
                message_count += 1  # Увеличиваем счётчик сообщений
            else:
                # Если стрим уже активен, обновляем его
                game_name, viewer_count = stream_info
                embed = discord.Embed(
                    title=f"🎮 {TWITCH_USERNAME} в эфире! 🔴",
                    description=f"Присоединяйтесь к стриму {TWITCH_USERNAME} на Twitch.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Ссылка на стрим:", value=f"[Перейти на Twitch](https://www.twitch.tv/{TWITCH_USERNAME})", inline=False)
                embed.add_field(name="Игра:", value=game_name, inline=True)
                embed.add_field(name="Зрители:", value=viewer_count, inline=True)
                embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/twitch_profile_image.png")
                embed.set_footer(text="Created by stupa | Discord: stupapupa___")
                embed.set_image(url=GIF_URL)
                await msg.edit(embed=embed)
                message_count += 1  # Увеличиваем счётчик сообщений
        else:
            if stream_live:  # Если стрим завершился
                stream_end_time = time.time()  # Записываем время окончания стрима
                stream_duration = stream_end_time - stream_start_time
                # Логируем продолжительность и количество сообщений
                print(f"Стрим {TWITCH_USERNAME} завершился!")
                print(f"Продолжительность стрима: {stream_duration // 60} минут {stream_duration % 60} секунд.")
                print(f"Количество сообщений: {message_count}")
                # Сохраняем данные в файл
                with open("stream_logs/stream_log.txt", "a") as log_file:
                    log_file.write(f"Стрим {TWITCH_USERNAME} завершился!\n")
                    log_file.write(f"Продолжительность: {stream_duration // 60} минут {stream_duration % 60} секунд.\n")
                    log_file.write(f"Сообщений за стрим: {message_count}\n")
                # Сбросить переменные для следующего стрима
                stream_live = False
                message_count = 0

        await asyncio.sleep(10)  # Проверка каждые 10 секунд

# Функция получения информации о стриме (замените на вашу)
def get_stream_info():
    # Возвращаем примерную информацию о стриме для теста
    return ("Some Game", 100)  # Игра и количество зрителей

# Запуск бота
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))  # Здесь должен быть ваш Discord токен
