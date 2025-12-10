from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands, tasks
import qrcode
import io
import random
import aiohttp
import os
import time
import asyncio
from typing import Union, Optional
from datetime import datetime, timedelta

import blink
from blink import (
    decode_invoice,
    pay_invoice,
    get_wallet_balance,
    check_payment,
    create_invoice,
    pay_address,
    create_donate_invoice,
    check_donate_payment,
    get_donate_wallet_balance
)

from database import Database

TICKET_PRICE = 1
LOTTO_MAX_NUM = 2100
MAX_TICKETS_PER_ROUND = LOTTO_MAX_NUM 
LOTTO_PICK_COUNT = 1      
MAX_BUY_PER_USER = 5

MEMPOOL_URL = os.getenv("MEMPOOL_URL", "https://mempool.space")

db = Database()

TIMEOUT = aiohttp.ClientTimeout(total=30)

async def get_current_block_height():
    url = f"{MEMPOOL_URL}/api/blocks/tip/height"
    print(f"[DEBUG] Fetching block height from: {url}")
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200: 
                    result = int(await resp.text())
                    print(f"[DEBUG] Block height: {result}")
                    return result
                else:
                    print(f"[ERROR] HTTP {resp.status}")
        except Exception as e:
            print(f"[ERROR] Block Height Failed: {e}")
    return None

async def get_block_hash(height):
    url = f"{MEMPOOL_URL}/api/block-height/{height}"
    print(f"[DEBUG] Fetching block hash from: {url}")
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200: 
                    result = await resp.text()
                    print(f"[DEBUG] Block hash: {result[:16]}...")
                    return result
                else:
                    print(f"[ERROR] HTTP {resp.status}")
        except Exception as e:
            print(f"[ERROR] Block Hash Failed: {e}")
    return None

async def get_latest_block_info():
    url = f"{MEMPOOL_URL}/api/v1/blocks"
    print(f"[DEBUG] Fetching latest block from: {url}")
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"[DEBUG] Latest block: #{data[0]['height']}")
                    return data[0] 
                else:
                    print(f"[ERROR] HTTP {resp.status}")
        except Exception as e:
            print(f"[ERROR] Latest Block Failed: {e}")
    return None

def generate_lotto_numbers(seed_val=None):
    if seed_val is not None:
        random.seed(seed_val)
    return sorted(random.sample(range(1, LOTTO_MAX_NUM + 1), LOTTO_PICK_COUNT))

