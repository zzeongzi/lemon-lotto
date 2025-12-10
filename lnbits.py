import aiohttp
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

LNBITS_URL = os.getenv("LNBITS_URL")
LNBITS_KEY = os.getenv("LNBITS_KEY")

# 도네이트 전용 지갑 키
LNBITS_DONATE_KEY = os.getenv("LNBITS_DONATE_KEY")

headers = {
    "X-Api-Key": LNBITS_KEY,
    "Content-Type": "application/json"
}

donate_headers = {
    "X-Api-Key": LNBITS_DONATE_KEY,
    "Content-Type": "application/json"
}

# 타임아웃 설정 (10초로 증가)
TIMEOUT = aiohttp.ClientTimeout(total=10)

async def create_invoice(amount: int, memo: str = "Lotto Ticket"):
    """레몬 지갑 인보이스 생성"""
    url = f"{LNBITS_URL}/api/v1/payments"
    data = {"out": False, "amount": amount, "memo": memo, "expiry": 600, "unit": "sat"}
    
    print(f"[DEBUG] Creating LEMON invoice: {amount} sats")
    
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status == 201:
                    result = await resp.json()
                    print(f"[DEBUG] LEMON invoice created: {result.get('payment_hash', 'N/A')[:16]}...")
                    return result
                else:
                    print(f"[ERROR] LEMON Invoice Create Failed: {resp.status} - {await resp.text()}")
                    return None
        except Exception as e:
            print(f"[ERROR] Connection error (create_invoice): {e}")
            return None

async def create_donate_invoice(amount: int, memo: str = "LEMON Donation"):
    """도네이트 지갑 인보이스 생성"""
    if not LNBITS_DONATE_KEY:
        print("[ERROR] LNBITS_DONATE_KEY not set in .env")
        return None
    
    url = f"{LNBITS_URL}/api/v1/payments"
    data = {"out": False, "amount": amount, "memo": memo, "expiry": 600, "unit": "sat"}
    
    print(f"[DEBUG] Creating DONATE invoice: {amount} sats")
    
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.post(url, headers=donate_headers, json=data) as resp:
                if resp.status == 201:
                    result = await resp.json()
                    print(f"[DEBUG] DONATE invoice created: {result.get('payment_hash', 'N/A')[:16]}...")
                    return result
                else:
                    print(f"[ERROR] DONATE Invoice Create Failed: {resp.status} - {await resp.text()}")
                    return None
        except Exception as e:
            print(f"[ERROR] Connection error (create_donate_invoice): {e}")
            return None

async def check_payment(payment_hash: str):
    """레몬 지갑 결제 확인"""
    url = f"{LNBITS_URL}/api/v1/payments/{payment_hash}"
    
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    is_paid = data.get("paid", False)
                    if is_paid:
                        print(f"[DEBUG] LEMON payment confirmed: {payment_hash[:16]}...")
                    return is_paid
        except Exception as e:
            print(f"[ERROR] Check payment error: {e}")
    return False

