import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp

load_dotenv()

# Запись cookies в файл, если есть переменная окружения YOUTUBE_COOKIES
cookies_content = os.getenv('YOUTUBE_COOKIES')
if cookies_content:
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookies_content)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Бот запущен как {bot.user}')

@bot.command(name='music')
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        await ctx.send("❌ Ты должен быть в голосовом канале!")
        return

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = ctx.voice_client
        if vc.channel != voice_channel:
            await vc.move_to(voice_channel)

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
        'cookiefile': 'cookies.txt' if cookies_content else None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        # Если результат - плейлист, берем первый трек
        if 'entries' in info:
            info = info['entries'][0]
        url = info['url']

    if vc.is_playing():
        vc.stop()

    vc.play(discord.FFmpegPCMAudio(url), after=lambda e: print('▶️ Завершено'))

    await ctx.send(f"🎶 Воспроизвожу: `{query}`")

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 Музыка остановлена и бот вышел из канала.")
    else:
        await ctx.send("❌ Бот не в голосовом канале.")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("❌ Ошибка: переменная DISCORD_BOT_TOKEN не установлена.")
else:
    bot.run(TOKEN)
