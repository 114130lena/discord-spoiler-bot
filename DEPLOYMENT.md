# /미디어테스트 및 Ubuntu 업데이트
`/미디어테스트 주소:https://your-domain.example/test.mp4` 명령어로 외부 HTTPS 미디어의 Discord Media Gallery 내 재생 가능 여부를 검증합니다.

## 시작
- Python 환경에 `pip install -r requirements.txt`를 실행하세요. Media Gallery를 위해 discord.py 2.6 이상이 필요합니다.
- `TOKEN` 환경변수로 봇 토큰을 설정하고 기존 방식대로 `python main.py`를 실행하세요.
- 명령어는 관리자만 사용할 수 있습니다. 공개 HTTPS 미디어의 **직접 파일 링크**를 사용합니다.
- `MEDIA_TEST_ALLOWED_HOSTS=media.example.com`을 설정하면 이 도메인만 받습니다(권장).
- 코드 업데이트만으로 실행 중인 프로세스가 새 버전으로 바뀌지 않습니다. 재시작해야 합니다.
- 서버에서 외부 미디어를 Discord가 표시할 수 있더라도 무제한 대용량 재생은 보장되지 않습니다. PC/모바일에서 직접 검증하세요.

## 선택 사항: Ubuntu 홈서버 1분 간격 자동 반영
**현재 서버의 실제 배포 경로와 systemd 서비스명을 확인한 뒤에만 설치하세요.** 다른 봇(어비스봇 등)에 적용하지 마세요.

1. `deploy/update.env.example`을 복사하여 `/etc/discord-spoiler-update.env`를 만들고 실제 값으로 변경하세요. 비밀값을 GitHub에 커밋하지 마세요.
2. `sudo install -m 0755 deploy/update.sh /usr/local/bin/discord-spoiler-update`
3. `sudo install -m 0644 deploy/discord-spoiler-update.service /etc/systemd/system/`
4. `sudo install -m 0644 deploy/discord-spoiler-update.timer /etc/systemd/system/`
5. `sudo systemctl daemon-reload && sudo systemctl enable --now discord-spoiler-update.timer`
6. 즉시 동기화: `sudo systemctl start discord-spoiler-update.service`
7. 확인: `systemctl status discord-spoiler-update.timer; journalctl -u discord-spoiler-update.service -n 50 --no-pager`

업데이트 스크립트는 로컬 수정이 있을 경우 자동 업데이트를 중단하고, git fast-forward만 허용합니다. 변경이 있을 때만 의존성 설치 및 대상 서비스 재시작을 수행합니다. 업데이트 실패 시 수동 복구가 필요할 수 있습니다.
