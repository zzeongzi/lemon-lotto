import discord
import sqlite3
import hashlib
import random
import string
from discord.ext import commands, tasks
from discord import app_commands
from lnbits import create_invoice, check_payment, create_withdraw_link

TICKET_PRICE = 100   # 티켓 가격 (sats)
TOTAL_CARDS = 210000 # 전체 카드 수

class LottoEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_payments_loop.start()

    def get_db(self):
        return sqlite3.connect('lotto.db')

    @app_commands.command(name="buy", description="로또 티켓 구매")
    async def buy(self, interaction: discord.Interaction, amount: int):
        if amount < 1:
            await interaction.response.send_message("최소 1장 이상 구매해야 합니다.", ephemeral=True)
            return

        total_price = amount * TICKET_PRICE
        memo = f"Buy {amount} tickets - {interaction.user.name}"
        invoice = await create_invoice(total_price, memo)

        if not invoice:
            await interaction.response.send_message("오류 발생", ephemeral=True)
            return

        # 결제 대기 등록
        self.bot.pending_payments[invoice['payment_hash']] = {
            "user_id": interaction.user.id,
            "amount": amount,
            "channel_id": interaction.channel_id
        }
        
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={invoice['payment_request']}"
        embed = discord.Embed(title=f"🎟️ {amount}장 구매 ({total_price} sats)", color=discord.Color.blue())
        embed.set_image(url=qr_url)
        embed.add_field(name="Invoice", value=f"```{invoice['payment_request']}```")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(seconds=3)
    async def check_payments_loop(self):
        if not self.bot.pending_payments:
            return

        to_remove = []
        for p_hash, data in self.bot.pending_payments.items():
            if await check_payment(p_hash):
                await self.issue_tickets(data['user_id'], data['amount'], data['channel_id'])
                to_remove.append(p_hash)
        
        for p_hash in to_remove:
            del self.bot.pending_payments[p_hash]

    async def issue_tickets(self, user_id, amount, channel_id):
        conn = self.get_db()
        cursor = conn.cursor()
        
        # 현재 회차 확인
        cursor.execute("SELECT round_id FROM rounds WHERE status='OPEN'")
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO rounds (status) VALUES ('OPEN')")
            round_id = cursor.lastrowid
        else:
            round_id = row[0]

        # 티켓 발급
        user_salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        owner_hash = hashlib.sha256(f"{user_id}:{user_salt}".encode()).hexdigest()
        
        issued = []
        for _ in range(amount):
            while True:
                num = random.randint(0, TOTAL_CARDS - 1)
                try:
                    cursor.execute("INSERT INTO tickets (round_id, card_number, owner_hash) VALUES (?, ?, ?)", 
                                   (round_id, num, owner_hash))
                    issued.append(num)
                    break
                except:
                    continue
        
        conn.commit()
        conn.close()

        # DM 발송
        user = self.bot.get_user(user_id)
        if user:
            await user.send(f"🎟️ 티켓 발급 완료!\n번호: {issued}\n🔑 검증키(Salt): `{user_salt}` (절대 잃어버리지 마세요!)")

async def setup(bot):
    await bot.add_cog(LottoEngine(bot))
