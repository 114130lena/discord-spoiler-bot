"""Components V2 외부 미디어 재생 테스트 (/미디어테스트).

이 명령어는 미디어 파일을 다운로드하거나 Discord로 다시 업로드하지 않습니다.
Discord의 미디어 프록시가 외부 HTTPS URL을 재생할 수 있는지 확인합니다.
"""

import ipaddress
import os
from urllib.parse import urlsplit

import discord
from discord import app_commands

SUPPORTED_EXTENSIONS = {".mp4", ".webm", ".mov", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif"}


def check_media_url(raw_url: str) -> str:
    if len(raw_url) > 2048:
        raise ValueError("URL은 2048자 이하로 입력해 주세요.")
    try:
        parsed = urlsplit(raw_url)
        host = parsed.hostname
        if parsed.scheme != "https" or not host or parsed.username or parsed.password:
            raise ValueError("공개 HTTPS 미디어 주소만 지원합니다.")
        if parsed.port not in (None, 443):
            raise ValueError("기본 HTTPS 포트(443) 주소만 사용해 주세요.")
        if host.lower() == "localhost" or host.endswith(".local"):
            raise ValueError("로컬 서버 주소는 사용할 수 없습니다.")
        try:
            ipaddress.ip_address(host)
        except ValueError:
            if "." not in host:
                raise ValueError("외부에서 접근 가능한 도메인을 사용해 주세요.")
        else:
            raise ValueError("IP 주소 대신 공개 도메인을 사용해 주세요.")

        allowed = [h.strip().lower() for h in os.getenv("MEDIA_TEST_ALLOWED_HOSTS", "").split(",") if h.strip()]
        if allowed and host.lower() not in allowed:
            raise ValueError("허용된 미디어 도메인이 아닙니다.")

        path = parsed.path.lower()
        if not any(path.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
            raise ValueError("MP4, WebM, MOV 또는 지원되는 이미지 파일의 직접 URL을 입력해 주세요.")
    except (ValueError, TypeError) as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError("올바른 HTTPS 주소를 입력해 주세요.") from exc
    return raw_url


def register_media_test(client: discord.Client) -> None:
    @client.tree.command(name="미디어테스트", description="외부 HTTPS 영상/사진을 디스코드 안에서 재생 테스트")
    @app_commands.describe(주소="직접 재생 가능한 HTTPS .mp4/.webm/.mov 또는 이미지 URL")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def media_test(interaction: discord.Interaction, 주소: str) -> None:
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 테스트할 수 있습니다.", ephemeral=True)
            return

        try:
            url = check_media_url(주소.strip())
        except ValueError as exc:
            await interaction.response.send_message(f"❌ {exc}", ephemeral=True)
            return

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.TextDisplay(
            "## 🎬 외부 미디어 재생 테스트\n"
            "아래 미디어의 **재생 버튼을 누르면 디스코드 내부에서 재생되는지** 확인해 주세요. "
            "외부 파일을 Discord에 업로드하지 않습니다."
        ))
        view.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(url, description="외부 HTTPS 영상/이미지 재생 테스트")
        ))
        try:
            await interaction.response.send_message(view=view)
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ 디스코드가 외부 미디어를 표시하지 못했습니다. 파일 URL, HTTPS 접근 가능 여부 및 미디어 형식을 확인해 주세요.",
                ephemeral=True,
            )
