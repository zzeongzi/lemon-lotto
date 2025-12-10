# ========================================
# /stats 명령어 정확성 검증 스크립트
# ========================================

# 본인 디스코드 ID로 변경
$userId = 759983364111073332

Write-Host "=== 현재 통계 ===" -ForegroundColor Cyan
sqlite3 lotto.db "SELECT user_id, total_spent, total_won, balance, win_count FROM users WHERE user_id = $userId;"

Write-Host "`n=== 실제 결제 총액 ===" -ForegroundColor Cyan
sqlite3 lotto.db "SELECT type, COUNT(*) as count, SUM(amount) as total FROM invoices WHERE user_id = $userId AND status = 'PAID' GROUP BY type;"

Write-Host "`n=== 실제 당첨 기록 ===" -ForegroundColor Cyan
sqlite3 lotto.db "SELECT COUNT(*) as win_count, SUM(amount) as total_won, SUM(CASE WHEN is_claimed = 1 THEN amount ELSE 0 END) as claimed, SUM(CASE WHEN is_claimed = 0 AND is_expired = 0 THEN amount ELSE 0 END) as pending FROM user_wins WHERE user_id = $userId;"

Write-Host "`n=== 당첨 상세 ===" -ForegroundColor Cyan
sqlite3 lotto.db "SELECT block_height, amount, CASE WHEN is_claimed = 1 THEN '✅수령' WHEN is_expired = 1 THEN '❌만료' ELSE '⏳대기' END as status FROM user_wins WHERE user_id = $userId ORDER BY block_height DESC;"

Write-Host "`n=== 불일치 검사 ===" -ForegroundColor Yellow

# total_spent 검사
$result = sqlite3 lotto.db "SELECT u.total_spent, COALESCE(SUM(i.amount), 0) FROM users u LEFT JOIN invoices i ON u.user_id = i.user_id AND i.status = 'PAID' WHERE u.user_id = $userId;" | Out-String
$values = $result.Trim() -split '\|'
$dbSpent = [int]$values[0]
$actualSpent = [int]$values[1]
$diffSpent = $dbSpent - $actualSpent

Write-Host "total_spent: DB=$dbSpent, Actual=$actualSpent, Diff=$diffSpent" -ForegroundColor $(if ($diffSpent -eq 0) { "Green" } else { "Red" })

# total_won 검사
$result = sqlite3 lotto.db "SELECT u.total_won, COALESCE(SUM(w.amount), 0) FROM users u LEFT JOIN user_wins w ON u.user_id = w.user_id WHERE u.user_id = $userId;" | Out-String
$values = $result.Trim() -split '\|'
$dbWon = [int]$values[0]
$actualWon = [int]$values[1]
$diffWon = $dbWon - $actualWon

Write-Host "total_won: DB=$dbWon, Actual=$actualWon, Diff=$diffWon" -ForegroundColor $(if ($diffWon -eq 0) { "Green" } else { "Red" })

# win_count 검사
$result = sqlite3 lotto.db "SELECT u.win_count, COALESCE(COUNT(w.id), 0) FROM users u LEFT JOIN user_wins w ON u.user_id = w.user_id WHERE u.user_id = $userId;" | Out-String
$values = $result.Trim() -split '\|'
$dbCount = [int]$values[0]
$actualCount = [int]$values[1]
$diffCount = $dbCount - $actualCount

Write-Host "win_count: DB=$dbCount, Actual=$actualCount, Diff=$diffCount" -ForegroundColor $(if ($diffCount -eq 0) { "Green" } else { "Red" })

Write-Host "`n=== 검증 완료 ===" -ForegroundColor Green