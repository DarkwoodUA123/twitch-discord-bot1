import os
import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'options': '-vn'}

queues = {}

from discord.ui import View, Button

class MusicControl(View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx

    @discord.ui.button(label="⏯️ Пауза/Воспроизведение", style=discord.ButtonStyle.primary)
    async def pause_resume(self, interaction: discord.Interaction, button: Button):
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("❌ Бот не в голосовом канале.", ephemeral=True)
        if vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Воспроизведение", ephemeral=True)
        else:
            vc.pause()
            await interaction.response.send_message("⏸️ Пауза", ephemeral=True)

    @discord.ui.button(label="⏹️ Стоп", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: Button):
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("❌ Бот не в голосовом канале.", ephemeral=True)
        vc.stop()
        queues[interaction.guild.id] = []
        await vc.disconnect()
        await interaction.response.send_message("🛑 Музыка остановлена и бот отключен.", ephemeral=True)

async def play_next(ctx):
    guild_id = ctx.guild.id
    if queues.get(guild_id):
        url, title = queues[guild_id].pop(0)
        vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        def after_playing(error):
            coro = play_next(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error in after_playing: {e}")

        vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=after_playing)
        await ctx.send(f"🎶 Теперь играет: **{title}**", view=MusicControl(ctx))
    else:
        vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if vc and vc.is_connected():
            await vc.disconnect()
            await ctx.send("✅ Очередь закончилась, бот отключился.")

@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user}")

@bot.command(name="music")
async def music(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Ты должен быть в голосовом канале.")

    channel = ctx.author.voice.channel

    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not vc:
        vc = await channel.connect()
    elif vc.channel != channel:
        await vc.move_to(channel)

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        except Exception as e:
            return await ctx.send(f"❌ Ошибка при поиске: {e}")

    url = info['url']
    title = info.get('title')

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []

    queues[ctx.guild.id].append((url, title))
    await ctx.send(f"➕ Добавлено в очередь: **{title}**")

    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        await play_next(ctx)

@bot.command(name="stop")
async def stop(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_connected():
        queues[ctx.guild.id] = []
        vc.stop()
        await vc.disconnect()
        await ctx.send("🛑 Музыка остановлена и бот отключен.")
    else:
        await ctx.send("❗ Бот не в голосовом канале.")

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        print("❌ Пожалуйста, укажите токен бота в переменной окружения DISCORD_BOT_TOKEN")
        exit(1)
    bot.run(TOKEN)
