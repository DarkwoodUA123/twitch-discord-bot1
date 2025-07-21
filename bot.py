import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

music_queue = []

@bot.event
async def on_ready():
    print(f'✅ Бот запущен как {bot.user}')

async def play_next(ctx):
    if len(music_queue) > 0:
        url, title = music_queue.pop(0)
        ctx.voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f"▶️ Сейчас играет: `{title}`")
    else:
        await ctx.voice_client.disconnect()
        await ctx.send("✅ Очередь закончилась. Бот вышел из голосового канала.")

@bot.command(name='play')
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Ты должен быть в голосовом канале!")

    channel = ctx.author.voice.channel

    if not ctx.voice_client:
        await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'cookiefile': 'cookies.txt',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        entry = info['entries'][0] if 'entries' in info else info
        url = entry['url']
        title = entry.get('title', 'неизвестный трек')

    if ctx.voice_client.is_playing():
        music_queue.append((url, title))
        await ctx.send(f"➕ Добавлено в очередь: `{title}`")
    else:
        ctx.voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f"🎶 Сейчас играет: `{title}`")

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Пропущен трек.")
    else:
        await ctx.send("❌ Сейчас ничего не играет.")

@bot.command(name='queue')
async def queue(ctx):
    if not music_queue:
        return await ctx.send("📭 Очередь пуста.")
    message = '\n'.join([f"{i+1}. {title}" for i, (_, title) in enumerate(music_queue)])
    await ctx.send(f"🎶 Очередь треков:\n{message}")

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        music_queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 Музыка остановлена и бот вышел из канала.")
    else:
        await ctx.send("❌ Бот не в голосовом канале.")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("❌ Ошибка: DISCORD_BOT_TOKEN не найден.")
else:
    bot.run(TOKEN)
