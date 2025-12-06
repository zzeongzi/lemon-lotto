🍋 LEMON LOTTO 백서 (Whitepaper)
탈중앙화 비트코인 블록체인 기반 공정 추첨 시스템

📋 목차
개요
핵심 기술
시스템 구조
게임 메커니즘
경제 모델
보안 및 투명성
사용자 기능
거버넌스 (DAO)
기술 스택
로드맵

1. 개요

1.1 비전
LEMON LOTTO는 비트코인 블록체인의 불변성과 예측 불가능성을 활용하여, 누구도 조작할 수 없는 완전히 공정한 추첨 시스템을 제공합니다.

1.2 문제점
기존 온라인 로또/복권 시스템의 문제:

❌ 불투명한 추첨 과정 (운영자가 결과 조작 가능)
❌ 높은 수수료 (30~50%)
❌ 중앙화된 관리 (신뢰 필요)
❌ 검증 불가능 (결과를 믿을 수밖에 없음)

1.3 해결책
LEMON LOTTO의 혁신:

✅ Provably Fair (비트코인 블록 해시 기반 추첨)
✅ 초저 수수료 (1%)
✅ 완전 투명 (모든 거래 기록 공개)
✅ 즉시 검증 가능 (누구나 결과 재계산 가능)
✅ 라이트닝 네트워크 (즉시 입출금)

2. 핵심 기술

2.1 Provably Fair (증명 가능한 공정성)
원리: 비트코인 블록 해시 → 랜덤 시드 → 당첨 번호 생성
특징
    - 블록 해시는 채굴 전까지 아무도 예측 불가
    - 채굴 후에는 전 세계 누구나 검증 가능
    - 과거 결과 변조 불가능 (블록체인 불변성)

예시

# 블록 #926610의 해시
    block_hash = "00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054"

# 해시를 숫자로 변환 (시드)
    seed = int(block_hash, 16)

# 시드로 난수 생성
    random.seed(seed)
    winning_number = random.randint(1, 2100)

2.2 라이트닝 네트워크 (Lightning Network)

장점
⚡ 즉시 결제 (1초 이내)
💰 초저 수수료 (1 sat 미만)
🔒 비트코인 보안 (메인넷 정산)

통합
LNbits API를 통한 인보이스 생성/결제
라이트닝 주소 지원 (user@domain.com)

3. 시스템 구조

3.1 아키텍처

┌─────────────────────────────────────────────────┐
│                  Discord Bot                    │
│                (유저 인터페이스)                 │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼─────┐    ┌─────▼──────┐
    │ Database │    │   LNbits   │
    │ (SQLite) │    │ (Lightning)│
    └────┬─────┘    └─────┬──────┘
         │                │
         └────────┬───────┘
                  │
         ┌────────▼─────────┐
         │ Bitcoin Mempool  │
         │  (블록 데이터)    │
         └──────────────────┘

3.2 데이터베이스 스키마

users (사용자)

user_id         INTEGER PRIMARY KEY
balance         INTEGER  -- 미출금 잔액
total_spent     INTEGER  -- 총 구매액
total_won       INTEGER  -- 총 당첨액
win_count       INTEGER  -- 당첨 횟수

tickets (티켓)

id              INTEGER PRIMARY KEY
user_id         INTEGER
numbers         TEXT     -- 선택 번호
target_block    INTEGER  -- 추첨 블록
created_at      TIMESTAMP

rounds (회차)

block_height        INTEGER PRIMARY KEY
winning_numbers     TEXT
block_hash          TEXT
prize_pool          INTEGER  -- 상금풀
carryover_to_next   INTEGER  -- 이월금
processed_at        TIMESTAMP

user_wins (당첨 기록)

id              INTEGER PRIMARY KEY
user_id         INTEGER
block_height    INTEGER
amount          INTEGER  -- 당첨금
created_at      INTEGER
expires_at      INTEGER  -- 만료 시각 (30일)
is_claimed      INTEGER  -- 수령 여부
is_expired      INTEGER  -- 만료 여부

