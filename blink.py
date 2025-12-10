import aiohttp
import os
from dotenv import load_dotenv
import bolt11
from typing import Optional, Dict, Any

load_dotenv()

BLINK_API_URL = os.getenv("BLINK_API_URL", "https://api.blink.sv/graphql")
BLINK_API_KEY = os.getenv("BLINK_API_KEY")
BLINK_WALLET_ID = os.getenv("BLINK_WALLET_ID")

async def blink_request(query: str, variables: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Blink GraphQL API 요청"""
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": BLINK_API_KEY
    }
    
    payload: Dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(BLINK_API_URL, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "errors" in data:
                        print(f"[ERROR] GraphQL errors: {data['errors']}")
                        return None
                    return data.get("data")
                else:
                    text = await resp.text()
                    print(f"[ERROR] HTTP {resp.status}: {text}")
                    return None
        except Exception as e:
            print(f"[ERROR] Blink request failed: {e}")
            return None

async def get_wallet_balance() -> int:
    """지갑 잔액 조회"""
    query = """
    query walletBalance($walletId: WalletId!) {
      me {
        defaultAccount {
          walletById(walletId: $walletId) {
            balance
          }
        }
      }
    }
    """
    variables = {"walletId": BLINK_WALLET_ID}
    
    result = await blink_request(query, variables)
    if result:
        balance = result.get("me", {}).get("defaultAccount", {}).get("walletById", {}).get("balance", 0)
        return balance
    return 0

async def create_invoice(amount: int, memo: str = "", invoice_type: str = "lotto") -> Optional[Dict[str, Any]]:
    """
    인보이스 생성
    
    Args:
        amount: 금액 (sats)
        memo: 메모
        invoice_type: 타입 (lotto/donate) - DB 저장용, API에는 전송 안 함
    
    Returns:
        dict: {payment_hash, payment_request, amount}
    """
    query = """
    mutation lnInvoiceCreate($input: LnInvoiceCreateInput!) {
      lnInvoiceCreate(input: $input) {
        invoice {
          paymentHash
          paymentRequest
          satoshis
        }
        errors {
          message
        }
      }
    }
    """
    
    variables = {
        "input": {
            "walletId": BLINK_WALLET_ID,
            "amount": amount,
            "memo": memo
        }
    }
    
    print(f"[DEBUG] Creating invoice: amount={amount}, memo={memo}, type={invoice_type}")
    result = await blink_request(query, variables)
    
    if result:
        invoice_data = result.get("lnInvoiceCreate", {})
        
        if invoice_data.get("errors"):
            print(f"[ERROR] Create invoice failed: {invoice_data['errors']}")
            return None
        
        invoice = invoice_data.get("invoice")
        if invoice:
            return {
                "payment_hash": invoice["paymentHash"],
                "payment_request": invoice["paymentRequest"],
                "amount": invoice["satoshis"]
            }
    
    print(f"[ERROR] Create invoice failed: No data returned")
    return None

async def create_donate_invoice(amount: int, memo: str = "") -> Optional[Dict[str, Any]]:
    """기부 인보이스 생성 (create_invoice와 동일, 타입만 다름)"""
    return await create_invoice(amount, memo, invoice_type="donate")

async def check_payment(payment_hash: str) -> bool:
    """결제 확인 - DB에서 payment_request 가져와서 확인"""
    from database import Database
    db = Database()
    
    # 1. DB에서 인보이스 조회
    invoice_data = db.get_invoice(payment_hash)
    
    if not invoice_data:
        print(f"[ERROR] Invoice not found in DB: {payment_hash[:16]}...")
        return False
    
    # 2. payment_request 추출
    payment_request = invoice_data.get('payment_request')
    if not payment_request:
        print(f"[ERROR] No payment_request in DB for: {payment_hash[:16]}...")
        return False
    
    # 3. Blink API로 확인 (paymentRequest 사용)
    query = """
    query lnInvoicePaymentStatus($input: LnInvoicePaymentStatusInput!) {
      lnInvoicePaymentStatus(input: $input) {
        status
        errors {
          message
        }
      }
    }
    """
    
    variables = {
        "input": {
            "paymentRequest": payment_request  # ✅ paymentHash 대신 paymentRequest
        }
    }
    
    print(f"[DEBUG] Checking payment with paymentRequest: {payment_request[:50]}...")
    result = await blink_request(query, variables)
    
    if result:
        status_data = result.get("lnInvoicePaymentStatus", {})
        status = status_data.get("status")
        print(f"[DEBUG] Payment status: {status}")
        return status == "PAID"
    
    return False

async def check_donate_payment(payment_hash: str) -> bool:
    """기부 결제 확인 (check_payment와 동일)"""
    return await check_payment(payment_hash)

async def decode_invoice(payment_request: str) -> Optional[Dict[str, Any]]:
    """
    인보이스 디코딩 (bolt11 사용)
    
    Args:
        payment_request: Lightning 인보이스 문자열
    
    Returns:
        dict: {payment_hash, amount, amount_msat} 또는 None
    """
    try:
        # bolt11 라이브러리로 디코딩
        decoded = bolt11.decode(payment_request)
        
        # amount_msat가 None일 수 있음 (금액 미지정 인보이스)
        amount_msat = decoded.amount_msat if decoded.amount_msat else 0
        amount_sats = amount_msat // 1000 if amount_msat > 0 else 0
        
        print(f"[DEBUG] Decoded invoice: hash={decoded.payment_hash[:16]}..., amount={amount_sats} sats")
        
        return {
            "payment_hash": decoded.payment_hash,
            "amount": amount_sats,
            "amount_msat": amount_msat
        }
    except Exception as e:
        print(f"[ERROR] Invoice decode failed: {e}")
        return None

async def pay_invoice(payment_request: str) -> Dict[str, bool]:
    """인보이스 결제"""
    query = """
    mutation lnInvoicePaymentSend($input: LnInvoicePaymentInput!) {
      lnInvoicePaymentSend(input: $input) {
        status
        errors {
          message
        }
      }
    }
    """
    
    variables = {
        "input": {
            "walletId": BLINK_WALLET_ID,
            "paymentRequest": payment_request
        }
    }
    
    result = await blink_request(query, variables)
    
    if result:
        payment_data = result.get("lnInvoicePaymentSend", {})
        status = payment_data.get("status")
        
        if payment_data.get("errors"):
            print(f"[ERROR] Payment failed: {payment_data['errors']}")
            return {"success": False}
        
        return {"success": status == "SUCCESS"}
    
    return {"success": False}

async def pay_address(address: str, amount: int) -> Dict[str, bool]:
    """라이트닝 주소로 결제"""
    query = """
    mutation lnAddressPaymentSend($input: LnAddressPaymentSendInput!) {
      lnAddressPaymentSend(input: $input) {
        status
        errors {
          message
        }
      }
    }
    """
    
    variables = {
        "input": {
            "walletId": BLINK_WALLET_ID,
            "lnAddress": address,
            "amount": amount
        }
    }
    
    result = await blink_request(query, variables)
    
    if result:
        payment_data = result.get("lnAddressPaymentSend", {})
        status = payment_data.get("status")
        
        if payment_data.get("errors"):
            print(f"[ERROR] Address payment failed: {payment_data['errors']}")
            return {"success": False}
        
        return {"success": status == "SUCCESS"}
    
    return {"success": False}

async def get_donate_wallet_balance() -> int:
    """기부 지갑 잔액 (일반 지갑과 동일)"""
    return await get_wallet_balance()
