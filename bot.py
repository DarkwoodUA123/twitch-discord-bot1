import asyncio

# Добавим переменную для отслеживания текущего состояния стрима
stream_live = False

@bot.event
async def on_ready():
    print(f"Зашёл как {bot.user}")
    bot.loop.create_task(check_stream_loop())

async def check_stream_loop():
    global stream_live
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        stream_info = get_stream_info()
        if stream_info:
            if not stream_live:
                stream_live = True
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
                await channel.send("@everyone", embed=embed)
        else:
            stream_live = False

        await asyncio.sleep(10)  # Проверка каждые 10 секунд
