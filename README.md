# ひだまり健康チェック管理システム Ver1.3.14

## 修正内容
- PostgreSQLの boolean = integer エラーを修正
- ログイン判定で `is_active = TRUE OR is_active = 1` を使わない
- 健康チェックCRUDをタブ表示
- 利用者登録、健康チェック保存、更新、削除、一覧検索、今日の入力状況

## 初期ログイン
- ID: admin
- PW: admin

## Neon側に古いDBがある場合
SQL Editorで以下を実行してからRebootしてください。

```sql
DROP TABLE IF EXISTS health_records CASCADE;
DROP TABLE IF EXISTS excretion_records CASCADE;
DROP TABLE IF EXISTS handover_records CASCADE;
DROP TABLE IF EXISTS staff_accounts CASCADE;
DROP TABLE IF EXISTS users CASCADE;
```
