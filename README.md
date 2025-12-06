# 🍋 LEMON LOTTO

**Provably Fair Bitcoin Lightning Lottery Bot**

비트코인 블록체인 기반 공정 추첨 시스템 Discord 봇

## ✨ 특징

- ⚡ **Lightning Network** 즉시 결제
- 🎲 **Provably Fair** 블록 해시 기반 추첨
- 💰 **초저 수수료** 1%
- 🔍 **완전 투명** 모든 결과 검증 가능
- 🏛️ **DAO 거버넌스** 커뮤니티 투표

## 🚀 설치 방법

### 1. 저장소 클론
\`\`\`bash
git clone https://github.com/your-username/lemon-lotto.git
cd lemon-lotto
\`\`\`

### 2. 패키지 설치
\`\`\`bash
pip3 install -r requirements.txt
\`\`\`

### 3. 환경변수 설정
\`\`\`bash
cp .env.example .env
nano .env
\`\`\`

`.env` 파일에 다음 정보 입력:
- Discord Bot Token
- LNbits API Key & URL
- Admin User ID

### 4. 봇 실행
\`\`\`bash
python3 bot.py
\`\`\`

## 📋 명령어

| 명령어 | 설명 |
|--------|------|
| `/buy [수량]` | 티켓 구매 (1~5장) |
| `/my` | 내 티켓 조회 |
| `/info` | 현재 회차 정보 |
| `/claim` | 당첨금 수령 |
| `/withdraw [invoice]` | 출금 |
| `/stats` | 개인 통계 |
| `/rank` | 서버 랭킹 |
| `/verify [블록]` | 결과 검증 |

## 🛠️ 기술 스택

- **Python 3.10+**
- **Discord.py**
- **SQLite**
- **Lightning Network (LNbits)**
- **Bitcoin Mempool API**

## 📖 백서

자세한 내용은 [WHITEPAPER.md](WHITEPAPER.md) 참조

## 🔐 보안

- 민감한 정보는 `.env` 파일에 저장
- `.env` 파일은 절대 커밋하지 마세요
- `.env.example` 파일을 참고하여 설정

## 🤝 기여

Pull Request 환영합니다!

1. Fork
2. Feature Branch 생성 (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Pull Request 생성

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 참조

## 📞 문의

- Issues: [GitHub Issues](https://github.com/your-username/lemon-lotto/issues)
- Discord: [서버 초대 링크]

---

**⚠️ 주의:** 이 봇은 실제 비트코인을 사용합니다. 테스트넷에서 먼저 테스트하세요.
