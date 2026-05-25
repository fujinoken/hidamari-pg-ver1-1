import os

APP_NAME = "ひだまり健康チェック管理システム"
APP_VERSION = "Ver1.3.13 精査・安定版"

DEFAULT_ADMIN_LOGIN_ID = os.getenv("DEFAULT_ADMIN_LOGIN_ID", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")
DEFAULT_FACILITY_ID = os.getenv("DEFAULT_FACILITY_ID", "default")
DEFAULT_FACILITY_NAME = os.getenv("DEFAULT_FACILITY_NAME", "ひだまり")
