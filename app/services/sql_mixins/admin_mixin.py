from typing import Dict, Optional
from app.services.db_interface import DBInterface, logger


class AdminMixin:
    # 管理员鉴权
    def get_admin_user(self: DBInterface, username: str) -> Optional[dict]:
        """供登录接口验证账号密码使用"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_name, hashed_password FROM admin_users WHERE user_name = ?",
                (username,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # 系统设置
    def get_system_setting(
        self: DBInterface, setting_key: str, default_value: str = None
    ) -> Optional[str]:
        """获取系统配置（如大模型Key、系统提示词、爬虫周期）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT setting_value FROM system_settings WHERE setting_key = ?",
                (setting_key,),
            )
            row = cursor.fetchone()
            return row["setting_value"] if row else default_value

    def get_all_settings(self: DBInterface) -> Dict[str, str]:
        """获取所有配置，供后台面板一次性展示"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_key, setting_value FROM system_settings")
            rows = cursor.fetchall()
            return {row["setting_key"]: row["setting_value"] for row in rows}

    def update_system_setting(self: DBInterface, setting_key: str, setting_value: str):
        """
        更新或插入系统配置。
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO system_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value
                """,
                (setting_key, setting_value),
            )
            conn.commit()
            logger.info(f"系统配置已更新: {setting_key}")

    # dashboard
    def get_dashboard_stats(self: DBInterface) -> dict:
        """获取首页概览数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM notices")
            total_notices = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM api_keys WHERE is_active = 1")
            active_keys = cursor.fetchone()["count"]

            return {
                "total_notices": total_notices,
                "active_api_keys": active_keys,
            }
