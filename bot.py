import os
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
sp = Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user}")

@bot.command()
async def spotify(ctx, *, query):
    results = sp.search(q=query, type='track', limit=1)
    if not results['tracks']['items']:
        return await ctx.send("❌ Трек не найден в Spotify")
    
    track = results['tracks']['items'][0]
    name = track['name']
    artist = track['artists'][0]['name']
    search_query = f"{artist} - {name}"
    await play_from_youtube(ctx, search_query)

@bot.command()
async def play(ctx, *, query):
    await play_from_youtube(ctx, query)

async def play_from_youtube(ctx, query):
    if not ctx.author.voice:
        return await ctx.send("❌ Ты должен быть в голосовом канале!")

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)

    voice_client = ctx.voice_client

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': False
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        url = info['entries'][0]['url'] if 'entries' in info else info['url']

    source = await discord.FFmpegOpusAudio.from_probe(url, method='fallback')
    if voice_client.is_playing():
        voice_client.stop()
    voice_client.play(source)
    await ctx.send(f"🎶 Воспроизвожу: {query}")

bot.run(os.getenv("DISCORD_TOKEN"))
