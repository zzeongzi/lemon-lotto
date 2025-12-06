import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Discord 설정
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

# LNbits 설정
LNBITS_URL = os.getenv("LNBITS_URL")
LNBITS_ADMIN_KEY = os.getenv("LNBITS_ADMIN_KEY")
LNBITS_INVOICE_KEY = os.getenv("LNBITS_INVOICE_KEY")

# 게임 설정
TICKET_PRICE = int(os.getenv("TICKET_PRICE", "1"))
MAX_TICKETS_PER_USER = int(os.getenv("MAX_TICKETS_PER_USER", "5"))
MAX_TOTAL_TICKETS = int(os.getenv("MAX_TOTAL_TICKETS", "2100"))
FEE_PERCENTAGE = float(os.getenv("FEE_PERCENTAGE", "1"))

# 데이터베이스
DB_PATH = os.getenv("DB_PATH", "lotto.db")

# 검증
if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN이 .env 파일에 없습니다!")
if not LNBITS_URL:
    raise ValueError("❌ LNBITS_URL이 .env 파일에 없습니다!")
if not LNBITS_ADMIN_KEY:
    raise ValueError("❌ LNBITS_ADMIN_KEY가 .env 파일에 없습니다!")