import discord
from discord import app_commands
import os
import json

TOKEN = os.getenv("TOKEN")

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "enabled": True,
        "channel_id": None
    }


def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f)


config = load_config()

intents = discord.Intents.default()
intents.message_content = True


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

    if message.author.bot:
        return

    if not config["enabled"]:
        return

    if config["channel_id"] is not None:
        if message.channel.id != config["channel_id"]:
            return

    if not message.attachments:
        return

    spoiler_files = []

    for attachment in message.attachments:

        try:
            file = await attachment.to_file(
                filename=attachment.filename,
                spoiler=True
            )

            spoiler_files.append(file)

        except Exception as e:
            print(f"파일 처리 실패: {e}")

    if spoiler_files:

        try:
            await message.channel.send(
                files=spoiler_files
            )

            await message.delete()

        except Exception as e:
            print(f"업로드 실패: {e}")


@client.tree.command(
    name="핑",
    description="봇 상태 확인"
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("퐁! 🏓")


@client.tree.command(
    name="상태",
    description="현재 설정 확인"
)
async def status(interaction: discord.Interaction):

    channel_text = "전체 채널"

    if config["channel_id"]:
        channel_text = f"<#{config['channel_id']}>"

    await interaction.response.send_message(
        f"자동 스포일러: {'켜짐' if config['enabled'] else '꺼짐'}\n"
        f"대상 채널: {channel_text}"
    )


@client.tree.command(
    name="켜기",
    description="자동 스포일러 켜기"
)
async def enable(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 관리자만 사용할 수 있습니다.",
            ephemeral=True
        )
        return

    config["enabled"] = True
    save_config()

    await interaction.response.send_message(
        "✅ 자동 스포일러가 켜졌습니다."
    )


@client.tree.command(
    name="끄기",
    description="자동 스포일러 끄기"
)
async def disable(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 관리자만 사용할 수 있습니다.",
            ephemeral=True
        )
        return

    config["enabled"] = False
    save_config()

    await interaction.response.send_message(
        "❌ 자동 스포일러가 꺼졌습니다."
    )


@client.tree.command(
    name="채널설정",
    description="자동 스포일러를 사용할 채널 설정"
)
@app_commands.describe(
    channel="감시할 채널"
)
async def set_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 관리자만 사용할 수 있습니다.",
            ephemeral=True
        )
        return

    config["channel_id"] = channel.id
    save_config()

    await interaction.response.send_message(
        f"✅ {channel.mention} 채널만 감시합니다."
    )


client.run(TOKEN)