4. 게임 메커니즘

4.1 회차 시스템

추첨 주기

비트코인 블록 10개마다 1회차 (약 100분)
블록 높이 끝자리가 0인 블록에서 추첨
예: #926610, #926620, #926630...

타임라인

블록 #926601 → 티켓 판매 시작 (회차 #926610)
블록 #926605 → 판매 계속
블록 #926609 → 마지막 구매 기회
블록 #926610 → 추첨! (다음 회차 #926620 시작)

4.2 티켓 구매

가격

1장당 1 Sats

구매 제한

회차당 최대 5장/인
전체 최대 2,100장/회차

번호 선택

1~2,100 중 자동 배정
중복 불가 (선착순)

프로세스

1. /buy [수량] 입력
2. LN 인보이스 생성 (QR 코드)
3. 지갑에서 결제
4. 자동 번호 배정
5. 상금풀 증가

4.3 추첨 방식

당첨 번호 생성

def generate_winning_number(block_hash):
    seed = int(block_hash, 16)
    random.seed(seed)
    return random.randint(1, 2100)

당첨 조건

선택 번호 == 당첨 번호 → 1등 (전액)

복수 당첨자

현재는 단일 번호 시스템 (1명만 당첨)
향후 확장 가능 (n개 번호 맞추기)

5. 경제 모델

5.1 상금풀 (Prize Pool)

구성

상금풀 = 티켓 판매액 + 이전 회차 이월금 + 만료 당첨금 회수액

예시:
회차 #926610:
- 티켓 판매: 1,500 Sats
- 이전 이월금: 500 Sats
- 만료 회수: 200 Sats
→ 총 상금풀: 2,200 Sats

5.2 수수료 구조

판매 수수료:1% (상금풀에서 차감)
출금 수수료:1% (출금 시 차감)

예시:
상금풀: 10,000 Sats
수수료: 100 Sats (1%)
실제 당첨금: 9,900 Sats

출금 시:
잔액: 9,900 Sats
수수료: 99 Sats (1%)
실제 수령: 9,801 Sats

5.3 이월 시스템

당첨자 없을 때:순수 상금 → 다음 회차 상금풀에 자동 이월

만료 당첨금 회수:30일 미수령 → 자동 회수 → 다음 회차 상금풀 이월

효과
🎰 잭팟 누적 (연속 미당첨 시)
💰 대박 기회 증가
♻️ 자금 순환 보장

6. 보안 및 투명성

6.1 조작 불가능성

비트코인 블록 해시 특성

예측 불가능 (SHA-256 해시 함수)
채굴 후 확정 (변경 불가)
전 세계 검증 (수천 개 노드)

시스템 설계

봇 운영자도 결과 조작 불가
모든 계산 공개 알고리즘
과거 기록 영구 보존

6.2 검증 방법

사용자 직접 검증

# 1. 블록 해시 조회
curl https://mempool.space/api/block-height/926610

# 2. Python으로 당첨 번호 계산
python3
>>> import random
>>> hash = "00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054"
>>> random.seed(int(hash, 16))
>>> random.randint(1, 2100)
1337  # 당첨 번호

봇 명령어

/verify [블록번호] → 자동 검증 결과 표시

6.3 자금 안전성

콜드월렛 분리

운영 자금 (핫월렛): 최소한만 보유
대부분 자금: 멀티시그 콜드월렛

투명성

전체 잔액 공개
유저 부채 공개
실시간 감사 가능

7. 사용자 기능

7.1 티켓 구매

/buy [수량]
→ 1~5장 구매, LN 인보이스 생성

7.2 내역 조회

/my
→ 구매 내역, 당첨 여부 확인
→ 회차별 삭제 가능

7.3 당첨금 수령

/claim
→ 미수령 당첨금을 잔액으로 이동
→ 30일 내 필수!

7.4 출금

/withdraw [인보이스]
→ 특정 금액 출금

/withdraw_addr [주소]
→ 전액 간편 출금

7.5 통계

/stats
→ 개인 통계 (구매/당첨/수익률)

