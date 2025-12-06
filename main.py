import discord
import asyncio
import os
import aiosqlite
from discord.ext import commands
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class LemonBot(commands.Bot):
    def __init__(self):
        # 봇 권한 설정
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.db = None  # DB 변수 미리 생성

    async def setup_hook(self):
        # 1. 데이터베이스 연결 (봇이 켜질 때 딱 한 번 실행)
        self.db = await aiosqlite.connect("lotto.db")
        print("✅ 데이터베이스(lotto.db) 연결 성공")

        # 2. Cogs(기능) 로드
        try:
            # cogs 폴더 안에 있는 lotto.py를 불러옵니다.
            await self.load_extension("cogs.lotto")
            print("✅ cogs.lotto 로드 성공")
        except Exception as e:
            print(f"❌ cogs.lotto 로드 실패: {e}")
        
        # 3. 명령어 동기화 (빗금 명령어 등록)
        await self.tree.sync()
        print("✅ 디스코드 명령어 동기화 완료")

    async def close(self):
        # 봇이 꺼질 때 DB도 안전하게 닫기
        if self.db:
            await self.db.close()
        await super().close()

    async def on_ready(self):
        print(f"🚀 로그인 성공: {self.user} (ID: {self.user.id})")
        print("🍋 레몬 봇이 준비되었습니다!")

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ .env 파일에서 DISCORD_TOKEN을 찾을 수 없습니다.")
        return
    
    bot = LemonBot()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Ctrl+C로 종료 시 깔끔하게 끄기
        pass
