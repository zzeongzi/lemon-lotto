<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍋 LEMON LOTTO - Whitepaper</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
            color: #2c3e50;
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 24px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.4);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: white;
            padding: 80px 50px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 15s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        header h1 {
            font-size: 4em;
            margin-bottom: 15px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }

        header .subtitle {
            font-size: 1.5em;
            opacity: 0.95;
            margin-top: 15px;
            position: relative;
            z-index: 1;
        }

        header .meta {
            margin-top: 30px;
            font-size: 1em;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        nav {
            background: linear-gradient(to right, #2c3e50, #34495e);
            padding: 25px 50px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        nav ul {
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
        }

        nav a {
            color: #ffd89b;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.05em;
            transition: all 0.3s;
            padding: 8px 16px;
            border-radius: 8px;
            position: relative;
        }

        nav a::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            width: 0;
            height: 3px;
            background: #ffd89b;
            transition: all 0.3s;
            transform: translateX(-50%);
        }

        nav a:hover::after {
            width: 100%;
        }

        nav a:hover {
            background: rgba(255, 216, 155, 0.1);
            color: #fff;
        }

        main {
            padding: 60px;
        }

        section {
            margin-bottom: 80px;
        }

        h2 {
            color: #19547b;
            font-size: 3em;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 5px solid #ffd89b;
            position: relative;
        }

        h2::before {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 100px;
            height: 5px;
            background: #19547b;
        }

        h3 {
            color: #2c3e50;
            font-size: 2.2em;
            margin: 40px 0 25px 0;
            padding-left: 20px;
            border-left: 6px solid #ffd89b;
        }

        h4 {
            color: #34495e;
            font-size: 1.6em;
            margin: 30px 0 18px 0;
        }

        p {
            margin-bottom: 20px;
            text-align: justify;
            font-size: 1.05em;
        }

        ul, ol {
            margin-left: 40px;
            margin-bottom: 20px;
        }

        li {
            margin-bottom: 12px;
            font-size: 1.05em;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            border-radius: 12px;
            overflow: hidden;
        }

        th, td {
            padding: 20px;
            text-align: left;
            border: none;
        }

        th {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: white;
            font-weight: 700;
            font-size: 1.1em;
        }

        tr:nth-child(even) {
            background: #f8f9fa;
        }

        tr:hover {
            background: #e8f4f8;
            transition: all 0.3s;
        }

        .mermaid {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 45px;
            border-radius: 16px;
            margin: 40px 0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            border: 2px solid #e0e6ed;
        }

        pre {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: #ecf0f1;
            padding: 30px;
            border-radius: 16px;
            overflow-x: auto;
            margin: 30px 0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            border-left: 6px solid #ffd89b;
            font-size: 0.95em;
        }

        code {
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }

        .feature-card {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            transform: rotate(45deg);
        }

        .feature-card:hover {
            transform: translateY(-12px) scale(1.02);
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }

        .feature-card h4 {
            color: white;
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }

        .feature-card p {
            position: relative;
            z-index: 1;
        }

        .roadmap {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 40px;
            border-radius: 16px;
            margin: 30px 0;
            border-left: 8px solid #ffd89b;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        }

        .roadmap h4 {
            color: #19547b;
            margin-bottom: 20px;
            font-size: 1.8em;
        }

        .roadmap ul {
            list-style: none;
            margin-left: 0;
        }

        .roadmap li {
            padding: 12px 0;
            padding-left: 40px;
            position: relative;
            font-size: 1.1em;
        }

        .roadmap li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
            font-size: 1.5em;
            width: 30px;
            height: 30px;
            background: #d4edda;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .roadmap li.pending:before {
            content: "○";
            color: #95a5a6;
            background: #e9ecef;
        }

        .roadmap li.progress:before {
            content: "⟳";
            color: #f39c12;
            background: #fff3cd;
        }

        footer {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 60px;
            text-align: center;
        }

        footer h3 {
            color: #ffd89b;
            border: none;
            padding: 0;
            margin-bottom: 20px;
        }

        footer a {
            color: #ffd89b;
            text-decoration: none;
            font-weight: 700;
            transition: all 0.3s;
        }

        footer a:hover {
            color: #fff;
            text-decoration: underline;
        }

        .highlight {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: white;
            padding: 40px;
            border-radius: 16px;
            margin: 40px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        }

        .highlight h4 {
            color: white;
            margin-bottom: 15px;
        }

        .emoji {
            font-size: 1.8em;
            margin-right: 15px;
        }

        .problem-box {
            background: linear-gradient(135deg, #ffe6e6 0%, #ffcccc 100%);
            border-left: 8px solid #e74c3c;
            padding: 30px;
            margin: 30px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(231, 76, 60, 0.2);
        }

        .solution-box {
            background: linear-gradient(135deg, #e8f8f5 0%, #d4edda 100%);
            border-left: 8px solid #27ae60;
            padding: 30px;
            margin: 30px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(39, 174, 96, 0.2);
        }

        .info-box {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 8px solid #2196f3;
            padding: 30px;
            margin: 30px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 2.5em;
            }

            main {
                padding: 30px;
            }

            nav ul {
                flex-direction: column;
                align-items: center;
            }

            h2 {
                font-size: 2em;
            }

            h3 {
                font-size: 1.6em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍋 LEMON LOTTO</h1>
            <div class="subtitle">탈중앙화 비트코인 블록체인 기반 공정 추첨 시스템</div>
            <div class="meta">
                <strong>Version:</strong> 1.0.0 | 
                <strong>Last Updated:</strong> 2025-01-06 | 
                <strong>Team:</strong> LEMON Development
            </div>
        </header>

        <nav>
            <ul>
                <li><a href="#overview">개요</a></li>
                <li><a href="#tech">핵심 기술</a></li>
                <li><a href="#architecture">시스템 구조</a></li>
                <li><a href="#game">게임 메커니즘</a></li>
                <li><a href="#economy">경제 모델</a></li>
                <li><a href="#security">보안</a></li>
                <li><a href="#features">사용자 기능</a></li>
                <li><a href="#dao">거버넌스</a></li>
                <li><a href="#roadmap">로드맵</a></li>
            </ul>
        </nav>

        <main>
            <!-- 1. 개요 -->
            <section id="overview">
                <h2>1. 개요</h2>

                <h3>1.1 비전</h3>
                <p>
                    <strong>LEMON LOTTO</strong>는 비트코인 블록체인의 불변성과 예측 불가능성을 활용하여, 
                    누구도 조작할 수 없는 <strong>완전히 공정한 추첨 시스템</strong>을 제공합니다.
                </p>

                <div class="mermaid">
                    mindmap
                      root((🍋 LEMON LOTTO))
                        Provably Fair
                          Bitcoin Block Hash
                          Verifiable
                          Immutable
                        Lightning Network
                          Instant Payment
                          Low Fee
                          Scalable
                        Transparency
                          Open Source
                          Public Records
                          Community Driven
                        Security
                          Cold Wallet
                          Multi-sig
                          Auditable
                </div>

                <h3>1.2 문제점</h3>
                <div class="problem-box">
                    <h4>❌ 기존 온라인 로또/복권 시스템의 문제</h4>
                    <ul>
                        <li><strong>불투명한 추첨 과정</strong> - 운영자가 결과 조작 가능</li>
                        <li><strong>높은 수수료</strong> - 30~50%의 과도한 수수료</li>
                        <li><strong>중앙화된 관리</strong> - 운영자에 대한 맹목적 신뢰 필요</li>
                        <li><strong>검증 불가능</strong> - 결과를 믿을 수밖에 없음</li>
                    </ul>
                </div>

                <h3>1.3 해결책</h3>
                <div class="solution-box">
                    <h4>✅ LEMON LOTTO의 혁신</h4>
                    <ul>
                        <li><strong>Provably Fair</strong> - 비트코인 블록 해시 기반 추첨</li>
                        <li><strong>초저 수수료</strong> - 단 1%의 합리적 수수료</li>
                        <li><strong>완전 투명</strong> - 모든 거래 기록 공개</li>
                        <li><strong>즉시 검증 가능</strong> - 누구나 결과 재계산 가능</li>
                        <li><strong>라이트닝 네트워크</strong> - 즉시 입출금</li>
                    </ul>
                </div>

                <div class="mermaid">
                    graph LR
                        A[기존 복권] -->|문제| B[중앙화된 신뢰]
                        A -->|문제| C[느린 정산]
                        A -->|문제| D[높은 수수료]
                        A -->|문제| E[검증 불가]
                        
                        F[LEMON LOTTO] -->|해결| G[암호학적 검증]
                        F -->|해결| H[Lightning 즉시 정산]
                        F -->|해결| I[1% 수수료]
                        F -->|해결| J[완전 투명]
                        
                        style A fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:3px
                        style F fill:#27ae60,color:#fff,stroke:#229954,stroke-width:3px
                        style B fill:#e74c3c,color:#fff
                        style C fill:#e74c3c,color:#fff
                        style D fill:#e74c3c,color:#fff
                        style E fill:#e74c3c,color:#fff
                        style G fill:#27ae60,color:#fff
                        style H fill:#27ae60,color:#fff
                        style I fill:#27ae60,color:#fff
                        style J fill:#27ae60,color:#fff
                </div>
            </section>

            <!-- 2. 핵심 기술 -->
            <section id="tech">
                <h2>2. 핵심 기술</h2>

                <h3>2.1 Provably Fair (증명 가능한 공정성)</h3>
                
                <h4>원리</h4>
                <div class="mermaid">
                    graph TD
                        A[Bitcoin Block Hash] -->|SHA-256| B[Random Seed]
                        B -->|Python random.seed| C[Pseudo-Random Generator]
                        C -->|random.randint 1-2100| D[Winning Number]
                        
                        E[Anyone Can Verify] -.->|Check| A
                        E -.->|Recalculate| B
                        E -.->|Confirm| D
                        
                        style A fill:#f39c12,color:#fff,stroke:#e67e22,stroke-width:3px
                        style B fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:3px
                        style C fill:#9b59b6,color:#fff,stroke:#8e44ad,stroke-width:3px
                        style D fill:#27ae60,color:#fff,stroke:#229954,stroke-width:3px
                        style E fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:3px
                </div>

                <div class="info-box">
                    <h4>🔍 특징</h4>
                    <ul>
                        <li>블록 해시는 채굴 전까지 <strong>아무도 예측 불가</strong></li>
                        <li>채굴 후에는 전 세계 <strong>누구나 검증 가능</strong></li>
                        <li>과거 결과 <strong>변조 불가능</strong> (블록체인 불변성)</li>
                    </ul>
                </div>

                <h4>알고리즘</h4>
                <pre><code># 블록 #926610의 해시
block_hash = "00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054"

# 해시를 숫자로 변환 (시드)
seed = int(block_hash, 16)

# 시드로 난수 생성
random.seed(seed)
winning_number = random.randint(1, 2100)

print(f"당첨 번호: {winning_number}")</code></pre>

                <h3>2.2 라이트닝 네트워크</h3>
                
                <div class="feature-grid">
                    <div class="feature-card">
                        <h4><span class="emoji">⚡</span>즉시 결제</h4>
                        <p>1초 이내 거래 완료<br>실시간 티켓 구매</p>
                    </div>
                    <div class="feature-card">
                        <h4><span class="emoji">💰</span>초저 수수료</h4>
                        <p>1 sat 미만의 수수료<br>소액 거래 최적화</p>
                    </div>
                    <div class="feature-card">
                        <h4><span class="emoji">🔒</span>비트코인 보안</h4>
                        <p>메인넷 정산 보장<br>검증된 보안 프로토콜</p>
                    </div>
                </div>

                <div class="mermaid">
                    sequenceDiagram
                        participant U as 👤 User
                        participant W as 💼 Wallet
                        participant LN as ⚡ Lightning
                        participant B as 🤖 Bot
                        
                        U->>B: /buy 3
                        B->>LN: Create Invoice (3 sats)
                        LN-->>B: Invoice + QR Code
                        B-->>U: Display Payment Request
                        U->>W: Open Wallet
                        W->>LN: Pay Invoice
                        LN->>B: Payment Confirmed (Webhook)
                        B->>B: Assign Numbers
                        B-->>U: ✅ Purchase Complete!
                        
                        Note over U,B: Total Time: < 5 seconds
                </div>
            </section>

            <!-- 3. 시스템 구조 -->
            <section id="architecture">
                <h2>3. 시스템 구조</h2>

                <h3>3.1 전체 아키텍처</h3>
                <div class="mermaid">
                    graph TB
                        subgraph Frontend
                            A[Discord Bot<br/>사용자 인터페이스]
                        end
                        
                        subgraph Backend
                            B[Database<br/>SQLite]
                            C[LNbits API<br/>Lightning Network]
                        end
                        
                        subgraph External
                            D[Bitcoin Mempool<br/>블록 데이터 소스]
                        end
                        
                        A -->|Store Data| B
                        A -->|Payment| C
                        B -->|Query Blocks| D
                        C -->|Verify| D
                        
                        style A fill:#5865F2,stroke:#fff,color:#fff,stroke-width:4px
                        style B fill:#27ae60,stroke:#fff,color:#fff,stroke-width:4px
                        style C fill:#f39c12,stroke:#fff,color:#fff,stroke-width:4px
                        style D fill:#e74c3c,stroke:#fff,color:#fff,stroke-width:4px
                </div>

                <h3>3.2 데이터 흐름</h3>
                <div class="mermaid">
                    sequenceDiagram
                        participant User as 👤 사용자
                        participant Bot as 🤖 Discord Bot
                        participant DB as 💾 Database
                        participant LN as ⚡ LNbits
                        participant BTC as ₿ Bitcoin

                        rect rgb(200, 230, 255)
                        Note over User,LN: 티켓 구매 단계
                        User->>Bot: /buy 3
                        Bot->>LN: 인보이스 생성 (3 sats)
                        LN-->>Bot: Lightning Invoice + QR
                        Bot-->>User: 결제 요청 표시
                        User->>LN: ⚡ 결제 완료
                        LN->>Bot: 웹훅 알림
                        Bot->>DB: 티켓 저장
                        Bot-->>User: ✅ 구매 완료 (번호 배정)
                        end
                        
                        rect rgb(255, 230, 200)
                        Note over Bot,BTC: ⏰ 추첨 시간 (블록 #926610)
                        Bot->>BTC: 블록 해시 요청
                        BTC-->>Bot: Block Hash
                        Bot->>DB: 참가자 목록 조회
                        Bot->>Bot: 🎲 당첨 번호 계산
                        Bot->>DB: 당첨자 확인
                        end
                        
                        rect rgb(200, 255, 200)
                        Note over Bot,User: 당첨금 지급
                        Bot->>DB: user_wins 기록
                        Bot->>LN: 💰 당첨금 전송 준비
                        Bot-->>User: 🎉 당첨 알림
                        User->>Bot: /claim
                        Bot->>DB: 잔액 업데이트
                        Bot-->>User: ✅ 수령 완료
                        end
                </div>

                <h3>3.3 데이터베이스 스키마</h3>
                <div class="mermaid">
                    erDiagram
                        USERS ||--o{ TICKETS : purchases
                        USERS ||--o{ USER_WINS : wins
                        ROUNDS ||--o{ TICKETS : contains
                        ROUNDS ||--o{ USER_WINS : generates
                        
                        USERS {
                            int user_id PK
                            int balance
                            int total_spent
                            int total_won
                            int win_count
                        }
                        
                        TICKETS {
                            int id PK
                            int user_id FK
                            text numbers
                            int target_block FK
                            timestamp created_at
                        }
                        
                        ROUNDS {
                            int block_height PK
                            text winning_numbers
                            text block_hash
                            int prize_pool
                            int carryover_to_next
                            timestamp processed_at
                        }
                        
                        USER_WINS {
                            int id PK
                            int user_id FK
                            int block_height FK
                            int amount
                            int created_at
                            int expires_at
                            int is_claimed
                            int is_expired
                        }
                </div>
            </section>

            <!-- 4. 게임 메커니즘 -->
            <section id="game">
                <h2>4. 게임 메커니즘</h2>

                <h3>4.1 회차 시스템</h3>
                
                <div class="info-box">
                    <h4>⏰ 추첨 주기</h4>
                    <ul>
                        <li>비트코인 블록 <strong>10개마다 1회차</strong> (약 100분)</li>
                        <li>블록 높이 끝자리가 <strong>0인 블록</strong>에서 추첨</li>
                        <li>예: #926610, #926620, #926630...</li>
                    </ul>
                </div>

                <div class="mermaid">
                    gantt
                        title 회차 타임라인
                        dateFormat X
                        axisFormat %H:%M
                        
                        section 회차 #926610
                        판매 시작 (블록 #926601)      :a1, 0, 10m
                        판매 진행 (블록 #926605)      :a2, after a1, 40m
                        마지막 구매 (블록 #926609)    :a3, after a2, 40m
                        추첨! (블록 #926610)          :milestone, m1, after a3, 0m
                        
                        section 회차 #926620
                        판매 시작                      :b1, after m1, 10m
                        판매 진행                      :b2, after b1, 80m
                        추첨                          :milestone, m2, after b2, 0m
                </div>

                <h3>4.2 티켓 구매 프로세스</h3>
                <div class="mermaid">
                    stateDiagram-v2
                        [*] --> CommandInput: /buy [수량]
                        CommandInput --> Validation: 입력 검증
                        Validation --> InvoiceGeneration: ✅ 유효
                        Validation --> Error: ❌ 무효
                        Error --> [*]: 오류 메시지
                        
                        InvoiceGeneration --> PaymentPending: QR 코드 표시
                        PaymentPending --> PaymentConfirmed: 사용자 결제
                        PaymentPending --> PaymentExpired: 10분 경과
                        PaymentExpired --> [*]: 취소
                        
                        PaymentConfirmed --> NumberAssignment: 번호 자동 배정
                        NumberAssignment --> PrizePoolUpdate: 상금풀 증가
                        PrizePoolUpdate --> [*]: ✅ 구매 완료
                </div>

                <h3>4.3 추첨 방식</h3>
                <div class="mermaid">
                    flowchart TD
                        A[추첨 블록 도달] --> B{블록 해시 조회}
                        B --> C[해시를 정수로 변환]
                        C --> D[random.seed 설정]
                        D --> E[당첨 번호 생성 1-2100]
                        E --> F{당첨자 확인}
                        F -->|있음| G[user_wins 기록]
                        F -->|없음| H[상금 이월]
                        G --> I[당첨 알림]
                        H --> J[다음 회차 상금풀 증가]
                        I --> K[End]
                        J --> K
                        
                        style A fill:#f39c12,color:#fff
                        style E fill:#3498db,color:#fff
                        style G fill:#27ae60,color:#fff
                        style H fill:#e74c3c,color:#fff
                </div>
            </section>

            <!-- 5. 경제 모델 -->
            <section id="economy">
                <h2>5. 경제 모델</h2>

                <h3>5.1 상금풀 구성</h3>
                <div class="mermaid">
                    pie title 상금풀 구성 요소
                        "티켓 판매액" : 70
                        "이전 회차 이월금" : 20
                        "만료 당첨금 회수" : 10
                </div>

                <h3>5.2 자금 흐름</h3>
                <div class="mermaid">
                    graph LR
                        A[티켓 판매] -->|99%| B[상금풀]
                        A -->|1%| C[수수료]
                        
                        D[이전 이월금] --> B
                        E[만료 회수] --> B
                        
                        B -->|당첨자 있음| F[당첨금 지급]
                        B -->|당첨자 없음| G[다음 회차 이월]
                        
                        F -->|30일 내 수령| H[사용자 잔액]
                        F -->|30일 미수령| I[자동 회수]
                        I --> E
                        
                        H -->|출금| J[Lightning 송금]
                        J -->|1% 수수료| C
                        
                        style A fill:#3498db,color:#fff
                        style B fill:#f39c12,color:#fff
                        style C fill:#e74c3c,color:#fff
                        style F fill:#27ae60,color:#fff
                        style G fill:#9b59b6,color:#fff
                </div>

                <h3>5.3 경제 시뮬레이션</h3>
                <table>
                    <thead>
                        <tr>
                            <th>회차</th>
                            <th>판매액</th>
                            <th>이월금</th>
                            <th>총 상금풀</th>
                            <th>수수료</th>
                            <th>순수 상금</th>
                            <th>결과</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>#926610</td>
                            <td>1,000 sats</td>
                            <td>0 sats</td>
                            <td>1,000 sats</td>
                            <td>10 sats</td>
                            <td>990 sats</td>
                            <td>미당첨 → 이월</td>
                        </tr>
                        <tr>
                            <td>#926620</td>
                            <td>1,500 sats</td>
                            <td>990 sats</td>
                            <td>2,490 sats</td>
                            <td>25 sats</td>
                            <td>2,465 sats</td>
                            <td>당첨자 1명</td>
                        </tr>
                        <tr>
                            <td>#926630</td>
                            <td>2,000 sats</td>
                            <td>0 sats</td>
                            <td>2,500 sats</td>
                            <td>25 sats</td>
                            <td>2,475 sats</td>
                            <td>미당첨 → 이월</td>
                        </tr>
                        <tr>
                            <td>#926640</td>
                            <td>2,100 sats</td>
                            <td>2,475 sats</td>
                            <td>5,075 sats</td>
                            <td>51 sats</td>
                            <td>5,024 sats</td>
                            <td>🎰 잭팟!</td>
                        </tr>
                    </tbody>
                </table>
            </section>

            <!-- 6. 보안 -->
            <section id="security">
                <h2>6. 보안 및 투명성</h2>

                <h3>6.1 조작 불가능성</h3>
                <div class="mermaid">
                    graph TD
                        A[비트코인 블록 해시] --> B{예측 가능?}
                        B -->|NO| C[SHA-256 해시 함수]
                        C --> D[채굴 전까지 알 수 없음]
                        
                        E[채굴 후] --> F{변경 가능?}
                        F -->|NO| G[블록체인 불변성]
                        G --> H[전 세계 노드 검증]
                        
                        I[봇 운영자] --> J{결과 조작 가능?}
                        J -->|NO| K[공개 알고리즘]
                        K --> L[누구나 재계산 가능]
                        
                        style B fill:#e74c3c,color:#fff
                        style F fill:#e74c3c,color:#fff
                        style J fill:#e74c3c,color:#fff
                        style D fill:#27ae60,color:#fff
                        style H fill:#27ae60,color:#fff
                        style L fill:#27ae60,color:#fff
                </div>

                <h3>6.2 검증 프로세스</h3>
                <pre><code># 1. 블록 해시 조회
curl https://mempool.space/api/block-height/926610

# 2. Python으로 당첨 번호 계산
python3
>>> import random
>>> hash = "00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054"
>>> random.seed(int(hash, 16))
>>> random.randint(1, 2100)
1337  # 당첨 번호

# 3. 봇 명령어로 자동 검증
/verify 926610</code></pre>

                <h3>6.3 보안 계층</h3>
                <div class="mermaid">
                    graph TB
                        subgraph Layer1[Application Layer]
                            A[Discord Bot]
                            B[Rate Limiting]
                            C[Input Validation]
                        end
                        
                        subgraph Layer2[Data Layer]
                            D[SQLite Encryption]
                            E[Daily Backup]
                            F[Cloud Sync]
                        end
                        
                        subgraph Layer3[Payment Layer]
                            G[Hot Wallet - Minimum Balance]
                            H[Cold Wallet - Main Funds]
                            I[Multi-sig]
                        end
                        
                        subgraph Layer4[Infrastructure Layer]
                            J[2FA Authentication]
                            K[Firewall]
                            L[Auto Restart]
                        end
                        
                        A --> D
                        D --> G
                        G --> J
                        
                        style Layer1 fill:#e3f2fd
                        style Layer2 fill:#f3e5f5
                        style Layer3 fill:#e8f5e9
                        style Layer4 fill:#fff3e0
                </div>
            </section>

            <!-- 7. 사용자 기능 -->
            <section id="features">
                <h2>7. 사용자 기능</h2>

                <h3>7.1 명령어 맵</h3>
                <div class="mermaid">
                    mindmap
                      root((LEMON LOTTO<br/>Commands))
                        Purchase
                          /buy [수량]
                          /my
                        Claim
                          /claim
                          /withdraw
                          /withdraw_addr
                        Info
                          /info
                          /verify
                          /stats
                          /rank
                        Support
                          /donate
                          /donate_info
                        DAO
                          /vote_withdraw
                </div>

                <h3>7.2 사용자 여정</h3>
                <div class="mermaid">
                    journey
                        title LEMON LOTTO 사용자 경험
                        section 티켓 구매
                          명령어 입력: 5: User
                          결제 요청 확인: 4: User
                          Lightning 결제: 5: User
                          번호 배정 확인: 5: User
                        section 추첨 대기
                          회차 정보 확인: 3: User
                          상금풀 확인: 4: User
                          추첨 알림 대기: 3: User
                        section 당첨 후
                          당첨 알림 수신: 5: User
                          당첨금 수령: 5: User
                          출금 요청: 4: User
                          Lightning 수령: 5: User
                </div>
            </section>

            <!-- 8. 거버넌스 -->
            <section id="dao">
                <h2>8. 거버넌스 (DAO)</h2>

                <h3>8.1 비상 출금 시스템</h3>
                <div class="mermaid">
                    stateDiagram-v2
                        [*] --> Proposal: 제안 생성
                        Proposal --> Voting: 투표 시작
                        Voting --> Counting: 투표 종료
                        
                        Counting --> Passed: 찬성 51% 이상 & 최소 3표
                        Counting --> Rejected: 조건 미달
                        
                        Passed --> Execution: 자동 실행
                        Rejected --> [*]: 제안 종료
                        Execution --> [*]: 송금 완료
                        
                        note right of Voting
                            24시간 투표 기간
                            ✅ 찬성
                            ❌ 반대
                        end note
                        
                        note right of Passed
                            조건:
                            1. 최소 3표
                            2. 찬성 51% 이상
                        end note
                </div>

                <h3>8.2 향후 DAO 기능</h3>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h4><span class="emoji">💰</span>수수료율 조정</h4>
                        <p>커뮤니티 투표로 수수료율 결정</p>
                    </div>
                    <div class="feature-card">
                        <h4><span class="emoji">🎮</span>게임 규칙 변경</h4>
                        <p>추첨 방식, 당첨 조건 개선</p>
                    </div>
                    <div class="feature-card">
                        <h4><span class="emoji">✨</span>신규 기능 추가</h4>
                        <p>새로운 게임 모드 제안</p>
                    </div>
                    <div class="feature-card">
                        <h4><span class="emoji">📊</span>수익 배분</h4>
                        <p>수익금 사용처 결정</p>
                    </div>
                </div>
            </section>

            <!-- 9. 로드맵 -->
            <section id="roadmap">
                <h2>10. 로드맵</h2>

                <div class="mermaid">
                    timeline
                        title LEMON LOTTO 개발 로드맵
                        section Phase 1 - MVP
                            2024 Q4 : 기본 티켓 구매/추첨
                                   : Provably Fair 구현
                                   : LN 결제 통합
                                   : 회차별 상금풀 관리
                        section Phase 2 - 고급 기능
                            2025 Q1 : 30일 만료 시스템
                                   : 자동 이월 메커니즘
                                   : DAO 비상 출금
                                   : 통계/랭킹 시스템
                        section Phase 3 - 확장
                            2025 Q2 : 다중 번호 선택
                                   : 등급별 당첨
                                   : 웹 대시보드
                                   : 모바일 앱
                        section Phase 4 - 탈중앙화
                            2025 Q3 : 스마트 컨트랙트
                                   : 완전 자동화
                                   : 크로스체인 지원
                                   : LEMON 토큰
                </div>

                <div class="roadmap">
                    <h4>✅ Phase 1: MVP (완료)</h4>
                    <ul>
                        <li>기본 티켓 구매/추첨</li>
                        <li>Provably Fair 구현</li>
                        <li>LN 결제 통합</li>
                        <li>회차별 상금풀 관리</li>
                    </ul>
                </div>

                <div class="roadmap">
                    <h4>✅ Phase 2: 고급 기능 (완료)</h4>
                    <ul>
                        <li>30일 만료 시스템</li>
                        <li>자동 이월 메커니즘</li>
                        <li>DAO 비상 출금</li>
                        <li>통계/랭킹 시스템</li>
                    </ul>
                </div>

                <div class="roadmap">
                    <h4 class="progress">🔄 Phase 3: 확장 (진행 중)</h4>
                    <ul>
                        <li class="progress">다중 번호 선택 (6개 중 3개 맞추기 등)</li>
                        <li class="progress">등급별 당첨 (1등/2등/3등)</li>
                        <li class="pending">웹 대시보드</li>
                        <li class="pending">모바일 앱</li>
                    </ul>
                </div>

                <div class="roadmap">
                    <h4>🔮 Phase 4: 탈중앙화 (계획)</h4>
                    <ul>
                        <li class="pending">스마트 컨트랙트 마이그레이션 (RSK/Stacks)</li>
                        <li class="pending">완전 자동화 (봇 없이 작동)</li>
                        <li class="pending">크로스체인 지원</li>
                        <li class="pending">토큰 경제 (LEMON 토큰)</li>
                    </ul>
                </div>
            </section>

            <!-- 결론 -->
            <section>
                <div class="highlight">
                    <h2 style="color: white; border: none; padding: 0;">🎯 결론</h2>
                    <p style="font-size: 1.2em; margin-top: 20px;">
                        <strong>LEMON LOTTO</strong>는 단순한 로또 게임이 아닙니다.
                    </p>
                    <p style="font-size: 1.1em;">
                        이것은:
                    </p>
                    <ul style="font-size: 1.1em; margin-top: 15px;">
                        <li>🔓 <strong>투명성의 증명</strong></li>
                        <li>⚡ <strong>비트코인 기술의 실용적 활용</strong></li>
                        <li>🤝 <strong>커뮤니티 주도 거버넌스</strong></li>
                        <li>🌍 <strong>누구나 검증 가능한 공정성</strong></li>
                    </ul>
                    <p style="font-size: 1.3em; margin-top: 30px; font-style: italic;">
                        비트코인의 철학을 게임에 담았습니다.
                    </p>
                    <p style="font-size: 1.5em; margin-top: 20px; font-weight: bold;">
                        "Don't trust, verify."
                    </p>
                    <p style="font-size: 1.1em; margin-top: 10px;">
                        — 신뢰하지 말고, 검증하라.
                    </p>
                </div>
            </section>
        </main>

        <footer>
            <h3>🍋 LEMON LOTTO Project</h3>
            <p style="margin: 25px 0; font-size: 1.1em;">
                <strong>GitHub:</strong> <a href="https://github.com/zzeongzi/lemon-lotto">github.com/zzeongzi/lemon-lotto</a>
            </p>
            <p style="font-size: 1.05em;">
                <strong>문의:</strong> <a href="https://github.com/zzeongzi/lemon-lotto/issues">GitHub Issues</a> 또는 Discord DM
            </p>
            <p style="font-size: 1.05em; margin-top: 15px;">
                <strong>기여:</strong> Pull Request 환영합니다!
            </p>
            <p style="margin-top: 40px; opacity: 0.8; font-size: 1em;">
                <strong>License:</strong> MIT License - 자유롭게 사용, 수정, 배포 가능
            </p>
            <p style="margin-top: 30px; font-size: 0.95em; opacity: 0.7;">
                Version: 1.0.0 | Last Updated: 2025-01-06 | LEMON Development Team
            </p>
        </footer>
    </div>

    <script>
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            themeVariables: {
                primaryColor: '#ffd89b',
                primaryTextColor: '#2c3e50',
                primaryBorderColor: '#19547b',
                lineColor: '#34495e',
                secondaryColor: '#19547b',
                tertiaryColor: '#ecf0f1'
            },
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            },
            sequence: {
                useMaxWidth: true,
                wrap: true
            },
            gantt: {
                useMaxWidth: true
            }
        });
    </script>
</body>
</html>
