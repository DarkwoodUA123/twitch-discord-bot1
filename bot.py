import os
import asyncio
import time
import discord

# Путь для хранения логов
log_file_path = "stream_logs/stream_log.txt"

# Убедимся, что директория для логов существует
if not os.path.exists("stream_logs"):
    os.makedirs("stream_logs")

# Добавим переменные для отслеживания
stream_start_time = None
stream_end_time = None
message_count = 0  # Счётчик сообщений

@bot.event
async def on_ready():
    print(f"Зашёл как {bot.user}")
    bot.loop.create_task(check_stream_loop())

async def check_stream_loop():
    global stream_live, stream_start_time, stream_end_time, message_count
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        stream_info = get_stream_info()
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
                # Если стрим уже активен, просто обновляем его
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
                with open(log_file_path, "a") as log_file:
                    log_file.write(f"Стрим {TWITCH_USERNAME} завершился!\n")
                    log_file.write(f"Продолжительность: {stream_duration // 60} минут {stream_duration % 60} секунд.\n")
                    log_file.write(f"Сообщений за стрим: {message_count}\n")
                # Сбросить переменные для следующего стрима
                stream_live = False
                message_count = 0

        await asyncio.sleep(5)  # Проверка каждые 5 секунд