def get_target_block_for_height(current_height: int) -> int:
    """
    현재 블록 높이 기준으로, 다음 회차(끝자리가 0인 블록)를 계산.
    예: 926601 -> 926610, 926609 -> 926610, 926610 -> 926620
    """
    return ((current_height // 10) + 1) * 10

def get_next_round_block(block_height) -> int:
    """다음 회차 블록 계산"""
    return block_height + 10

# --- UI Views ---
class DeleteConfirmView(discord.ui.View):
    def __init__(self, block_to_delete, user_id):
        super().__init__(timeout=60)
        self.block_to_delete = block_to_delete
        self.user_id = user_id

    @discord.ui.button(label="네, 삭제합니다", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction, button):
        if interaction.user.id != self.user_id:
            return
        db.delete_user_tickets_by_block(self.user_id, self.block_to_delete)
        for child in self.children:
            if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                child.disabled = True
        await interaction.response.edit_message(
            content=f"🗑️ **#{self.block_to_delete} 회차** 내역이 영구 삭제되었습니다.",
            view=self
        )

    @discord.ui.button(label="취소", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction, button):
        if interaction.user.id != self.user_id:
            return
        for child in self.children:
            if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                child.disabled = True
        await interaction.response.edit_message(
            content="❌ 삭제가 취소되었습니다.",
            view=self
        )

class DeleteHistorySelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="🗑️ 삭제할 회차 선택...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        block_to_delete = int(self.values[0])
        view = DeleteConfirmView(block_to_delete, interaction.user.id)
        await interaction.response.send_message(
            f"⚠️ **#{block_to_delete} 회차**의 구매 내역을 정말로 삭제하시겠습니까?\n"
            "(삭제 후에는 복구할 수 없으며, 당첨 확인도 불가능합니다)",
            view=view,
            ephemeral=True
        )

class HistoryView(discord.ui.View):
    def __init__(self, history_blocks):
        super().__init__(timeout=60)
        if history_blocks:
            options = [
                discord.SelectOption(
                    label=f"#{block} 회차 삭제",
                    value=str(block),
                    description="이 회차의 기록을 지웁니다."
                )
                for block in history_blocks[:25]
            ]
            self.add_item(DeleteHistorySelect(options))

class DonateView(discord.ui.View):
    def __init__(
        self, 
        payment_hash, 
        payment_request, 
        amount, 
        user: Union[discord.User, discord.Member], 
        bot
    ):
        super().__init__(timeout=600)
        self.payment_hash = payment_hash
        self.payment_request = payment_request
        self.amount = amount
        self.user = user
        self.is_processed = False
        self.bot = bot
        self.message: Optional[Union[discord.Message, discord.WebhookMessage]] = None
        self.check_task = None
    
    async def start_checking(self):
        """자동 결제 확인 시작"""
        self.check_task = asyncio.create_task(self._auto_check_payment())
    
    async def _auto_check_payment(self):
        """2초마다 결제 확인 (최대 120초)"""
        print(f"[DEBUG] Auto-check started for donation: {self.payment_hash[:16]}...")
        
        for i in range(60):  # 120초 동안 2초마다 확인
            if self.is_processed:
                print(f"[DEBUG] Payment already processed, stopping auto-check")
                return
            
            await asyncio.sleep(2)
            
            try:
                is_paid = await blink.check_donate_payment(self.payment_hash)
                
                if is_paid:
                    print(f"[DEBUG] Auto-check: Payment confirmed!")
                    await self._process_donation()
                    return
            except Exception as e:
                print(f"[ERROR] Auto-check error: {e}")
        
        print(f"[DEBUG] Auto-check timeout (120s)")
    
    async def _process_donation(self):
        """기부 처리 및 DM 발송"""
        if self.is_processed:
            return
        
        self.is_processed = True
        print(f"[DEBUG] Processing donation: {self.amount} sats from user {self.user.id}")
        
        try:
            # 🔹 인보이스 상태 업데이트
            db.mark_invoice_paid(self.payment_hash)
            print(f"[DEBUG] Invoice marked as PAID: {self.payment_hash[:16]}...")
            
            # 기존 기부 기록 (donations 테이블)
            db.add_donation(self.user.id, self.amount)
            print(f"[DEBUG] Donation recorded in database")
        except Exception as e:
            print(f"[ERROR] Database error: {e}")
            return
        
        # 버튼 비활성화
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        
        # 메시지 업데이트
        try:
            if self.message:
                await self.message.edit(
                    content="✅ **기부 완료!** 감사합니다!\n💌 자세한 내용은 DM을 확인하세요!",
                    view=self
                )
                print(f"[DEBUG] Message updated")
        except Exception as e:
            print(f"[WARN] Could not edit message: {e}")
        
        # 🔹 DM으로 감사 메시지 발송
        try:
            total_donated = db.get_user_total_donation(self.user.id)
            
            embed = discord.Embed(
                title="🍋 기부 완료!",
                description="**LEMON DONATE**에 기부해주셔서 감사합니다!",
                color=0xF1C40F
            )
            embed.add_field(
                name="💰 이번 기부",
                value=f"**{self.amount:,} Sats**",
                inline=True
            )
            embed.add_field(
                name="📊 누적 기부",
                value=f"**{total_donated:,} Sats**",
                inline=True
            )
            embed.set_footer(text="여러분의 기부로 봇이 운영됩니다. 감사합니다! 🙏")
            
            await self.user.send(embed=embed)
            print(f"[DEBUG] Donation confirmation DM sent to {self.user.name}")
            
        except discord.Forbidden:
            print(f"[ERROR] Cannot send DM to {self.user.name} (DM disabled)")
            if self.message:
                try:
                    await self.message.edit(
                        content=(
                            f"✅ **기부 완료!** 감사합니다!\n\n"
                            f"💰 기부 금액: **{self.amount:,} Sats**\n\n"
                            f"⚠️ DM이 비활성화되어 있습니다."
                        ),
                        view=self
                    )
                except:
                    pass
        
        except Exception as e:
            print(f"[ERROR] Failed to send donation DM: {e}")
        
        # 공개 채널에 기부 공지
        try:
            if self.message and self.message.channel:
                await self.message.channel.send(
                    f"🍋 **{self.user.mention}**님이 **{self.amount:,} Sats**를 "
                    "**LEMON DONATE**에 기부하셨습니다! 🙏"
                )
                print(f"[DEBUG] Donation announcement sent")
        except Exception as e:
            print(f"[ERROR] Could not send announcement: {e}")
    
    async def on_timeout(self):
        """타임아웃 시 자동 확인 중지"""
        if self.check_task and not self.check_task.done():
            self.check_task.cancel()

    @discord.ui.button(label="인보이스 보기", style=discord.ButtonStyle.secondary, emoji="📋")
    async def copy_address(self, interaction, button):
        await interaction.response.send_message(
            "👇 **다음 메시지의 인보이스를 복사하세요**\n"
            "💡 텍스트를 길게 눌러 전체 선택 → 복사",
            ephemeral=True
        )
        await interaction.followup.send(
            self.payment_request,
            ephemeral=True
        )

    @discord.ui.button(label="기부 확인", style=discord.ButtonStyle.primary, emoji="🙏")
    async def check_donation(self, interaction, button):
        print(f"[DEBUG] Donation check button clicked by {interaction.user.id}")
        
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("본인만 확인할 수 있습니다.", ephemeral=True)
            return

        if self.is_processed:
            await interaction.response.send_message("✅ 이미 처리되었습니다.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        try:
            print(f"[DEBUG] Checking payment for hash: {self.payment_hash[:16]}...")
            is_paid = await blink.check_donate_payment(self.payment_hash)
            print(f"[DEBUG] Payment result: {is_paid}")
        except Exception as e:
            print(f"[ERROR] Payment check exception: {e}")
            await interaction.followup.send(
                "❌ 결제 확인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                ephemeral=True
            )
            return

        if is_paid:
            await self._process_donation()
            await interaction.followup.send("✅ 기부가 확인되었습니다!", ephemeral=True)
        else:
            print(f"[DEBUG] Payment not confirmed yet for hash: {self.payment_hash[:16]}...")
            await interaction.followup.send(
                "❌ 아직 입금이 확인되지 않았습니다.\n"
                "라이트닝 네트워크 처리 시간이 걸릴 수 있습니다. 잠시 후 다시 시도해주세요.",
                ephemeral=True
            )

class BuyView(discord.ui.View):
    def __init__(
        self, 
        payment_hash: str, 
        invoice: str, 
        amount: int, 
        ticket_count: int, 
        user: Union[discord.User, discord.Member],
        bot
    ):
        super().__init__(timeout=120)
        self.payment_hash = payment_hash
        self.invoice = invoice
        self.amount = amount
        self.ticket_count = ticket_count
        self.user = user
        self.bot = bot
        self.message: Optional[Union[discord.Message, discord.WebhookMessage]] = None
        self.checking = False

    @discord.ui.button(label="📋 인보이스 복사", style=discord.ButtonStyle.secondary)
    async def copy_invoice(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "👇 **다음 메시지의 인보이스를 복사하세요**\n"
            "💡 텍스트를 길게 눌러 전체 선택 → 복사",
            ephemeral=True
        )
        await interaction.followup.send(
            self.invoice,
            ephemeral=True
        )

    async def start_checking(self):
        if self.checking:
            return
        self.checking = True
        
        for _ in range(60):
            await asyncio.sleep(2)
            paid = await check_payment(self.payment_hash)
            
            if paid:
                print(f"[DEBUG] Payment confirmed for: {self.payment_hash[:16]}...")
                
                # 🔹 DB에서 인보이스 상태 업데이트
                db.mark_invoice_paid(self.payment_hash)
                print(f"[DEBUG] Invoice marked as PAID: {self.payment_hash[:16]}...")
                
                # 🔹 구매 처리
                await self._process_purchase()
                
                self.stop()
                return
        
        # 타임아웃
        if self.message:
            try:
                await self.message.edit(
                    content="⏰ **결제 시간 초과** (2분)\n다시 시도하려면 `/buy` 명령어를 사용하세요.",
                    view=None
                )
            except:
                pass
        self.stop()

    async def _process_purchase(self):
        """구매 처리 및 DM 발송"""
        try:
            current_height = await get_current_block_height()
            if not current_height:
                print("[ERROR] Failed to get current block height")
                return
            
            target_block = ((current_height // 10) + 1) * 10
            print(f"[DEBUG] process_purchase: current_height={current_height}, target_block={target_block}")
            
            # ✅ 수정: 각 티켓을 개별적으로 저장
            numbers = []
            for i in range(self.ticket_count):
                num = random.randint(1, LOTTO_MAX_NUM)
                numbers.append(num)
                # 🔹 각 번호를 개별 레코드로 저장
                db.add_ticket(self.user.id, [num], target_block)
                print(f"[DEBUG] Ticket {i+1}/{self.ticket_count}: {num} saved")
        
            print(f"[DEBUG] Total {self.ticket_count} tickets saved: {numbers}")
            
            # 🔹 사용자 통계 업데이트
            db.update_user_stats(self.user.id, spent=self.amount)
            
            # 🔹 상금풀 업데이트
            db.add_to_prize_pool(target_block, self.amount)
            print(f"[DEBUG] Added {self.amount} sats to prize pool for block {target_block}")
            
            # 🔹 원본 메시지 업데이트 (채널)
            if self.message:
                try:
                    await self.message.edit(
                        content="✅ **결제 확인 완료!** 티켓이 발급되었습니다.\n💌 자세한 내용은 DM을 확인하세요!",
                        view=None
                    )
                except:
                    pass
            
            # 🔹 DM으로 상세 정보 발송
            try:
                prize_pool = db.get_prize_pool(target_block)
                
                embed = discord.Embed(
                    title="🎉 로또 구매 완료!",
                    description=f"**#{target_block}** 회차 티켓이 발급되었습니다.",
                    color=0x00FF00
                )
                embed.add_field(
                    name="🎱 내 번호",
                    value=f"```{', '.join(map(str, numbers))}```",
                    inline=False
                )
                embed.add_field(
                    name="💰 이번 회차 상금풀",
                    value=f"**{prize_pool:,} Sats**",
                    inline=True
                )
                embed.add_field(
                    name="🎟️ 구매 수량",
                    value=f"{self.ticket_count}장",
                    inline=True
                )
                embed.add_field(
                    name="⛏️ 추첨 블록",
                    value=f"#{target_block}",
                    inline=True
                )
                embed.set_footer(text="추첨은 10블록마다 자동으로 진행됩니다.")
                
                await self.user.send(embed=embed)
                print(f"[DEBUG] Purchase confirmation DM sent to {self.user.name}")
                
            except discord.Forbidden:
                print(f"[ERROR] Cannot send DM to {self.user.name} (DM disabled)")
                if self.message:
                    try:
                        prize_pool = db.get_prize_pool(target_block)
                        await self.message.edit(
                            content=(
                                f"✅ **결제 확인 완료!** 티켓이 발급되었습니다.\n\n"
                                f"🎉 구매 완료!\n"
                                f"🎱 내 번호들: `{', '.join(map(str, numbers))}`\n"
                                f"💰 이번 회차 상금풀: **{prize_pool:,} Sats**\n"
                                f"추첨: **#{target_block}** 블록 (10블록마다 추첨)\n\n"
                                f"⚠️ DM이 비활성화되어 있습니다. 서버 설정에서 DM을 허용해주세요."
                            ),
                            view=None
                        )
                    except:
                        pass
            
            except Exception as e:
                print(f"[ERROR] Failed to send DM: {e}")
        
        except Exception as e:
            print(f"[ERROR] process_purchase failed: {e}")
            import traceback
            traceback.print_exc()

class EmergencyWithdrawVoteView(discord.ui.View):
    """비상 출금 투표 뷰"""
    def __init__(self, proposal_id: str, bot):
        super().__init__(timeout=None)
        self.proposal_id = proposal_id
        self.bot = bot
        self.message = None
        self.voted_users = set()

    async def update_embed(self, interaction, extra_status=None):
        """투표 결과를 실시간으로 업데이트"""
        row = db.get_dao_votes_summary(self.proposal_id)
        if not row:
            return
        
        yes_votes = row["yes_votes"]
        no_votes = row["no_votes"]
        amount = row["amount"]
        reason = row["reason"]
        status = row["status"]
        total = yes_votes + no_votes
        
        yes_pct = (yes_votes / total * 100) if total > 0 else 0
        no_pct = (no_votes / total * 100) if total > 0 else 0
        
        desc = f"**사유:** {reason}"
        if status == "passed":
            desc += "\n\n✅ **가결 및 출금 완료**"
        elif status == "failed":
            desc += "\n\n❌ **출금 실패 (결제 오류)**"
        elif status == "rejected":
            desc += "\n\n❌ **부결됨**"

        embed = discord.Embed(
            title="🚨 비상 출금 투표",
            description=desc,
            color=0xFF6B6B
        )
        embed.add_field(name="💰 출금 금액", value=f"{amount:,} Sats", inline=True)
        embed.add_field(
            name="📊 진행 상황",
            value=(
                f"✅ **찬성:** {yes_votes}표 ({yes_pct:.1f}%)\n"
                f"❌ **반대:** {no_votes}표 ({no_pct:.1f}%)\n"
                f"📋 **총 투표:** {total}표\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"가결 조건: 최소 3표 & 찬성 51% 이상"
            ),
            inline=False
        )

        footer_text = f"ID: {self.proposal_id}"
        if extra_status:
            footer_text += f" | {extra_status}"
        embed.set_footer(text=footer_text)
        
        await interaction.response.edit_message(embed=embed, view=self)

    async def try_finalize_if_needed(self, interaction):
        """가결 조건 충족 시 출금 실행 및 상태 업데이트"""
        row = db.get_dao_votes_summary(self.proposal_id)
        if not row:
            return

        yes_votes = row["yes_votes"]
        no_votes = row["no_votes"]
        status = row["status"]
        invoice = row["invoice"]
        amount = row["amount"]

        total = yes_votes + no_votes
        if status != "voting":
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            if interaction.message:
                await interaction.message.edit(view=self)
            return

        if total < 3:
            return

        yes_pct = (yes_votes / total * 100) if total > 0 else 0
        if yes_pct < 51:
            return

        print(f"[EMERGENCY] Proposal {self.proposal_id} PASSED. Paying invoice {amount} sats...")
        db.set_dao_status(self.proposal_id, "executing")

        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if interaction.message:
            await interaction.message.edit(view=self)

        reason = row.get("reason", "")
        memo_log = f"비상출금 - {reason}" if reason else "비상출금"
        print(f"[EMERGENCY] Memo: {memo_log}")

        result = await blink.pay_invoice(invoice)
        success = result.get("success", False) if isinstance(result, dict) else result

        if success:
            db.set_dao_status(self.proposal_id, "passed")
            await interaction.followup.send(
                f"✅ 비상 출금 가결 및 송금 완료: **{amount:,} Sats**\n"
                f"📝 메모: {memo_log}",
                ephemeral=False
            )
            await self.update_embed(interaction, extra_status="출금 완료")
        else:
            db.set_dao_status(self.proposal_id, "failed")
            await interaction.followup.send(
                "❌ 비상 출금 결제 실패 - 관리자에게 문의하세요.",
                ephemeral=False
            )
            await self.update_embed(interaction, extra_status="출금 실패")

    @discord.ui.button(label="✅ 찬성", style=discord.ButtonStyle.green, custom_id="vote_yes")
    async def vote_yes(self, interaction, button):
        user_id = interaction.user.id

        proposal = db.get_dao_proposal(self.proposal_id)
        if not proposal or proposal["status"] != "voting":
            await interaction.response.send_message(
                "❌ 이미 종료된 투표입니다.",
                ephemeral=True
            )
            return
        
        existing = db.get_dao_vote(self.proposal_id, user_id)
        if existing:
            await interaction.response.send_message("❌ 이미 투표하셨습니다.", ephemeral=True)
            return
        
        db.add_dao_vote(self.proposal_id, user_id, "yes")
        db.increment_dao_yes(self.proposal_id)
        
        await self.update_embed(interaction)
        await self.try_finalize_if_needed(interaction)

    @discord.ui.button(label="❌ 반대", style=discord.ButtonStyle.red, custom_id="vote_no")
    async def vote_no(self, interaction, button):
        user_id = interaction.user.id

        proposal = db.get_dao_proposal(self.proposal_id)
        if not proposal or proposal["status"] != "voting":
            await interaction.response.send_message(
                "❌ 이미 종료된 투표입니다.",
                ephemeral=True
            )
            return
        
        existing = db.get_dao_vote(self.proposal_id, user_id)
        if existing:
            await interaction.response.send_message("❌ 이미 투표하셨습니다.", ephemeral=True)
            return
        
        db.add_dao_vote(self.proposal_id, user_id, "no")
        db.increment_dao_no(self.proposal_id)
        
        await self.update_embed(interaction)


# --- Main Cog ---
class Lotto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_checked_block = 0
        self.processed_payments = set() 
        self.check_block_loop.start()
        self.status_update_loop.start()
        self.expire_wins_loop.start()
        self.expiry_reminder_loop.start()

    async def cog_unload(self):
        self.check_block_loop.cancel()
        self.status_update_loop.cancel()
        self.expire_wins_loop.cancel()
        self.expiry_reminder_loop.cancel()

    async def get_real_jackpot(self):
        """Blink 지갑 - 유저 미출금 합계 (참고용)"""
        total_wallet = await blink.get_wallet_balance()
        user_liabilities = db.get_total_user_liabilities()
        return max(0, total_wallet - user_liabilities)

    @tasks.loop(seconds=60)
    async def check_block_loop(self):
        announce_channels = db.get_channels('text')
        if not announce_channels:
            return

        current_height = await get_current_block_height()
        if not current_height:
            return

        if self.last_checked_block == 0:
            self.last_checked_block = current_height
            return

        if current_height > self.last_checked_block:
            for h in range(self.last_checked_block + 1, current_height + 1):
                if h % 10 == 0:
                    print(f"[Lotto] 회차 블록 도달! #{h} 추첨 시작...")
                    await self.announce_winner(h)
            self.last_checked_block = current_height

    async def announce_winner(self, block_height: int):
        """특정 블록 높이의 당첨자 발표"""
        print(f"[DEBUG] Announcing winner for block {block_height}")
        
        # 1. 블록 해시 가져오기
        block_hash = await get_block_hash(block_height)
        if not block_hash:
            print(f"[ERROR] Cannot get block hash for {block_height}")
            return
        
        print(f"[DEBUG] Block hash: {block_hash[:20]}...")
        
        # 2. 당첨 번호 생성
        winning_numbers = generate_lotto_numbers(int(block_hash, 16))
        winning_number = winning_numbers[0]
        print(f"[DEBUG] Winning number: {winning_number}")
        
        # 3. 추첨 결과 저장
        db.save_round_result(block_height, winning_numbers, block_hash)
        
        # 4. 상금풀 조회
        prize_pool = db.get_prize_pool(block_height)
        print(f"[DEBUG] Prize pool: {prize_pool}")
        
        # 5. 해당 회차 티켓 조회
        tickets = db.get_tickets_for_block(block_height)
        print(f"[DEBUG] Total tickets for block {block_height}: {len(tickets)}")
        
        if not tickets:
            print(f"[DEBUG] No tickets for block {block_height}")
            # 상금 이월
            next_block = ((block_height // 10) + 1) * 10
            db.add_to_prize_pool(next_block, prize_pool)
            print(f"[DEBUG] Prize pool {prize_pool} rolled over to block {next_block}")
            
            # 공지
            channels_data = db.get_channels('text')
            for ch_data in channels_data:
                channel = self.bot.get_channel(ch_data['channel_id'])
                if channel:
                    embed = discord.Embed(
                        title=f"🎲 #{block_height} 회차 추첨 결과",
                        description=f"🎱 당첨 번호: **{winning_number}**",
                        color=0x95A5A6
                    )
                    embed.add_field(
                        name="📊 결과",
                        value=f"당첨자 없음 (판매 티켓: 0장)\n💰 상금 **{prize_pool:,} Sats** → 다음 회차 이월",
                        inline=False
                    )
                    try:
                        await channel.send(embed=embed)
                    except:
                        pass
            return
        
        # 6. 당첨자 찾기
        winners = []
        for ticket in tickets:
            try:
                user_id = ticket['user_id']
                numbers_str = ticket['numbers']
                
                # numbers 파싱
                if isinstance(numbers_str, str):
                    numbers = eval(numbers_str)
                else:
                    numbers = numbers_str
                
                # 리스트가 아니면 리스트로 변환
                if not isinstance(numbers, list):
                    numbers = [numbers]
                
                print(f"[DEBUG] Checking ticket: user={user_id}, numbers={numbers}")
                
                # 당첨 확인
                if winning_number in numbers:
                    winners.append({
                        'user_id': user_id,
                        'numbers': numbers
                    })
                    print(f"[DEBUG] ✅ Winner found: user_id={user_id}, number={winning_number}")
            
            except Exception as e:
                print(f"[ERROR] Error processing ticket: {e}")
                continue
        
        print(f"[DEBUG] Total winners: {len(winners)}")
        
        # 7. 당첨 처리
        if winners:
            prize_per_winner = prize_pool // len(winners)
            print(f"[DEBUG] Prize per winner: {prize_per_winner}")
            
            winner_mentions = []
            
            for winner in winners:
                user_id = winner['user_id']
                
                # ✅ user_wins 테이블에 저장
                try:
                    db.add_user_win(
                        user_id=user_id,
                        block_height=block_height,
                        amount=prize_per_winner
                    )
                    print(f"[DEBUG] ✅ Win recorded for user {user_id}: {prize_per_winner} sats")
                except Exception as e:
                    print(f"[ERROR] Failed to record win for user {user_id}: {e}")
                    continue
                
                # ✅✅ 통계 업데이트 추가 (이 부분이 누락되었음!)
                try:
                    db.update_user_stats(user_id, won=prize_per_winner)
                    print(f"[DEBUG] ✅ Stats updated for user {user_id}")
                except Exception as e:
                    print(f"[ERROR] Failed to update stats for user {user_id}: {e}")
                
                # DM 발송
                try:
                    user = await self.bot.fetch_user(user_id)
                    embed = discord.Embed(
                        title="🎉 로또 당첨!",
                        description=f"**#{block_height}** 회차에 당첨되었습니다!",
                        color=0xFFD700
                    )
                    embed.add_field(name="🎱 당첨 번호", value=f"**{winning_number}**", inline=True)
                    embed.add_field(name="💰 당첨금", value=f"**{prize_per_winner:,} Sats**", inline=True)
                    embed.add_field(
                        name="📝 수령 방법",
                        value="`/claim` 명령어로 잔액에 추가하세요!",
                        inline=False
                    )
                    
                    await user.send(embed=embed)
                    print(f"[DEBUG] Winner DM sent to user {user_id}")
                    winner_mentions.append(f"<@{user_id}>")
                
                except discord.Forbidden:
                    print(f"[ERROR] Cannot send DM to user {user_id}")
                    winner_mentions.append(f"<@{user_id}> (DM 불가)")
                except Exception as e:
                    print(f"[ERROR] Failed to send DM to user {user_id}: {e}")
                    winner_mentions.append(f"<@{user_id}>")
            
            # 공지
            channels_data = db.get_channels('text')
            for ch_data in channels_data:
                channel = self.bot.get_channel(ch_data['channel_id'])
                if channel:
                    embed = discord.Embed(
                        title=f"🎉 #{block_height} 회차 추첨 결과",
                        description=f"🎱 당첨 번호: **{winning_number}**",
                        color=0xFFD700
                    )
                    embed.add_field(
                        name="🏆 당첨자",
                        value="\n".join(winner_mentions),
                        inline=False
                    )
                    embed.add_field(
                        name="💰 당첨금",
                        value=f"**{prize_per_winner:,} Sats** (총 {len(winners)}명)",
                        inline=False
                    )
                    embed.set_footer(text="/claim 명령어로 당첨금을 수령하세요!")
                    
                    try:
                        await channel.send("@here", embed=embed)
                    except:
                        pass
        
        else:
            # 당첨자 없음 - 이월
            print(f"[DEBUG] No winners for block {block_height}")
            next_block = ((block_height // 10) + 1) * 10
            db.add_to_prize_pool(next_block, prize_pool)
            print(f"[DEBUG] Prize pool {prize_pool} rolled over to block {next_block}")
            
            channels_data = db.get_channels('text')
            for ch_data in channels_data:
                channel = self.bot.get_channel(ch_data['channel_id'])
                if channel:
                    embed = discord.Embed(
                        title=f"🎲 #{block_height} 회차 추첨 결과",
                        description=f"🎱 당첨 번호: **{winning_number}**",
                        color=0x95A5A6
                    )
                    embed.add_field(
                        name="📊 결과",
                        value=f"당첨자 없음 (판매 티켓: {len(tickets)}장)\n💰 상금 **{prize_pool:,} Sats** → 다음 회차 이월",
                        inline=False
                    )
                    try:
                        await channel.send(embed=embed)
                    except:
                        pass

    @tasks.loop(minutes=10)
    async def status_update_loop(self):
        channels_data = db.get_channels('voice')
        if not channels_data:
            return

        current_height = await get_current_block_height()
        if not current_height:
            return
        target_block = get_target_block_for_height(current_height)
        prize_pool = db.get_prize_pool(target_block)

        new_name = f"🎰 #{target_block} 풀: {prize_pool:,} Sats"

        for ch_data in channels_data:
            channel = self.bot.get_channel(ch_data['channel_id'])
            if channel:
                try:
                    await channel.edit(name=new_name)
                except:
                    pass

    @tasks.loop(minutes=60)
    async def expire_wins_loop(self):
        """30일 지난 미수령 당첨금 회수 → 다음 회차 상금풀에 이월"""
        expired_wins = db.get_expired_unclaimed_wins()
        if not expired_wins:
            return

        now_block = await get_current_block_height()
        if not now_block:
            return
        next_round_block = get_target_block_for_height(now_block)

        total_reclaimed = 0
        for w in expired_wins:
            amount = w["amount"]
            total_reclaimed += amount
            db.mark_win_expired(w["id"])
            print(f"[EXPIRE] User {w['user_id']} win #{w['id']} expired: {amount} sats")

        if total_reclaimed > 0:
            db.add_to_prize_pool(next_round_block, total_reclaimed)
            print(f"[EXPIRE] Total {total_reclaimed} sats reclaimed → Round #{next_round_block}")

    @tasks.loop(hours=24)
    async def expiry_reminder_loop(self):
        """만료 3일 전 알림"""
        expiring = db.get_expiring_wins(days_before=3)
        
        for row in expiring:
            try:
                user = await self.bot.fetch_user(row['user_id'])
                if user:
                    days_left = (row['expires_at'] - int(time.time())) // 86400
                    
                    embed = discord.Embed(
                        title="⚠️ 당첨금 만료 임박!",
                        description=(
                            f"**#{row['block_height']} 회차** 당첨금이 **{days_left}일 후** 만료됩니다!\n\n"
                            f"💰 **금액: {row['amount']:,} Sats**\n"
                            f"📅 **만료일: <t:{row['expires_at']}:F>**\n\n"
                            f"지금 바로 수령하세요:\n"
                            f"1️⃣ `/claim` - 잔액으로 이동\n"
                            f"2️⃣ `/withdraw_addr [주소]` - 즉시 출금"
                        ),
                        color=0xFF0000
                    )
                    await user.send(embed=embed)
                    print(f"✅ 만료 알림 발송: {user.name}")
            except Exception as e:
                print(f"❌ 만료 알림 실패 ({row['user_id']}): {e}")

    channel_group = app_commands.Group(name="channel", description="알림 및 상태 채널 관리")

    @channel_group.command(name="add", description="현재 채널(또는 선택한 채널)을 봇 관리 목록에 추가합니다.")
    @commands.has_permissions(administrator=True)
    async def channel_add(self, interaction: discord.Interaction, channel: discord.TextChannel | discord.VoiceChannel):
        ch_type = 'text' if isinstance(channel, discord.TextChannel) else 'voice'
        db.add_channel(channel.id, ch_type, interaction.guild_id)
        type_str = "📜 공지(텍스트)" if ch_type == 'text' else "🔊 상태표시(음성)"
        await interaction.response.send_message(
            f"✅ **{channel.mention}**이(가) **{type_str}** 채널로 등록되었습니다."
        )

    @channel_group.command(name="remove", description="등록된 채널을 목록에서 제거합니다.")
    @commands.has_permissions(administrator=True)
    async def channel_remove(self, interaction: discord.Interaction, channel: discord.TextChannel | discord.VoiceChannel):
        db.remove_channel(channel.id)
        await interaction.response.send_message(
            f"🗑️ **{channel.mention}**이(가) 관리 목록에서 제거되었습니다."
        )

    @channel_group.command(name="list", description="현재 등록된 모든 관리 채널을 보여줍니다.")
    @commands.has_permissions(administrator=True)
    async def channel_list(self, interaction: discord.Interaction):
        text_channels = db.get_channels('text')
        voice_channels = db.get_channels('voice')

        desc = "**📜 공지 채널 (Winner Alert)**\n"
        if text_channels:
            for ch in text_channels:
                desc += f"- <#{ch['channel_id']}>\n"
        else:
            desc += "- 없음\n"

        desc += "\n**🔊 상태 채널 (Jackpot Status)**\n"
        if voice_channels:
            for ch in voice_channels:
                desc += f"- <#{ch['channel_id']}>\n"
        else:
            desc += "- 없음\n"

        embed = discord.Embed(title="📡 채널 설정 현황", description=desc, color=0x3498db)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="admin_announce", description="[관리자] 특정 회차의 결과를 수동으로 공지합니다.")
    @commands.has_permissions(administrator=True)
    async def admin_announce(self, interaction: discord.Interaction, block_height: int):
        await interaction.response.defer(ephemeral=True)
        await self.announce_winner(block_height)
        await interaction.followup.send(f"✅ #{block_height} 회차 수동 공지 완료")

    @app_commands.command(name="admin_balance", description="[관리자] 로또/기부 잔액 확인")
    @commands.has_permissions(administrator=True)
    async def admin_balance(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # DB에서 타입별 집계
        lotto_balance = db.get_lotto_balance()
        donate_balance = db.get_donate_balance()
        
        # Blink 실제 잔액
        total_balance = await blink.get_wallet_balance()
        
        # 검증
        calculated_total = lotto_balance + donate_balance
        is_valid = (calculated_total == total_balance)
        
        embed = discord.Embed(title="💰 지갑 현황", color=0x00ff00 if is_valid else 0xff0000)
        embed.add_field(name="🎰 로또 판매금", value=f"{lotto_balance:,} sats", inline=False)
        embed.add_field(name="❤️ 기부금", value=f"{donate_balance:,} sats", inline=False)
        embed.add_field(name="━━━━━━━━━━━━━━━", value="", inline=False)
        embed.add_field(name="📊 DB 합계", value=f"{calculated_total:,} sats", inline=True)
        embed.add_field(name="🏦 Blink 잔액", value=f"{total_balance:,} sats", inline=True)
        embed.add_field(
            name="✅ 검증", 
            value="✅ 일치" if is_valid else f"❌ 불일치 (차이: {abs(calculated_total - total_balance):,} sats)", 
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="info", description="현재 진행 중인 회차 정보와 예상 채굴 시간을 확인합니다.")
    async def info(self, interaction: discord.Interaction):
        print(f"[DEBUG] /info command called by {interaction.user}")
        await interaction.response.defer(ephemeral=True)
        
        latest_block = await get_latest_block_info()
        
        if not latest_block:
            jackpot = await self.get_real_jackpot()
            await interaction.followup.send(
                f"⚠️ 블록체인 정보를 가져오지 못했습니다.\n"
                f"💰 현재 잭팟(지갑 기준): **{jackpot:,} Sats**"
            )
            return

        current_height = latest_block['height']
        last_timestamp = latest_block['timestamp']

        target_block = get_target_block_for_height(current_height)
        print(f"[DEBUG] /info: current_height={current_height}, target_block={target_block}")

        blocks_remaining = target_block - current_height
        
        now = int(time.time())
        elapsed_since_last = now - last_timestamp
        
        current_block_remaining = max(0, 600 - elapsed_since_last)
        
        total_remaining = current_block_remaining + ((blocks_remaining - 1) * 600)
        
        if total_remaining > 0:
            hours = total_remaining // 3600
            mins = (total_remaining % 3600) // 60
            secs = total_remaining % 60
            
            if hours > 0:
                time_str = f"⏳ 약 **{hours}시간 {mins}분** 후"
            else:
                time_str = f"⏳ 약 **{mins}분 {secs}초** 후"
            color = 0x3498db 
        else:
            time_str = f"🔥 **곧 채굴됩니다!**"
            color = 0xe74c3c 

        prize_pool = db.get_prize_pool(target_block)
        tickets = db.get_tickets_for_block(target_block)
        tickets_sold = len(tickets)
        tickets_left = MAX_TICKETS_PER_ROUND - tickets_sold
        status_str = f"{tickets_sold} / {MAX_TICKETS_PER_ROUND} 장"
        if tickets_left == 0:
            status_str += " (🚫 매진)"

        embed = discord.Embed(title=f"🎲 #{target_block} 회차 진행 중", color=color)
        embed.add_field(
            name="💰 이번 회차 상금풀",
            value=f"**{prize_pool:,} Sats**",
            inline=False
        )
        embed.add_field(
            name="⛏️ 채굴 예상",
            value=f"{time_str}\n(남은 블록: {blocks_remaining}개)",
            inline=False
        )
        embed.add_field(name="🎟️ 판매 현황", value=status_str, inline=True)
        embed.add_field(name="📏 현재 높이", value=f"#{current_height}", inline=True)
        embed.set_footer(text=f"마지막 블록 생성: {elapsed_since_last // 60}분 {elapsed_since_last % 60}초 전")

        print(f"[DEBUG] Sending embed to user")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="buy", description="로또 구매 (1장~5장)")
    @app_commands.describe(amount="구매할 수량 (기본 1장, 최대 5장)")
    async def buy(self, interaction: discord.Interaction, amount: int = 1):
        if amount < 1 or amount > 5:
            await interaction.response.send_message(
                "❌ 한 번에 **1장~5장**까지만 구매할 수 있습니다.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        current_height = await get_current_block_height()
        if not current_height:
            await interaction.followup.send("❌ 블록체인 연결 실패")
            return

        target_block = get_target_block_for_height(current_height)
        print(f"[DEBUG] /buy: current_height={current_height}, target_block={target_block}")

        tickets_in_round = db.get_tickets_for_block(target_block)

        my_tickets_count = sum(
            1 for t in tickets_in_round if t['user_id'] == interaction.user.id
        )

        if my_tickets_count >= MAX_BUY_PER_USER:
            await interaction.followup.send(
                f"🚫 **구매 한도 초과!**\n"
                f"이번 회차(#{target_block})에서 이미 {MAX_BUY_PER_USER}장을 모두 구매하셨습니다."
            )
            return

        if my_tickets_count + amount > MAX_BUY_PER_USER:
            available_to_buy = MAX_BUY_PER_USER - my_tickets_count
            await interaction.followup.send(
                f"🚫 **구매 한도 초과!**\n"
                f"현재 {my_tickets_count}장을 보유 중입니다. "
                f"**{available_to_buy}장**만 더 구매할 수 있습니다."
            )
            return

        if len(tickets_in_round) + amount > MAX_TICKETS_PER_ROUND:
            left = MAX_TICKETS_PER_ROUND - len(tickets_in_round)
            await interaction.followup.send(
                f"🚫 **티켓 부족!**\n현재 {left}장만 남았습니다. (요청: {amount}장)"
            )
            return

        total_price = TICKET_PRICE * amount
        
        # 🔹 인보이스 생성
        invoice = await blink.create_invoice(
            total_price,
            f"Lotto - {interaction.user.name} ({amount} tickets)",
            invoice_type="lotto"
        )
        
        if not invoice:
            await interaction.followup.send("❌ 오류 발생: Blink API 연결 실패")
            return

        # 🔹 DB에 인보이스 저장 (payment_request 포함)
        db.save_invoice(
            payment_hash=invoice['payment_hash'],
            amount=invoice['amount'],
            invoice_type="lotto",
            user_id=interaction.user.id,
            payment_request=invoice['payment_request']
        )
        print(f"[DEBUG] Invoice saved to DB: {invoice['payment_hash'][:16]}... (lotto)")

        qr = qrcode.make(invoice['payment_request'])
        with io.BytesIO() as f:
            qr.save(f, 'PNG')
            f.seek(0)
            file = discord.File(f, filename='qr.png')

        view = BuyView(
            invoice['payment_hash'],
            invoice['payment_request'],
            total_price,
            amount,
            interaction.user,
            self.bot
        )
        
        msg = await interaction.followup.send(
            f"🧾 **{total_price} Sats** 결제 ({amount}장) - 입금 확인 중...",
            file=file,
            view=view,
            wait=True
        )
        
        view.message = msg
        await view.start_checking()

    @app_commands.command(name="my", description="내 로또 구매 내역 확인")
    async def my(self, interaction: discord.Interaction):
        print(f"[DEBUG] /my called by user {interaction.user.id}")
        await interaction.response.defer(ephemeral=True)
        print(f"[DEBUG] /my deferred")

        current_height = await get_current_block_height()
        print(f"[DEBUG] /my current_height: {current_height}")
        if not current_height:
            await interaction.followup.send("❌ 블록체인 정보를 불러올 수 없습니다.")
            return

        print(f"[DEBUG] /my fetching tickets for user {interaction.user.id}")
        tickets = db.get_user_tickets(interaction.user.id)
        print(f"[DEBUG] /my tickets count: {len(tickets) if tickets else 0}")
        if not tickets:
            print(f"[DEBUG] /my no tickets found")
            await interaction.followup.send("🎟️ 구매한 로또 내역이 없습니다.")
            return
        
        print(f"[DEBUG] /my processing {len(tickets)} tickets")

        print(f"[DEBUG] /my building history")
        history = {}
        for t in tickets:
            block = t['target_block']
            if block not in history:
                history[block] = []
            nums = eval(t['numbers'])
        
            # ✅ 수정: 리스트인 경우 모든 번호 추가
            if isinstance(nums, list):
                history[block].extend(nums)
            else:
                history[block].append(nums)

        print(f"[DEBUG] /my creating embed with {len(history)} rounds")
        embed = discord.Embed(title="📜 내 로또 구매 내역", color=0x3498db)

        for block, nums_list in history.items():
            print(f"[DEBUG] /my processing block {block}")
            if block > current_height:
                print(f"[DEBUG] /my block {block} is future")
                header = f"🟢 #{block} 회차 (추첨 대기)"
                nums_str = ", ".join(map(str, nums_list))
                value = f"```\n{nums_str}\n```"
            else:
                print(f"[DEBUG] /my block {block} is past, getting round_info")
                round_info = db.get_round_result(block)
                print(f"[DEBUG] /my round_info: {round_info}")
                
                if not round_info or round_info.get('winning_numbers') is None:
                    print(f"[DEBUG] /my no round_info, fetching block hash for {block}")
                    b_hash = await get_block_hash(block)
                    print(f"[DEBUG] /my block_hash: {b_hash[:20] if b_hash else None}...")
                    if b_hash:
                        print(f"[DEBUG] /my generating winning numbers for {block}")
                        seed = int(b_hash, 16)
                        w_nums = generate_lotto_numbers(seed)
                        print(f"[DEBUG] /my winning_numbers: {w_nums}")
                        db.save_round_result(block, w_nums, b_hash)
                        round_info = {'winning_numbers': str(w_nums)}
                    else:
                        print(f"[DEBUG] /my failed to get block hash for {block}")

                if round_info and round_info.get('winning_numbers') is not None:
                    print(f"[DEBUG] /my checking winners for block {block}")
                    try:
                        win_nums_str = round_info['winning_numbers']
                        print(f"[DEBUG] /my win_nums_str: {win_nums_str}, type: {type(win_nums_str)}")
                        
                        if isinstance(win_nums_str, str):
                            win_nums = eval(win_nums_str)
                        else:
                            win_nums = win_nums_str
                        
                        print(f"[DEBUG] /my win_nums: {win_nums}, type: {type(win_nums)}")
                        
                        if isinstance(win_nums, list) and len(win_nums) > 0:
                            win_num = win_nums[0]
                        else:
                            raise ValueError(f"Invalid winning_numbers format: {win_nums}")
                        
                        print(f"[DEBUG] /my win_num: {win_num}, nums_list: {nums_list}")
                        matched = [n for n in nums_list if n == win_num]
                        print(f"[DEBUG] /my matched: {matched}")
                        is_winner = len(matched) > 0
                        result_text = "🎉 당첨!" if is_winner else "💩 꽝"
                        print(f"[DEBUG] /my result: {result_text}")
                    except Exception as e:
                        print(f"[ERROR] /my winner check error: {e}")
                        print(f"[ERROR] /my round_info: {round_info}")
                        result_text = "⚠️ 오류"
                        win_num = "?"
                        is_winner = False

                    print(f"[DEBUG] /my creating header for block {block}")
                    header = (
                        f"🏁 #{block} 회차 - 당첨번호: {win_num} │ {result_text}"
                    )
                    print(f"[DEBUG] /my header created")

                    my_nums_display = []
                    for n in nums_list:
                        if n == win_num:
                            my_nums_display.append(f"\u001b[0;32m{n}\u001b[0m")
                        else:
                            my_nums_display.append(f"\u001b[0;31m{n}\u001b[0m")

                    nums_str = " ".join(my_nums_display)
                    value = f"```ansi\n{nums_str}\n```"
                else:
                    header = f"⚠️ #{block} 회차 (결과 오류)"
                    value = f"```\n{', '.join(map(str, nums_list))}\n```"

            print(f"[DEBUG] /my adding field to embed")
            embed.add_field(name=header, value=value, inline=False)
            print(f"[DEBUG] /my field added")

        embed.set_footer(text=f"현재 블록 높이: #{current_height}")
        print(f"[DEBUG] /my creating view")
        view = HistoryView(list(history.keys()))
        print(f"[DEBUG] /my sending response")
        await interaction.followup.send(embed=embed, view=view)
        print(f"[DEBUG] /my completed")

    @app_commands.command(name="claim", description="만료 전 내 당첨금을 지갑 잔액으로 수령합니다.")
    async def claim(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        pending = db.get_pending_wins(interaction.user.id)
        if not pending:
            await interaction.followup.send("✅ 수령 가능한 당첨금이 없습니다.", ephemeral=True)
            return

        total = 0
        claimed_rounds = []
        for w in pending:
            total += w["amount"]
            claimed_rounds.append(f"#{w['block_height']}")
            db.mark_win_claimed(w["id"])

        if total > 0:
            db.add_balance(interaction.user.id, total)
            rounds_str = ", ".join(claimed_rounds)
            await interaction.followup.send(
                f"💰 **{total:,} Sats**를 잔액으로 수령했습니다!\n"
                f"📋 회차: {rounds_str}\n"
                f"현재 잔액은 `/stats`에서 확인할 수 있습니다.",
                ephemeral=True
            )
        else:
            await interaction.followup.send("✅ 수령 가능한 금액이 없습니다.", ephemeral=True)

    @app_commands.command(name="withdraw", description="[인보이스] 당첨금 출금 (미수령 당첨금 자동 수령 + 출금)")
    async def withdraw(self, interaction: discord.Interaction, invoice: str):
        await interaction.response.defer(ephemeral=True)

        pending = db.get_pending_wins(interaction.user.id)
        if pending:
            total_claimed = 0
            for w in pending:
                total_claimed += w["amount"]
                db.mark_win_claimed(w["id"])
            if total_claimed > 0:
                db.add_balance(interaction.user.id, total_claimed)
                await interaction.followup.send(
                    f"✅ 미수령 당첨금 **{total_claimed:,} Sats**를 자동으로 수령했습니다.",
                    ephemeral=True
                )

        user_data = db.get_user(interaction.user.id)
        if not user_data or user_data['balance'] <= 0:
            await interaction.followup.send(
                "❌ 출금할 당첨금이 없습니다.",
                ephemeral=True
            )
            return

        total_balance = user_data['balance']
        fee_reserve = max(1, int(total_balance * 0.01)) 
        real_amount = total_balance - fee_reserve

        if real_amount <= 0:
            await interaction.followup.send(
                "❌ 잔액 부족 (최소 수수료 필요)",
                ephemeral=True
            )
            return

        decoded = await blink.decode_invoice(invoice)
        if not decoded:
            await interaction.followup.send("❌ 잘못된 인보이스입니다.")
            return

        req_sats = decoded.get("amount", 0)

        if req_sats == 0:
            await interaction.followup.send(
                "❌ **금액이 지정되지 않은 인보이스**입니다. 금액을 포함해서 생성해주세요."
            )
            return

        if req_sats > real_amount:
            msg = (
                f"❌ **금액 초과!**\n"
                f"수수료 제외 **{real_amount:,} Sats** 이하로 생성해주세요.\n"
                f"(요청: {req_sats:,} / 가능: {real_amount:,})"
            )
            await interaction.followup.send(msg)
            return

        result = await blink.pay_invoice(invoice)
        paid = result.get("success", False) if isinstance(result, dict) else result
        
        if paid:
            db.clear_balance(interaction.user.id)
            await interaction.followup.send(
                f"✅ **{req_sats:,} Sats** 출금 완료!\n"
                f"💰 총 잔액 **{total_balance:,} Sats** 소멸됨"
            )
        else:
            await interaction.followup.send("❌ 송금 실패")

    @app_commands.command(name="withdraw_addr", description="[간편] 라이트닝 주소로 전액 출금 (미수령 당첨금 자동 수령 + 출금)")
    async def withdraw_addr(self, interaction: discord.Interaction, address: str):
        await interaction.response.defer(ephemeral=True)

        pending = db.get_pending_wins(interaction.user.id)
        if pending:
            total_claimed = 0
            for w in pending:
                total_claimed += w["amount"]
                db.mark_win_claimed(w["id"])
            if total_claimed > 0:
                db.add_balance(interaction.user.id, total_claimed)
                await interaction.followup.send(
                    f"✅ 미수령 당첨금 **{total_claimed:,} Sats**를 자동으로 수령했습니다.",
                    ephemeral=True
                )

        user_data = db.get_user(interaction.user.id)
        if not user_data or user_data['balance'] <= 0:
            await interaction.followup.send(
                "❌ 출금할 당첨금이 없습니다.",
                ephemeral=True
            )
            return

        total_balance = user_data['balance']
        fee_reserve = max(1, int(total_balance * 0.01))
        real_amount = total_balance - fee_reserve 

        if real_amount <= 0:
            await interaction.followup.send("❌ 잔액 부족", ephemeral=True)
            return

        result = await blink.pay_address(address, real_amount)
        paid = result.get("success", False) if isinstance(result, dict) else result
        
        if paid:
            db.clear_balance(interaction.user.id)
            await interaction.followup.send(
                f"✅ **{address}**로 **{real_amount:,} Sats** 송금 완료!\n"
                f"💰 총 잔액 **{total_balance:,} Sats** 소멸됨"
            )
        else:
            await interaction.followup.send(
                "❌ 송금 실패 (주소를 확인하거나 잠시 후 다시 시도하세요)"
            )

    @app_commands.command(name="donate", description="[기부] LEMON DONATE에 기부합니다.")
    async def donate(self, interaction: discord.Interaction, amount: int):
        if amount < 1:
            await interaction.response.send_message(
                "❌ 최소 1 Sats 이상",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        invoice = await blink.create_donate_invoice(
            amount,
            f"Donation - {interaction.user.name}"
        )
        
        if not invoice: 
            await interaction.followup.send("❌ 인보이스 생성 실패")
            return

        db.save_invoice(
            payment_hash=invoice['payment_hash'],
            amount=invoice['amount'],
            invoice_type="donate",
            user_id=interaction.user.id,
            payment_request=invoice['payment_request']
        )
        print(f"[DEBUG] Invoice saved to DB: {invoice['payment_hash'][:16]}... (donate)")

        qr = qrcode.make(invoice['payment_request'])
        with io.BytesIO() as f:
            qr.save(f, 'PNG')
            f.seek(0)
            file = discord.File(f, filename='qr.png')

        view = DonateView(
            invoice['payment_hash'],
            invoice['payment_request'],
            amount,
            interaction.user,
            self.bot
        )
        msg = await interaction.followup.send(
            f"🙏 **{amount:,} Sats** 기부 (LEMON DONATE)\n"
            f"💡 입금 시 자동으로 확인됩니다.",
            file=file,
            view=view
        )
        view.message = msg
        await view.start_checking()

    @app_commands.command(name="donate_info", description="🍋 LEMON DONATE 기부 현황 및 랭킹 확인")
    async def donate_info(self, interaction: discord.Interaction):
        total = db.get_total_donations()
        ranking = db.get_donation_ranking(limit=10)

        desc = f"### 🍋 현재 총 기부금: **{total:,} Sats**\n\n"
        desc += "**🏆 기부 천사 TOP 10**\n"
        if ranking:
            for i, row in enumerate(ranking, 1):
                desc += (
                    f"{i}. <@{row['user_id']}> : "
                    f"**{row['total_donated']:,} Sats**\n"
                )
        else:
            desc += "아직 기부 내역이 없습니다. 첫 번째 기부자가 되어보세요!"

        embed = discord.Embed(
            title="🍋 LEMON DONATE 현황",
            description=desc,
            color=0xF1C40F
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="나의 로또 통계 및 출금 가능액 확인")
    async def stats(self, interaction: discord.Interaction):
        user = db.get_user(interaction.user.id)
        if not user:
            await interaction.response.send_message("📊 기록 없음", ephemeral=True)
            return

        spent = user['total_spent']
        won = user['total_won']
        balance = user['balance']
        roi = ((won - spent) / spent * 100) if spent > 0 else 0
        total_donated = db.get_user_total_donation(interaction.user.id)
        
        pending_wins = db.get_pending_wins(interaction.user.id)
        pending_amount = sum(w['amount'] for w in pending_wins)

        if balance > 0:
            fee_reserve = max(1, int(balance * 0.01))
            real_amount = max(0, balance - fee_reserve)
            balance_str = (
                f"**{real_amount:,} Sats**\n"
                f"(총 {balance:,} - 수수료 {fee_reserve:,})"
            )
        else:
            balance_str = "0 Sats"

        # 🎨 설명 추가
        description = ""
        if roi > 0:
            description = "🎉 **수익 중!** 계속 행운을 빕니다!"
        elif roi < 0:
            description = "💪 **다음 기회에!** 포기하지 마세요!"
        else:
            description = "🎲 **손익분기점!** 다음 회차를 노려보세요!"
        
        if total_donated > 0:
            description += f"\n🍋 **기부 천사** - 총 {total_donated:,} Sats 기부"

        embed = discord.Embed(
            title=f"📊 {interaction.user.name}님의 통계",
            description=description,
            color=0x3498db if roi >= 0 else 0xe74c3c
        )
        
        embed.add_field(name="💰 출금 가능 금액", value=balance_str, inline=False)
        
        if pending_amount > 0:
            embed.add_field(
                name="⏳ 미수령 당첨금",
                value=f"**{pending_amount:,} Sats** ({len(pending_wins)}건)\n`/claim`으로 수령하세요",
                inline=False
            )
        
        # 로또 통계
        embed.add_field(name="💸 로또 구매액", value=f"{spent:,} Sats", inline=True)
        embed.add_field(name="🏆 총 당첨금", value=f"{won:,} Sats", inline=True)
        embed.add_field(name="📈 수익률", value=f"{roi:.2f}%", inline=True)
        embed.add_field(name="🎫 당첨 횟수", value=f"{user['win_count']}회", inline=True)
        
        # 기부 통계
        if total_donated > 0:
            embed.add_field(name="🍋 총 기부액", value=f"{total_donated:,} Sats", inline=True)
            # 기부 랭킹 조회
            ranking = db.get_donation_ranking(limit=100)
            user_rank = next((i+1 for i, r in enumerate(ranking) if r['user_id'] == interaction.user.id), None)
            if user_rank:
                embed.add_field(name="🏆 기부 랭킹", value=f"{user_rank}위", inline=True)
        
        embed.set_footer(
            text="💡 출금: /withdraw_addr [주소] | 기부: /donate [금액]"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rank", description="서버 로또 랭킹")
    @app_commands.choices(sort_by=[
        app_commands.Choice(name="총 당첨금 순", value="total_won"),
        app_commands.Choice(name="총 구매액 순", value="total_spent")
    ])
    async def rank(self, interaction: discord.Interaction, sort_by: str = "total_won"):
        rows = db.get_ranking(order_by=sort_by)
        if not rows:
            await interaction.response.send_message("📊 데이터 없음", ephemeral=True)
            return

        desc = ""
        for i, row in enumerate(rows, 1):
            desc += f"{i}. <@{row['user_id']}> : **{row[sort_by]:,} Sats**\n"

        embed = discord.Embed(title="🏆 랭킹", description=desc, color=0xFFD700)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="verify", description="검증")
    async def verify(self, interaction: discord.Interaction, block_height: int):
        await interaction.response.defer()

        block_hash = await get_block_hash(block_height)
        if not block_hash:
            await interaction.followup.send("❌ 블록 정보 없음")
            return

        nums = generate_lotto_numbers(int(block_hash, 16))
        round_info = db.get_round_result(block_height)
        
        if round_info:
            prize_pool = round_info.get('prize_pool', 0)
            pool_str = f"당시 회차 상금풀: {prize_pool:,} Sats"
        else:
            pool_str = "상금풀 정보 없음"

        desc = (
            "**🧮 당첨 번호 계산 방식 (Provably Fair)**\n"
            "1. 비트코인 블록체인에서 **블록 해시**를 가져옵니다.\n"
            "2. 해시값을 숫자로 변환하여 **랜덤 시드(Seed)**로 사용합니다.\n"
            "3. 이 시드를 통해 **1~2100 사이의 번호**를 결정합니다.\n"
            "👉 *블록 해시는 채굴 전까지 아무도 예측할 수 없으므로 조작이 불가능합니다.*"
        )

        embed = discord.Embed(
            title=f"🔍 #{block_height} 회차 검증",
            description=desc,
            color=0x9b59b6
        )
        embed.add_field(name="👑 당첨 번호", value=f"**{nums}**", inline=False)
        embed.add_field(name="🔗 블록 해시", value=f"`{block_hash}`", inline=False)
        embed.set_footer(text=pool_str)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="vote_withdraw",
        description="[긴급] 비상 출금 투표를 시작합니다."
    )
    async def vote_withdraw(self, interaction: discord.Interaction, invoice: str, reason: str):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ 서버에서만 사용 가능합니다.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        print(f"[DEBUG] Decoding invoice: {invoice[:50]}...")
        decoded = await decode_invoice(invoice)
        
        if not decoded:
            await interaction.followup.send("❌ 인보이스 디코딩 실패", ephemeral=True)
            return

        print(f"[DEBUG] Decoded data: {decoded}")

        amount_sats = decoded.get("amount", 0)
        print(f"[DEBUG] Final amount (sats): {amount_sats}")

        if amount_sats == 0:
            await interaction.followup.send(
                "❌ 인보이스 금액을 확인할 수 없습니다.",
                ephemeral=True
            )
            return

        proposal_id = f"withdraw_{int(time.time())}"

        db.create_dao_proposal(
            proposal_id=proposal_id,
            proposal_type="withdraw",
            invoice=invoice,
            amount=amount_sats,
            reason=reason,
            proposer_id=interaction.user.id,
            proposer_name=str(interaction.user)
        )

        embed = discord.Embed(
            title="🚨 비상 출금 투표",
            description=f"**사유:** {reason}",
            color=0xFF6B6B
        )
        embed.add_field(name="💰 출금 금액", value=f"{amount_sats:,} Sats", inline=True)
        embed.add_field(name="📝 제안자", value=interaction.user.mention, inline=True)
        embed.add_field(
            name="📊 진행 상황",
            value=(
                f"✅ **찬성:** 0표 (0.0%)\n"
                f"❌ **반대:** 0표 (0.0%)\n"
                f"📋 **총 투표:** 0표\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"가결 조건: 최소 3표 & 찬성 51% 이상"
            ),
            inline=False
        )
        embed.set_footer(text=f"ID: {proposal_id}")

        view = EmergencyWithdrawVoteView(proposal_id, self.bot)
        
        message = await interaction.followup.send(
            content=(
                "@everyone\n"
                "🚨 **긴급 비상 출금 투표가 시작되었습니다!**\n"
                "아래 버튼을 눌러 투표에 참여해주세요."
            ),
            embed=embed,
            view=view
        )
        view.message = message

        print(f"[DEBUG] Emergency proposal created: {proposal_id}, Amount: {amount_sats} sats")


async def setup(bot):
    await bot.add_cog(Lotto(bot))
