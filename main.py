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
    return {}


def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


config = load_config()


def get_guild_config(guild_id):
    guild_id = str(guild_id)

    if guild_id not in config:
        config[guild_id] = {
            "enabled": True,
            "channel_id": None
        }
        save_config()

    return config[guild_id]


intents = discord.Intents.default()
intents.message_content = True


class SpoilerBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        synced = await self.tree.sync()
        print(f"{len(synced)}개 명령어 동기화 완료")


client = SpoilerBot()


@client.event
async def on_ready():
    print(f"로그인 완료: {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild is None:
        return

    guild_config = get_guild_config(message.guild.id)

    if not guild_config["enabled"]:
        return

    if guild_config["channel_id"] is not None:
        if message.channel.id != guild_config["channel_id"]:
            return

    if not message.attachments:
        return

    spoiler_files = []

    for attachment in message.attachments:
        try:
            file = await attachment.to_file(spoiler=True)
            spoiler_files.append(file)
        except Exception as e:
            print(f"파일 처리 실패: {e}")

    if spoiler_files:
        try:
            await message.channel.send(files=spoiler_files)
            await message.delete()
        except Exception as e:
            print(f"업로드 실패: {e}")


@client.tree.command(name="핑", description="봇 상태 확인")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("퐁! 🏓")


@client.tree.command(name="상태", description="현재 설정 확인")
async def status(interaction: discord.Interaction):
    guild_config = get_guild_config(interaction.guild.id)

    channel_text = "전체 채널"

    if guild_config["channel_id"]:
        channel_text = f"<#{guild_config['channel_id']}>"

    await interaction.response.send_message(
        f"자동 스포일러: {'켜짐' if guild_config['enabled'] else '꺼짐'}\n"
        f"감시 채널: {channel_text}"
    )


@client.tree.command(name="켜기", description="자동 스포일러 켜기")
async def enable(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 관리자만 사용할 수 있습니다.",
            ephemeral=True
        )
        return

    guild_config = get_guild_config(interaction.guild.id)
    guild_config["enabled"] = True
    save_config()

    await interaction.response.send_message(
        "✅ 자동 스포일러가 켜졌습니다."
    )


@client.tree.command(name="끄기", description="자동 스포일러 끄기")
async def disable(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 관리자만 사용할 수 있습니다.",
            ephemeral=True
        )
        return

    guild_config = get_guild_config(interaction.guild.id)
    guild_config["enabled"] = False
    save_config()

    await interaction.response.send_message(
        "❌ 자동 스포일러가 꺼졌습니다."
    )


@client.tree.command(name="채널설정", description="감시할 채널 지정")
@app_commands.describe(channel="감시할 채널")
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

    guild_config = get_guild_config(interaction.guild.id)
    guild_config["channel_id"] = channel.id
    save_config()

    await interaction.response.send_message(
        f"✅ {channel.mention} 채널만 감시합니다."
    )


@client.tree.command(name="채널해제", description="모든 채널 감시")
async def clear_channel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 관리자만 사용할 수 있습니다.",
            ephemeral=True
        )
        return

    guild_config = get_guild_config(interaction.guild.id)
    guild_config["channel_id"] = None
    save_config()

    await interaction.response.send_message(
        "✅ 모든 채널을 감시하도록 변경했습니다."
    )


client.run(TOKEN)
