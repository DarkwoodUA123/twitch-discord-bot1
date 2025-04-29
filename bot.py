import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")

@bot.command()
async def test(ctx):
    game_name, viewer_count = get_stream_info()

    if game_name is None:
        game_name = "Неизвестно"
        viewer_count = "Нет данных"

    embed = discord.Embed(
        title=f"🎮 {TWITCH_USERNAME} в эфире! 🔴",
        description=f"Присоединяйтесь к стриму {TWITCH_USERNAME} на Twitch.",
        color=discord.Color.red()
    )
    embed.add_field(name="Ссылка на стрим:", value=f"[Перейти на Twitch](https://www.twitch.tv/{TWITCH_USERNAME})", inline=False)
    embed.add_field(name="Игра:", value=game_name, inline=True)
    embed.add_field(name="Зрители:", value=viewer_count, inline=True)
    embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/twitch_profile_image.png")
    embed.set_footer(text="Created by stupa | Discord: stupapupa___", icon_url="https://cdn.discordapp.com/icons/your_icon.png")

    await ctx.send("@everyone", embed=embed)

# Запуск
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