/rank
→ 서버 랭킹 (당첨금/구매액 순)

7.6 정보

/info
→ 현재 회차, 상금풀, 남은 시간

/verify [블록]
→ 과거 회차 검증

7.7 기부

/donate [금액]
→ 개발 지원 기부

/donate_info
→ 기부 현황 및 랭킹

8. 거버넌스

8.1 비상 출금 시스템

목적

시스템 오류 시 자금 보호
커뮤니티 투표로 결정

프로세스
1. 제안자: /vote_withdraw [인보이스] [사유]
2. 투표: ✅ 찬성 / ❌ 반대
3. 가결 조건: 최소 3표 & 찬성 51% 이상
4. 자동 실행: 조건 충족 시 즉시 송금

투명성

모든 제안 공개
투표 기록 저장
실행 결과 알림

8.2 향후 확장

계획 중인 기능

수수료율 조정 투표
게임 규칙 변경 제안
신규 기능 추가 결정
수익 배분 정책

9. 기술 스택

9.1 프론트엔드

Discord.py (봇 프레임워크)
discord.ui (버튼/셀렉트 메뉴)

9.2 백엔드
Python 3.10+
SQLite (데이터베이스)
aiohttp (비동기 HTTP)

9.3 블록체인
Bitcoin Mainnet (추첨 소스)
Mempool.space API (블록 데이터)

9.4 결제
Lightning Network
LNbits (지갑 API)
LNURL/Lightning Address

9.5 인프라
Linux Server (Ubuntu/Debian)
Systemd (프로세스 관리)
Docker (선택적)

10. 로드맵

✅ Phase 1: MVP (완료)
 기본 티켓 구매/추첨
 Provably Fair 구현
 LN 결제 통합
 회차별 상금풀 관리

✅ Phase 2: 고급 기능 (완료)
 30일 만료 시스템
 자동 이월 메커니즘
 비상 출금
 통계/랭킹 시스템

🔄 Phase 3: 확장 (미구현)
 다중 번호 선택 (6개 중 3개 맞추기 등)
 등급별 당첨 (1등/2등/3등)
 웹 대시보드
 모바일 앱

📊 경제 시뮬레이션

예시 시나리오

회차 #1:

판매: 1,000장 × 1 Sats = 1,000 Sats
수수료: 10 Sats (1%)
순수 상금: 990 Sats
당첨자: 없음 → 다음 회차 이월

회차 #2:

판매: 1,500 Sats
이월금: 990 Sats
총 상금풀: 2,490 Sats
수수료: 25 Sats (1%)
순수 상금: 2,465 Sats
당첨자: 1명 → user_wins 기록

회차 #3:

판매: 2,000 Sats
이월금: 0 Sats
만료 회수: 500 Sats (회차 #1 미수령분)
총 상금풀: 2,500 Sats
수수료: 25 Sats
순수 상금: 2,475 Sats

🔐 보안 고려사항

위험 요소

#LNbits 서버 해킹

대응: 콜드월렛 분리, 최소 잔액 유지

#봇 서버 다운

대응: 자동 재시작, 백업 서버

#데이터베이스 손실

대응: 일일 백업, 클라우드 동기화

#Discord 계정 해킹

대응: 2FA 필수, 권한 최소화

보안 원칙
✅ 최소 권한 원칙 (Principle of Least Privilege)
✅ 다중 서명 (Multisig Wallet)
✅ 정기 감사 (Weekly Audit)
✅ 버그 바운티 (Bug Bounty Program)

MIT License (오픈소스)
🎯 결론
LEMON LOTTO는 단순한 로또 게임이 아닙니다.

이것은:

🔓 투명성의 증명
⚡ 비트코인 기술의 실용적 활용
🤝 커뮤니티 주도 거버넌스
🌍 누구나 검증 가능한 공정성
비트코인의 철학을 게임에 담았습니다.

"Don't trust, verify."

— 신뢰하지 말고, 검증하라.

Version: 1.0.0

Last Updated: 2025-01-06

Author: LEMON Development Team