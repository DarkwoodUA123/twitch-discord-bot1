from discord.ext import tasks

# Функция для регулярной проверки стрима
@tasks.loop(minutes=1)  # Проверка каждую минуту
async def check_stream():
    channel = bot.get_channel(CHANNEL_ID)
    stream_info = get_stream_info()

    if stream_info is None:
        game_name = "Неизвестно"
        viewer_count = "Нет данных"
    else:
        game_name, viewer_count = stream_info

    embed = discord.Embed(
        title=f"🎮 {TWITCH_USERNAME} в эфире! 🔴" if stream_info else "🎮 {TWITCH_USERNAME} не в эфире",
        description=f"Присоединяйтесь к стриму {TWITCH_USERNAME} на Twitch.",
        color=discord.Color.red()
    )

    embed.add_field(name="Ссылка на стрим:", value=f"[Перейти на Twitch](https://www.twitch.tv/{TWITCH_USERNAME})", inline=False)
    embed.add_field(name="Игра:", value=game_name, inline=True)
    embed.add_field(name="Зрители:", value=viewer_count, inline=True)

    embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/twitch_profile_image.png")
    embed.set_footer(text="Created by stupa | Discord: stupapupa___", icon_url="https://cdn.discordapp.com/icons/your_icon.png")
    embed.set_image(url=GIF_URL)

    if message_id is None:
        msg = await channel.send(f"@everyone", embed=embed)
        message_id = msg.id  # Сохраняем ID первого сообщения
    else:
        msg = await channel.fetch_message(message_id)
        await msg.edit(embed=embed)

@bot.event
async def on_ready():
    print(f"Зашёл как {bot.user}")
    check_stream.start()  # Запускаем задачу проверки стрима

