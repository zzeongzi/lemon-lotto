import discord
import sqlite3
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View
from datetime import datetime, timedelta
from lnbits import pay_invoice

# 설정: 투표 기간 24시간, 최소 10명 참여
VOTE_DURATION_HOURS = 24
MIN_QUORUM = 10 

class Governance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_proposals_loop.start()

    def get_db(self):
        return sqlite3.connect('lotto.db')

    # 1. 비상 출금 제안 (관리자 전용)
    @app_commands.command(name="propose_withdraw", description="[관리자] 비상 자금 출금 제안을 올립니다.")
    @app_commands.describe(amount="출금할 금액(sats)", address="받을 라이트닝 주소(Bolt11)", reason="출금 사유")
    @commands.has_permissions(administrator=True)
    async def propose_withdraw(self, interaction: discord.Interaction, amount: int, address: str, reason: str):
        # 관리자 권한 체크는 디스코드 설정에 따름
        end_time = datetime.now() + timedelta(hours=VOTE_DURATION_HOURS)
        
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO proposals (proposer_id, amount, reason, target_address, ends_at)
            VALUES (?, ?, ?, ?, ?)
        """, (interaction.user.id, amount, reason, address, end_time))
        proposal_id = cursor.lastrowid
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title=f"🚨 비상 출금 제안 (#{proposal_id})",
            description=f"관리자가 커뮤니티 자금 출금을 요청했습니다.\n여러분의 투표로 결정됩니다.",
            color=discord.Color.orange()
        )
        embed.add_field(name="금액", value=f"{amount} sats", inline=True)
        embed.add_field(name="사유", value=reason, inline=False)
        embed.add_field(name="마감", value=f"<t:{int(end_time.timestamp())}:R>", inline=False)
        embed.set_footer(text=f"최소 {MIN_QUORUM}명 참여 & 찬성 다수 시 자동 집행")

        view = VoteView(proposal_id)
        await interaction.response.send_message(embed=embed, view=view)

    # 2. 투표 결과 집계 및 집행 (1분마다 체크)
    @tasks.loop(minutes=1)
    async def check_proposals_loop(self):
        conn = self.get_db()
        cursor = conn.cursor()
        now = datetime.now()
        
        # 마감됐는데 아직 처리 안 된(VOTING) 안건
        cursor.execute("""
            SELECT id, amount, target_address, votes_yes, votes_no 
            FROM proposals 
            WHERE status='VOTING' AND ends_at < ?
        """, (now,))
        
        for row in cursor.fetchall():
            pid, amount, address, yes, no = row
            total_votes = yes + no
            
            if total_votes >= MIN_QUORUM and yes > no:
                # 통과 -> 송금 시도
                try:
                    await pay_invoice(address)
                    cursor.execute("UPDATE proposals SET status='EXECUTED' WHERE id=?", (pid,))
                    print(f"✅ 제안 #{pid} 집행 완료: {amount} sats 송금됨.")
                except Exception as e:
                    print(f"❌ 제안 #{pid} 송금 실패: {e}")
                    cursor.execute("UPDATE proposals SET status='ERROR' WHERE id=?", (pid,))
            else:
                # 부결
                cursor.execute("UPDATE proposals SET status='REJECTED' WHERE id=?", (pid,))
        
        conn.commit()
        conn.close()

# 투표 버튼 UI
class VoteView(View):
    def __init__(self, proposal_id):
        super().__init__(timeout=None)
        self.proposal_id = proposal_id

    async def cast_vote(self, interaction, vote_type):
        conn = sqlite3.connect('lotto.db')
        cursor = conn.cursor()
        
        # 중복 투표 체크
        cursor.execute("SELECT vote_type FROM votes WHERE proposal_id=? AND user_id=?", (self.proposal_id, interaction.user.id))
        if cursor.fetchone():
            conn.close()
            await interaction.response.send_message("이미 투표하셨습니다!", ephemeral=True)
            return

        cursor.execute("INSERT INTO votes VALUES (?, ?, ?)", (self.proposal_id, interaction.user.id, vote_type))
        
        if vote_type == "YES":
            cursor.execute("UPDATE proposals SET votes_yes = votes_yes + 1 WHERE id=?", (self.proposal_id,))
        else:
            cursor.execute("UPDATE proposals SET votes_no = votes_no + 1 WHERE id=?", (self.proposal_id,))
        
        conn.commit()
        
        # 현재 스코어 확인
        cursor.execute("SELECT votes_yes, votes_no FROM proposals WHERE id=?", (self.proposal_id,))
        y, n = cursor.fetchone()
        conn.close()
        
        await interaction.response.send_message(f"투표 완료! (찬성: {y} vs 반대: {n})", ephemeral=True)

    @discord.ui.button(label="찬성", style=discord.ButtonStyle.green)
    async def vote_yes(self, interaction: discord.Interaction, button: Button):
        await self.cast_vote(interaction, "YES")

    @discord.ui.button(label="반대", style=discord.ButtonStyle.red)
    async def vote_no(self, interaction: discord.Interaction, button: Button):
        await self.cast_vote(interaction, "NO")

async def setup(bot):
    await bot.add_cog(Governance(bot))