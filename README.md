# ひだまり健康チェック管理システム Ver1.1 PostgreSQL 新設計版

Ver4.4 SQLite版を原型モデルに、商品化・多施設対応を見据えて最小中核機能から再設計した版です。

## 実装済み

- ログイン
- 初回パスワード変更必須
- 利用者マスタ
- 健康チェック
- 体重任意入力・最新体重表示
- 排泄チェック
- 業務全体申し送り（事実／気づき／次に見ること）
- 監査ログ
- PostgreSQL論理バックアップCSV ZIP
- 分割構造

## Streamlit Cloud Secrets

```
DATABASE_URL="postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"
```

## 初期ログイン

- 管理者: `kanri` / `rui`
- 職員: `staff` / `rui`

初回ログイン後、8文字以上・英字数字入りのパスワード変更が必要です。
