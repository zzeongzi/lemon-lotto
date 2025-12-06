import sqlite3
import os
from datetime import datetime, timedelta

DB_FILE = "lotto.db"

class Database:
    def __init__(self):
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # 사용자 테이블 (balance: 미출금 당첨금)
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY, 
                        balance INTEGER DEFAULT 0,
                        total_spent INTEGER DEFAULT 0,
                        total_won INTEGER DEFAULT 0,
                        win_count INTEGER DEFAULT 0
                    )''')
        
        # 티켓 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        numbers TEXT,
                        target_block INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
        
        # 회차 결과 테이블 + 상금풀 + 이월 기록
        c.execute('''CREATE TABLE IF NOT EXISTS rounds (
                        block_height INTEGER PRIMARY KEY,
                        winning_numbers TEXT,
                        block_hash TEXT,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        prize_pool INTEGER DEFAULT 0,
                        carryover_to_next INTEGER DEFAULT 0
                    )''')
        
        # 잭팟(장부상) 테이블 - 참고용
        c.execute('''CREATE TABLE IF NOT EXISTS jackpot (
                        id INTEGER PRIMARY KEY, 
                        amount INTEGER DEFAULT 0
                    )''')
        
        # 채널 설정 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS channels (
                        channel_id INTEGER PRIMARY KEY,
                        type TEXT,
                        guild_id INTEGER
                    )''')
        
        # 기부 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS donations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        amount INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')

        # 비상 출금 제안 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS dao_proposals (
                        proposal_id TEXT PRIMARY KEY,
                        proposal_type TEXT NOT NULL,
                        invoice TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        reason TEXT NOT NULL,
                        proposer_id INTEGER NOT NULL,
                        proposer_name TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'voting',
                        yes_votes INTEGER NOT NULL DEFAULT 0,
                        no_votes INTEGER NOT NULL DEFAULT 0
                    )''')

        # 비상 출금 투표 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS dao_votes (
                        proposal_id TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        vote TEXT NOT NULL,
                        PRIMARY KEY (proposal_id, user_id)
                    )''')

        # 🔹 유저 회차별 당첨 기록 테이블 (user_wins)
        c.execute('''CREATE TABLE IF NOT EXISTS user_wins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        block_height INTEGER NOT NULL,
                        amount INTEGER NOT NULL,
                        created_at INTEGER NOT NULL,
                        expires_at INTEGER NOT NULL,
                        is_claimed INTEGER NOT NULL DEFAULT 0,
                        is_expired INTEGER NOT NULL DEFAULT 0
                    )''')

        # 스키마 마이그레이션(기존 DB에 컬럼 없을 수 있음)
        try:
            c.execute("ALTER TABLE rounds ADD COLUMN prize_pool INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE rounds ADD COLUMN carryover_to_next INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        # 초기 잭팟 레코드 생성
        c.execute("INSERT OR IGNORE INTO jackpot (id, amount) VALUES (1, 0)")
        
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(DB_FILE)

    # --- [신규] 사용자들의 미출금 잔액 총합 구하기 ---
    def get_total_user_liabilities(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT SUM(balance) FROM users")
        result = c.fetchone()[0]
        conn.close()
        return result if result else 0

    # --- 티켓 관련 ---
    def save_ticket(self, user_id, numbers, target_block):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO tickets (user_id, numbers, target_block) VALUES (?, ?, ?)",
                  (user_id, str(numbers), target_block))
        
        # 사용자 없으면 생성
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()

    def get_tickets_by_block(self, block_height):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tickets WHERE target_block = ?", (block_height,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_user_tickets(self, user_id):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tickets WHERE user_id = ? ORDER BY target_block DESC", (user_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_user_tickets_by_block(self, user_id, block_height):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM tickets WHERE user_id = ? AND target_block = ?", (user_id, block_height))
        conn.commit()
        conn.close()

    # --- 사용자/통계 관련 ---
    def update_user_stats(self, user_id, spent=0, won=0):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        
        if spent > 0:
            c.execute(
                "UPDATE users SET total_spent = total_spent + ? WHERE user_id = ?",
                (spent, user_id)
            )
        
        if won > 0:
            c.execute(
                "UPDATE users SET total_won = total_won + ?, win_count = win_count + 1 WHERE user_id = ?",
                (won, user_id)
            )
            
        conn.commit()
        conn.close()

    def add_balance(self, user_id, amount):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()

    def get_user(self, user_id):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def clear_balance(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def get_ranking(self, order_by="total_won", limit=10):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        query = f"SELECT * FROM users ORDER BY {order_by} DESC LIMIT ?"
        c.execute(query, (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # --- 잭팟 관련 (참고용) ---
    def update_jackpot(self, amount):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE jackpot SET amount = amount + ? WHERE id = 1", (amount,))
        conn.commit()
        conn.close()

    def get_jackpot(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT amount FROM jackpot WHERE id = 1")
        res = c.fetchone()
        conn.close()
        return res[0] if res else 0

    def reset_jackpot(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE jackpot SET amount = 0 WHERE id = 1")
        conn.commit()
        conn.close()

    # --- 회차 결과 및 상금풀 관련 ---
    def save_round_result(self, block_height, winning_numbers, block_hash):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO rounds (block_height, winning_numbers, block_hash) VALUES (?, ?, ?)",
            (block_height, str(winning_numbers), block_hash)
        )
        conn.commit()
        conn.close()

    def get_round_result(self, block_height):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM rounds WHERE block_height = ?", (block_height,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def add_to_round_pool(self, block_height, amount):
        """특정 회차의 prize_pool에 금액 추가 (티켓 구매/이월 시 호출)"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO rounds (block_height, winning_numbers, block_hash, prize_pool) VALUES (?, NULL, NULL, 0)",
            (block_height,)
        )
        c.execute(
            "UPDATE rounds SET prize_pool = prize_pool + ? WHERE block_height = ?",
            (amount, block_height)
        )
        conn.commit()
        conn.close()

    def get_round_pool(self, block_height):
        """해당 회차의 prize_pool 조회"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT prize_pool FROM rounds WHERE block_height = ?", (block_height,))
        row = c.fetchone()
        conn.close()
        if not row:
            return 0
        return row["prize_pool"] if row["prize_pool"] is not None else 0

    def set_carryover(self, block_height, amount):
        """해당 회차에서 다음 회차로 이월된 금액 기록"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE rounds SET carryover_to_next = ? WHERE block_height = ?",
            (amount, block_height)
        )
        conn.commit()
        conn.close()

    # --- user_wins 관련 ---
    def add_user_win(self, user_id, block_height, amount, expires_after_days=30):
        """유저 회차별 당첨 기록 추가 (당첨 시 호출)"""
        conn = self.get_connection()
        c = conn.cursor()
        now_ts = int(datetime.utcnow().timestamp())
        expire_ts = int((datetime.utcnow() + timedelta(days=expires_after_days)).timestamp())
        c.execute(
            """INSERT INTO user_wins (user_id, block_height, amount, created_at, expires_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, block_height, amount, now_ts, expire_ts)
        )
        conn.commit()
        conn.close()

    def get_pending_wins(self, user_id):
        """아직 claim/만료되지 않은 당첨 기록"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        now_ts = int(datetime.utcnow().timestamp())
        c.execute(
            """SELECT * FROM user_wins
               WHERE user_id = ?
                 AND is_claimed = 0
                 AND is_expired = 0
                 AND expires_at > ?""",
            (user_id, now_ts)
        )
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def mark_win_claimed(self, win_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE user_wins SET is_claimed = 1 WHERE id = ?",
            (win_id,)
        )
        conn.commit()
        conn.close()

    def get_expired_unclaimed_wins(self):
        """만료됐지만 아직 수령 안 한 당첨 내역들"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        now_ts = int(datetime.utcnow().timestamp())
        c.execute(
            """SELECT * FROM user_wins
               WHERE is_claimed = 0
                 AND is_expired = 0
                 AND expires_at <= ?""",
            (now_ts,)
        )
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def mark_win_expired(self, win_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE user_wins SET is_expired = 1 WHERE id = ?",
            (win_id,)
        )
        conn.commit()
        conn.close()

    # --- 채널 관리 ---
    def add_channel(self, channel_id, ch_type, guild_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO channels (channel_id, type, guild_id) VALUES (?, ?, ?)", 
            (channel_id, ch_type, guild_id)
        )
        conn.commit()
        conn.close()

    def remove_channel(self, channel_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        conn.commit()
        conn.close()

    def get_channels(self, ch_type):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM channels WHERE type = ?", (ch_type,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # --- 기부 관련 ---
    def add_donation(self, user_id, amount):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO donations (user_id, amount) VALUES (?, ?)", (user_id, amount))
        conn.commit()
        conn.close()

    def get_total_donations(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT SUM(amount) FROM donations")
        res = c.fetchone()[0]
        conn.close()
        return res if res else 0

    def get_donation_ranking(self, limit=10):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('''
            SELECT user_id, SUM(amount) as total_donated 
            FROM donations 
            GROUP BY user_id 
            ORDER BY total_donated DESC 
            LIMIT ?
        ''', (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # --- 비상 출금(DAO) 관련 메서드 ---

    def create_dao_proposal(
        self,
        proposal_id: str,
        proposal_type: str,
        invoice: str,
        amount: int,
        reason: str,
        proposer_id: int,
        proposer_name: str
    ):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO dao_proposals
                (proposal_id, proposal_type, invoice, amount, reason, proposer_id, proposer_name, created_at, status)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, strftime('%s','now'), 'voting')
            """,
            (proposal_id, proposal_type, invoice, amount, reason, proposer_id, proposer_name)
        )
        conn.commit()
        conn.close()

    def get_dao_proposal(self, proposal_id: str):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM dao_proposals WHERE proposal_id = ?", (proposal_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def add_dao_vote(self, proposal_id: str, user_id: int, vote: str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO dao_votes (proposal_id, user_id, vote) VALUES (?, ?, ?)",
            (proposal_id, user_id, vote)
        )
        conn.commit()
        conn.close()

    def get_dao_vote(self, proposal_id: str, user_id: int):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM dao_votes WHERE proposal_id = ? AND user_id = ?",
            (proposal_id, user_id)
        )
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def increment_dao_yes(self, proposal_id: str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE dao_proposals SET yes_votes = yes_votes + 1 WHERE proposal_id = ?",
            (proposal_id,)
        )
        conn.commit()
        conn.close()

    def increment_dao_no(self, proposal_id: str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE dao_proposals SET no_votes = no_votes + 1 WHERE proposal_id = ?",
            (proposal_id,)
        )
        conn.commit()
        conn.close()

    def set_dao_status(self, proposal_id: str, status: str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE dao_proposals SET status = ? WHERE proposal_id = ?",
            (status, proposal_id)
        )
        conn.commit()
        conn.close()

    def get_dao_votes_summary(self, proposal_id: str):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT yes_votes, no_votes, amount, reason, status, invoice FROM dao_proposals WHERE proposal_id = ?",
            (proposal_id,)
        )
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
