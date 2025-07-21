import discord
from discord.ext import commands
import youtube_dl

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def music(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Ты должен быть в голосовом канале.")

    channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client is None:
        voice_client = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': 'in_playlist',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        url = info['url']
        title = info['title']

    voice_client.stop()
    voice_client.play(discord.FFmpegPCMAudio(url))
    await ctx.send(f"▶ Воспроизвожу: **{title}**")

bot.run('DISCORD_BOT_TOKEN')
