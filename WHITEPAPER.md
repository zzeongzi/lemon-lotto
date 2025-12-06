
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍋 LEMON - Provably Fair Lightning Lottery Whitepaper</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }

        header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }

        header .meta {
            margin-top: 20px;
            font-size: 0.9em;
            opacity: 0.8;
        }

        nav {
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 2px solid #e9ecef;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        nav ul {
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }

        nav a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s;
        }

        nav a:hover {
            color: #764ba2;
        }

        main {
            padding: 40px;
        }

        section {
            margin-bottom: 60px;
        }

        h2 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }

        h3 {
            color: #764ba2;
            font-size: 1.8em;
            margin: 30px 0 15px 0;
        }

        h4 {
            color: #555;
            font-size: 1.3em;
            margin: 20px 0 10px 0;
        }

        p {
            margin-bottom: 15px;
            text-align: justify;
        }

        ul, ol {
            margin-left: 30px;
            margin-bottom: 15px;
        }

        li {
            margin-bottom: 8px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        th, td {
            padding: 15px;
            text-align: left;
            border: 1px solid #ddd;
        }

        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
        }

        tr:nth-child(even) {
            background: #f8f9fa;
        }

        .mermaid {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        pre {
            background: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        code {
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .feature-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }

        .feature-card:hover {
            transform: translateY(-5px);
        }

        .feature-card h4 {
            color: white;
            margin-bottom: 10px;
        }

        .roadmap {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
        }

        .roadmap h4 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .roadmap ul {
            list-style: none;
            margin-left: 0;
        }

        .roadmap li {
            padding: 8px 0;
            padding-left: 30px;
            position: relative;
        }

        .roadmap li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #2ecc71;
            font-weight: bold;
        }

        .roadmap li.pending:before {
            content: "○";
            color: #95a5a6;
        }

        footer {
            background: #282c34;
            color: white;
            padding: 40px;
            text-align: center;
        }

        footer a {
            color: #667eea;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        .highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .emoji {
            font-size: 1.5em;
            margin-right: 10px;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 2em;
            }

            main {
                padding: 20px;
            }

            nav ul {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍋 LEMON</h1>
            <div class="subtitle">Provably Fair Lightning Lottery</div>
            <div class="meta">
                <strong>Version:</strong> 1.0 | 
                <strong>Date:</strong> 2024-12-06 | 
                <strong>Author:</strong> zzeongzi
            </div>
        </header>

        <nav>
            <ul>
                <li><a href="#overview">개요</a></li>
                <li><a href="#problem">문제 정의</a></li>
                <li><a href="#architecture">시스템 아키텍처</a></li>
                <li><a href="#algorithm">Provably Fair</a></li>
                <li><a href="#lightning">Lightning Network</a></li>
                <li><a href="#security">보안</a></li>
                <li><a href="#roadmap">로드맵</a></li>
            </ul>
        </nav>

        <main>
            <!-- 1. 개요 -->
            <section id="overview">
                <h2>1. 개요</h2>
                <p>
                    LEMON은 Discord 플랫폼에서 작동하는 <strong>검증 가능하게 공정한(Provably Fair)</strong> 
                    비트코인 라이트닝 복권 시스템입니다.
                </p>

                <h3>1.1 핵심 가치</h3>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h4><span class="emoji">🔍</span>투명성</h4>
                        <p>모든 추첨 과정이 암호학적으로 검증 가능</p>
                    </div>
                    <div class="feature-card">
                        <h4><span class="emoji">⚡</span>즉시성</h4>
                        <p>Lightning Network를 통한 실시간 결제</p>
                    </div>
                    <div class="feature-card">
                        <h4><span class="emoji">🎯</span>접근성</h4>
                        <p>Discord를 통한 쉬운 사용자 경험</p>
                    </div>
                    <div class="feature-card">
                        <h4><span class="emoji">⚖️</span>공정성</h4>
                        <p>조작 불가능한 난수 생성</p>
                    </div>
                </div>

                <h3>1.2 주요 기능</h3>
                <ul>
                    <li>⚡ Lightning Network 기반 즉시 결제</li>
                    <li>🎲 Bitcoin 블록 해시 기반 난수 생성</li>
                    <li>🔍 모든 추첨 결과 검증 가능</li>
                    <li>🤖 Discord 슬래시 커맨드 지원</li>
                    <li>📊 실시간 통계 및 히스토리</li>
                </ul>
            </section>

            <!-- 2. 문제 정의 -->
            <section id="problem">
                <h2>2. 문제 정의</h2>
                
                <h3>2.1 기존 온라인 복권의 문제점</h3>
                <table>
                    <thead>
                        <tr>
                            <th>문제</th>
                            <th>설명</th>
                            <th>LEMON 해결책</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>불투명성</strong></td>
                            <td>추첨 과정이 블랙박스</td>
                            <td>모든 과정 공개 및 검증 가능</td>
                        </tr>
                        <tr>
                            <td><strong>느린 정산</strong></td>
                            <td>당첨금 지급까지 수일 소요</td>
                            <td>Lightning으로 즉시 지급</td>
                        </tr>
                        <tr>
                            <td><strong>높은 수수료</strong></td>
                            <td>중개자 수수료 과다</td>
                            <td>P2P 직접 거래</td>
                        </tr>
                        <tr>
                            <td><strong>신뢰 문제</strong></td>
                            <td>운영자 조작 가능성</td>
                            <td>암호학적 검증으로 조작 불가능</td>
                        </tr>
                    </tbody>
                </table>

                <h3>2.2 해결 방안</h3>
                <div class="mermaid">
                    graph LR
                        A[기존 복권] -->|문제| B[중앙화된 신뢰]
                        A -->|문제| C[느린 정산]
                        A -->|문제| D[높은 수수료]
                        
                        E[LEMON] -->|해결| F[암호학적 검증]
                        E -->|해결| G[Lightning 즉시 정산]
                        E -->|해결| H[최소 수수료]
                        
                        style A fill:#e74c3c,color:#fff
                        style E fill:#2ecc71,color:#fff
                </div>
            </section>

            <!-- 3. 시스템 아키텍처 -->
            <section id="architecture">
                <h2>3. 시스템 아키텍처</h2>

                <h3>3.1 전체 구조</h3>
                <div class="mermaid">
                    graph TD
                        A[Discord Bot<br/>유저 인터페이스] --> B[Database<br/>SQLite]
                        A --> C[LNbits<br/>Lightning Network]
                        B --> D[Bitcoin Mempool<br/>블록 데이터]
                        C --> D
                        
                        style A fill:#5865F2,stroke:#fff,color:#fff
                        style B fill:#2ecc71,stroke:#fff,color:#fff
                        style C fill:#f39c12,stroke:#fff,color:#fff
                        style D fill:#e74c3c,stroke:#fff,color:#fff
                </div>

                <h3>3.2 데이터 흐름</h3>
                <div class="mermaid">
                    sequenceDiagram
                        participant User as 👤 사용자
                        participant Bot as 🤖 Discord Bot
                        participant DB as 💾 Database
                        participant LN as ⚡ LNbits
                        participant BTC as ₿ Bitcoin

                        User->>Bot: /lotto join
                        Bot->>LN: 인보이스 생성
                        LN-->>Bot: Lightning Invoice
                        Bot-->>User: 결제 요청 (QR)
                        User->>LN: ⚡ 결제 완료
                        LN->>Bot: 결제 확인 웹훅
                        Bot->>DB: 참가자 저장
                        Bot-->>User: ✅ 참가 완료
                        
                        Note over Bot,BTC: ⏰ 추첨 시간
                        
                        Bot->>BTC: 최신 블록 해시 요청
                        BTC-->>Bot: Block Hash
                        Bot->>DB: 참가자 목록 조회
                        Bot->>Bot: 🎲 당첨자 계산
                        Bot->>LN: 💰 상금 전송
                        Bot->>DB: 📝 결과 저장
                        Bot-->>User: 🎉 당첨 알림
                </div>

                <h3>3.3 컴포넌트 상세</h3>
                
                <h4>Discord Bot Layer</h4>
                <ul>
                    <li>슬래시 커맨드 처리</li>
                    <li>이벤트 리스너</li>
                    <li>사용자 인증</li>
                    <li>메시지 포맷팅</li>
                </ul>

                <h4>Database Layer</h4>
                <pre><code>-- 주요 테이블
lotteries      -- 복권 정보
participants   -- 참가자
transactions   -- 거래 내역
draws          -- 추첨 결과</code></pre>

                <h4>Lightning Layer</h4>
                <pre><code>LNbits API:
- POST /api/v1/payments  -- 인보이스 생성
- GET /api/v1/payments   -- 결제 확인
- POST /api/v1/payments  -- 송금</code></pre>
            </section>

            <!-- 4. Provably Fair 알고리즘 -->
            <section id="algorithm">
                <h2>4. Provably Fair 알고리즘</h2>

                <h3>4.1 난수 생성 프로세스</h3>
                <div class="mermaid">
                    graph LR
                        A[Server Seed] --> D[SHA256]
                        B[Client Seeds] --> D
                        C[Block Hash] --> D
                        D --> E[Final Hash]
                        E --> F[Winner Index]
                        
                        style D fill:#3498db,color:#fff
                        style E fill:#e74c3c,color:#fff
                        style F fill:#2ecc71,color:#fff
                </div>

                <h3>4.2 알고리즘 상세</h3>
                <pre><code>def select_winner(server_seed, client_seeds, block_hash, participants):
    """
    Provably Fair 당첨자 선정
    
    Args:
        server_seed: 서버가 생성한 시드 (사전 공개)
        client_seeds: 참가자들의 시드
        block_hash: Bitcoin 블록 해시
        participants: 참가자 목록
    
    Returns:
        winner: 당첨자
        proof: 검증 데이터
    """
    # 1. 모든 시드 결합
    combined = server_seed + ''.join(client_seeds) + block_hash
    
    # 2. SHA256 해싱
    final_hash = hashlib.sha256(combined.encode()).hexdigest()
    
    # 3. 정수 변환
    random_number = int(final_hash, 16)
    
    # 4. 당첨자 인덱스 계산
    winner_index = random_number % len(participants)
    
    # 5. 검증 데이터 생성
    proof = {
        'server_seed': server_seed,
        'client_seeds': client_seeds,
        'block_hash': block_hash,
        'final_hash': final_hash,
        'winner_index': winner_index
    }
    
    return participants[winner_index], proof</code></pre>

                <h3>4.3 검증 프로세스</h3>
                <div class="highlight">
                    <h4>사용자는 언제든지 결과를 검증할 수 있습니다</h4>
                    <pre style="background: rgba(0,0,0,0.2); margin-top: 15px;"><code>명령어: /lotto verify &lt;draw_id&gt;

출력 예시:
✅ 검증 완료!

Server Seed: abc123...
Client Seeds: [def456..., ghi789...]
Block Hash: 00000000000000000007...
Final Hash: 8f3a2b1c...

계산된 당첨자 인덱스: 42
실제 당첨자 인덱스: 42

✅ 결과가 일치합니다!</code></pre>
                </div>
            </section>

            <!-- 5. Lightning Network 통합 -->
            <section id="lightning">
                <h2>5. Lightning Network 통합</h2>

                <h3>5.1 LNbits 연동</h3>
                <pre><code>class LightningService:
    def __init__(self, lnbits_url, api_key):
        self.url = lnbits_url
        self.headers = {'X-Api-Key': api_key}
    
    async def create_invoice(self, amount_sats, memo):
        """Lightning 인보이스 생성"""
        data = {
            'out': False,
            'amount': amount_sats,
            'memo': memo
        }
        response = await self.post('/api/v1/payments', data)
        return response['payment_request']
    
    async def pay_invoice(self, payment_request):
        """Lightning 결제 실행"""
        data = {'out': True, 'bolt11': payment_request}
        return await self.post('/api/v1/payments', data)</code></pre>

                <h3>5.2 결제 흐름</h3>
                <div class="mermaid">
                    stateDiagram-v2
                        [*] --> InvoiceCreated: 인보이스 생성
                        InvoiceCreated --> Pending: QR 코드 표시
                        Pending --> Paid: 사용자 결제
                        Pending --> Expired: 10분 경과
                        Paid --> Confirmed: 블록체인 확인
                        Confirmed --> [*]: 참가 완료
                        Expired --> [*]: 취소
                </div>
            </section>

            <!-- 6. 보안 고려사항 -->
            <section id="security">
                <h2>6. 보안 고려사항</h2>

                <h3>6.1 위협 모델</h3>
                <table>
                    <thead>
                        <tr>
                            <th>위협</th>
                            <th>대응 방안</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>서버 시드 조작</strong></td>
                            <td>추첨 전 SHA256 해시 공개</td>
                        </tr>
                        <tr>
                            <td><strong>참가자 시드 조작</strong></td>
                            <td>Discord User ID 기반 자동 생성</td>
                        </tr>
                        <tr>
                            <td><strong>블록 해시 조작</strong></td>
                            <td>공개 Mempool API 사용</td>
                        </tr>
                        <tr>
                            <td><strong>결제 위조</strong></td>
                            <td>LNbits 웹훅 서명 검증</td>
                        </tr>
                        <tr>
                            <td><strong>데이터베이스 변조</strong></td>
                            <td>모든 기록 해시 체인으로 보호</td>
                        </tr>
                    </tbody>
                </table>

                <h3>6.2 보안 체크리스트</h3>
                <ul>
                    <li>✅ 환경 변수로 민감 정보 관리</li>
                    <li>✅ HTTPS/WSS 암호화 통신</li>
                    <li>✅ Rate limiting 구현</li>
                    <li>✅ SQL Injection 방지</li>
                    <li>✅ XSS 방지 (Discord Embed)</li>
                    <li>⏳ 2FA 인증 (향후)</li>
                    <li>⏳ 감사 로그 (향후)</li>
                </ul>
            </section>

            <!-- 7. 로드맵 -->
            <section id="roadmap">
                <h2>7. 로드맵</h2>

                <div class="roadmap">
                    <h4>Phase 1: MVP (현재)</h4>
                    <ul>
                        <li>Discord 봇 기본 구조</li>
                        <li>슬래시 커맨드</li>
                        <li class="pending">SQLite 데이터베이스</li>
                        <li class="pending">기본 복권 로직</li>
                    </ul>
                </div>

                <div class="roadmap">
                    <h4>Phase 2: Lightning 통합</h4>
                    <ul>
                        <li class="pending">LNbits API 연동</li>
                        <li class="pending">인보이스 생성/결제</li>
                        <li class="pending">자동 정산 시스템</li>
                        <li class="pending">웹훅 처리</li>
                    </ul>
                </div>

                <div class="roadmap">
                    <h4>Phase 3: Provably Fair</h4>
                    <ul>
                        <li class="pending">Bitcoin Mempool API 연동</li>
                        <li class="pending">난수 생성 알고리즘</li>
                        <li class="pending">검증 시스템</li>
                        <li class="pending">투명성 대시보드</li>
                    </ul>
                </div>

                <div class="roadmap">
                    <h4>Phase 4: 고급 기능</h4>
                    <ul>
                        <li class="pending">다중 복권 동시 진행</li>
                        <li class="pending">커스텀 복권 생성</li>
                        <li class="pending">통계 및 분석</li>
                        <li class="pending">모바일 웹 인터페이스</li>
                    </ul>
                </div>

                <div class="roadmap">
                    <h4>Phase 5: 확장</h4>
                    <ul>
                        <li class="pending">다른 Discord 서버 지원</li>
                        <li class="pending">API 공개</li>
                        <li class="pending">플러그인 시스템</li>
                        <li class="pending">다국어 지원</li>
                    </ul>
                </div>
            </section>

            <!-- 8. 참고 자료 -->
            <section>
                <h2>8. 참고 자료</h2>
                <ul>
                    <li><a href="https://bitcoin.org/bitcoin.pdf" target="_blank">Bitcoin Whitepaper</a></li>
                    <li><a href="https://lightning.network/lightning-network-paper.pdf" target="_blank">Lightning Network</a></li>
                    <li><a href="https://en.wikipedia.org/wiki/Provably_fair_algorithm" target="_blank">Provably Fair Algorithm</a></li>
                    <li><a href="https://discord.com/developers/docs" target="_blank">Discord Developer Docs</a></li>
                    <li><a href="https://github.com/lnbits/lnbits" target="_blank">LNbits Documentation</a></li>
                </ul>
            </section>
        </main>

        <footer>
            <h3>🍋 LEMON Project</h3>
            <p style="margin: 20px 0;">
                <strong>문의:</strong> <a href="https://github.com/zzeongzi/lemon-lotto/issues">GitHub Issues</a> 또는 Discord DM
            </p>
            <p>
                <strong>기여:</strong> Pull Request 환영합니다!
            </p>
            <p style="margin-top: 30px; opacity: 0.7;">
                MIT License - 자유롭게 사용, 수정, 배포 가능
            </p>
            <p style="margin-top: 20px; font-style: italic;">
                "Trust, but verify." - Bitcoin Community
            </p>
        </footer>
    </div>

    <script>
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }
        });
    </script>
</body>
</html>
EOF

echo "✅ whitepaper.html 생성 완료!"
echo ""
echo "📂 파일 위치: /home/umbrel/discord-LEMON/whitepaper.html"
echo ""
echo "🌐 브라우저에서 열기:"
echo "   file:///home/umbrel/discord-LEMON/whitepaper.html"
echo ""
echo "또는 웹 서버로 실행:"
echo "   cd /home/umbrel/discord-LEMON"
echo "   python3 -m http.server 8080"
echo "   그 다음 브라우저에서: http://localhost:8080/whitepaper.html"
