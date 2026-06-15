import discord
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

auto_spoiler = True

class SpoilerBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = SpoilerBot()

@client.event
async def on_ready():
    print(f"로그인 완료: {client.user}")

@client.event
async def on_message(message):

    global auto_spoiler

    if not auto_spoiler:
        return

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

@client.tree.command(name="핑", description="봇 상태 확인")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("퐁! 🏓")

@client.tree.command(name="켜기", description="자동 스포일러 켜기")
async def enable(interaction: discord.Interaction):

    global auto_spoiler
    auto_spoiler = True

    await interaction.response.send_message(
        "✅ 자동 스포일러가 켜졌습니다."
    )

@client.tree.command(name="끄기", description="자동 스포일러 끄기")
async def disable(interaction: discord.Interaction):

    global auto_spoiler
    auto_spoiler = False

    await interaction.response.send_message(
        "❌ 자동 스포일러가 꺼졌습니다."
    )

client.run(TOKEN)
