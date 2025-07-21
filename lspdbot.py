import discord
import asyncio
import aiohttp
import csv
import io

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSzsYgiiESDo7Ve_01qavZ9MXvNlydWcmme-9BHc7dpv4iS2s20RsZnsaH8NW6o_4vSqJIbu8nERij2/pub?output=csv"

DISCORD_CHANNEL_ID = 1395662330200723479  # Только этот канал
MENTION_ROLES = "<@&1396557433064652913> <@&1396557452421365832>"
OWNER_ID = 838188176878075925

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

headers = []
processed_rows = set()
first_run = True

async def check_new_responses():
    global headers, processed_rows, first_run
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    async with aiohttp.ClientSession() as session:
        while not client.is_closed():
            try:
                async with session.get(CSV_URL) as resp:
                    if resp.status == 200:
                        data = await resp.text()
                        reader = csv.reader(io.StringIO(data))
                        rows = list(reader)

                        if not headers and rows:
                            headers = rows[0]
                            rows = rows[1:]
                        else:
                            rows = rows[1:]

                        if first_run:
                            for row in rows:
                                processed_rows.add(tuple(row))
                            first_run = False
                        else:
                            for row in rows:
                                row_key = tuple(row)
                                if row_key not in processed_rows:
                                    embed = discord.Embed(
                                        title="Отчёт на Повышение | Central Patrol Division",
                                        url="https://docs.google.com/forms/d/e/1FAIpQLSdj133lWU4c18RkFgIifRDCIuX9DzTRn2zQE4C_x1RYVikVsw/viewform",
                                        color=0x87CEEB
                                    )
                                    for q, a in zip(headers, row):
                                        if a.strip():
                                            embed.add_field(name=q, value=a.strip(), inline=False)

                                    embed.set_image(url="https://i.imgur.com/cIDfrw8.png")
                                    await channel.send(content=MENTION_ROLES, embed=embed)
                                    processed_rows.add(row_key)
                    else:
                        print(f"Ошибка при получении CSV: статус {resp.status}")
            except Exception as e:
                print(f"Ошибка при запросе CSV: {e}")

            await asyncio.sleep(5)

@client.event
async def on_ready():
    print(f'Бот запущен как {client.user}')
    client.loop.create_task(check_new_responses())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        if message.author.id == OWNER_ID:
            channel = client.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                await channel.send(message.content)
        else:
            await message.channel.send("Не пиши, это без смысла")

client.run(DISCORD_TOKEN)
