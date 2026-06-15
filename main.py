import discord
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"로그인 완료: {client.user}")

@client.event
async def on_message(message):

    if message.author.bot:
        return

    if not message.attachments:
        return

    spoiler_files = []

    for attachment in message.attachments:

        file = await attachment.to_file(
            filename=f"SPOILER_{attachment.filename}"
        )

        spoiler_files.append(file)

    if spoiler_files:

        await message.channel.send(
            files=spoiler_files
        )

        await message.delete()

client.run(TOKEN)
