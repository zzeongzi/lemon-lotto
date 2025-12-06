import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

print("------ [환경변수 진단 시작] ------")

# 1. URL 확인
url = os.getenv('LNBITS_URL')
print(f"1. URL 상태: {url}")
if url and url.endswith('/'):
    print("   ⚠️ 경고: URL 끝에 슬래시(/)가 있습니다. 지워주세요.")

# 2. 키 확인 (보안을 위해 앞 4글자만 출력)
inv_key = os.getenv('LNBITS_INVOICE_KEY')
if inv_key:
    print(f"2. Invoice Key: {inv_key[:4]}... (길이: {len(inv_key)})")
    if " " in inv_key:
        print("   ❌ 에러: 키 안에 공백(띄어쓰기)이 포함되어 있습니다!")
    elif '"' in inv_key or "'" in inv_key:
        print("   ❌ 에러: 키에 따옴표가 포함되어 있습니다!")
    else:
        print("   ✅ 키 형식 양호함.")
else:
    print("   ❌ 에러: Invoice Key를 찾을 수 없습니다. .env 파일을 확인하세요.")

print("--------------------------------")