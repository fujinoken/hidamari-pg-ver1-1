# Ver1.3.1 DB定義統一版

差し替え対象:

- config/settings.py
- db/schema.py
- db/migrations.py
- services/auth_service.py

方針:

- facility_id = TEXT
- users.id = TEXT
- login_id = TEXT
- user_name は互換用任意列

推奨:
Neon DBは一度リセットし、この4ファイルを差し替えた状態で起動してください。