async def check_donate_payment(payment_hash: str):
    """도네이트 지갑 결제 확인"""
    if not LNBITS_DONATE_KEY:
        print("[ERROR] LNBITS_DONATE_KEY not set")
        return False
    
    url = f"{LNBITS_URL}/api/v1/payments/{payment_hash}"
    
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.get(url, headers=donate_headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    is_paid = data.get("paid", False)
                    if is_paid:
                        print(f"[DEBUG] DONATE payment confirmed: {payment_hash[:16]}...")
                    return is_paid
        except Exception as e:
            print(f"[ERROR] Check donate payment error: {e}")
    return False

async def decode_invoice(payment_request: str):
    """인보이스 디코딩 (디버깅 강화)"""
    url = f"{LNBITS_URL}/api/v1/payments/decode"
    data = {"data": payment_request}
    
    print(f"[DEBUG] Decoding invoice at: {url}")
    print(f"[DEBUG] Invoice (first 50 chars): {payment_request[:50]}...")
    
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.post(url, headers=headers, json=data) as resp:
                print(f"[DEBUG] Decode response status: {resp.status}")
                
                if resp.status == 200:
                    result = await resp.json()
                    print(f"[DEBUG] Decode response (full): {result}")
                    
                    # 금액 필드 확인
                    amount_msat = result.get("amount_msat", 0)
                    amount = result.get("amount", 0)
                    num_satoshis = result.get("num_satoshis", 0)
                    
                    print(f"[DEBUG] amount_msat: {amount_msat}")
                    print(f"[DEBUG] amount: {amount}")
                    print(f"[DEBUG] num_satoshis: {num_satoshis}")
                    
                    return result
                else:
                    error_text = await resp.text()
                    print(f"[ERROR] Decode failed HTTP {resp.status}")
                    print(f"[ERROR] Response: {error_text}")
                    return None
        except Exception as e:
            print(f"[ERROR] Decode invoice exception: {e}")
            return None
    
    return None

async def pay_invoice(bolt11: str):
    url = f"{LNBITS_URL}/api/v1/payments"
    data = {"out": True, "bolt11": bolt11}
    
    print(f"[DEBUG] Paying invoice: {bolt11[:50]}...")
    
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status == 201:
                    print(f"[DEBUG] Payment sent successfully")
                    return True
                else:
                    error_text = await resp.text()
                    print(f"[ERROR] Pay Failed ({resp.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"[ERROR] Pay invoice exception: {e}")
            return False

async def pay_address(address: str, amount: int):
    """라이트닝 주소로 송금"""
    print(f"[DEBUG] Paying to address: {address} ({amount} sats)")
    
    try:
        user, domain = address.split("@")
        lnurl_endpoint = f"https://{domain}/.well-known/lnurlp/{user}"
        
        print(f"[DEBUG] LNURL endpoint: {lnurl_endpoint}")
        
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            # 1. LNURL 정보 가져오기
            async with session.get(lnurl_endpoint) as resp:
                if resp.status != 200:
                    print(f"[ERROR] LNURL fetch failed: {resp.status}")
                    return False
                data = await resp.json()
                callback = data.get("callback")
                print(f"[DEBUG] Callback URL: {callback}")
            
            # 2. 인보이스 요청
            amount_msat = amount * 1000
            async with session.get(f"{callback}?amount={amount_msat}") as resp:
                if resp.status != 200:
                    print(f"[ERROR] Invoice request failed: {resp.status}")
                    return False
                data = await resp.json()
                bolt11 = data.get("pr")
                print(f"[DEBUG] Got invoice: {bolt11[:50]}...")
            
            # 3. 결제 실행
            return await pay_invoice(bolt11)
            
    except Exception as e:
        print(f"[ERROR] Address Pay Error: {e}")
        return False

async def get_wallet_balance():
    """레몬 지갑 잔액 조회"""
    url = f"{LNBITS_URL}/api/v1/wallet"
    print(f"[DEBUG] Fetching LEMON wallet balance from: {url}")
    
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    balance_msat = data.get("balance", 0)
                    balance_sats = balance_msat // 1000
                    print(f"[DEBUG] LEMON wallet balance: {balance_sats} sats ({balance_msat} msat)")
                    return balance_sats
                else:
                    error_text = await resp.text()
                    print(f"[ERROR] LEMON wallet check failed ({resp.status}): {error_text}")
                    return 0
        except Exception as e:
            print(f"[ERROR] LEMON wallet connection failed: {e}")
            return 0
    
    return 0

async def get_donate_wallet_balance():
    """도네이트 지갑 잔액 조회"""
    if not LNBITS_DONATE_KEY:
        print("[ERROR] LNBITS_DONATE_KEY not set")
        return 0
    
    url = f"{LNBITS_URL}/api/v1/wallet"
    print(f"[DEBUG] Fetching DONATE wallet balance from: {url}")
    
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.get(url, headers=donate_headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    balance_msat = data.get("balance", 0)
                    balance_sats = balance_msat // 1000
                    print(f"[DEBUG] DONATE wallet balance: {balance_sats} sats ({balance_msat} msat)")
                    return balance_sats
                else:
                    error_text = await resp.text()
                    print(f"[ERROR] DONATE wallet check failed ({resp.status}): {error_text}")
                    return 0
        except Exception as e:
            print(f"[ERROR] DONATE wallet connection failed: {e}")
            return 0
    
    return 0
