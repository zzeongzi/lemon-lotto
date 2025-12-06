import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import sys

load_dotenv()

# 토큰 가져오기 및 검증을 한 번에
def get_token() -> str:
    """환경변수에서 토큰을 가져오고 검증"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ 에러: DISCORD_TOKEN이 .env 파일에 없습니다!")
        print("💡 .env 파일을 생성하고 DISCORD_TOKEN을 설정하세요.")
        sys.exit(1)
    return token

TOKEN = get_token()  # 이제 타입은 str로 확정
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    if bot.user:
        print(f'✅ 봇 로그인: {bot.user.name} (ID: {bot.user.id})')
    print(f'🔗 연결된 서버: {len(bot.guilds)}개')
    
    try:
        synced = await bot.tree.sync()
        print(f'⚡ Slash 명령어 {len(synced)}개 동기화 완료')
    except Exception as e:
        print(f'❌ 명령어 동기화 실패: {e}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f'❌ 에러: {error}')

async def load_extensions():
    try:
        await bot.load_extension('cogs.lotto')
        print('✅ Lotto Cog 로드 완료')
    except Exception as e:
        print(f'❌ Cog 로드 실패: {e}')

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)  # ← 이제 경고 없음!

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
