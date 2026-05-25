# ひだまり健康チェック管理システム PostgreSQL版 Ver1.3

Ver4.4 SQLite版を原型設計図として、新設計したPostgreSQL版です。

## Ver1.3 追加内容
- 更新競合対策（updated_at比較）
- 監査ログ強化
- 権限チェック
- 多施設対応の土台（facility_id）
- CSV出力
- PostgreSQL論理バックアップ
- 検索高速化用インデックス
- 健康記録・排泄記録・申し送りの検索・更新・削除

## Streamlit Secrets

```toml
DATABASE_URL="postgresql://..."
```

## 初期ログイン

- 管理者: kanri / rui
- 職員: staff / rui

初回ログイン後、パスワード変更が必要です。
