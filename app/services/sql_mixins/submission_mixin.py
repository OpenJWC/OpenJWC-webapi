import sqlite3
from app.services.db_interface import DBInterface
from typing import List, Dict, Any
from app.utils.logging_manager import setup_logger
from app.models.models import SubmissionData

logger = setup_logger("submission_db_logs")

# TODO:
# 对齐数据表字段，submission统一通过SubmissionData数据接口通讯


class SubmissionMixin:
    def create_submission(self: DBInterface, submission: SubmissionData) -> int | None:
        """客户端：提交一条新资讯"""
        sql = """
            INSERT INTO submissions (label, title, date, detail_url, is_page,  content_text, attachments, submitter_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    submission.label,
                    submission.title,
                    submission.date,
                    submission.detail_url,
                    submission.is_page,
                    submission.content_text,
                    submission.attachments,
                    submission.submitter_id,
                ),
            )
            conn.commit()
            logger.info(f"收到新资讯提交, ID: {cursor.lastrowid}")
            return cursor.lastrowid

    def get_submissions_by_status(
        self: DBInterface, status: str = "pending"
    ) -> List[Dict[str, Any]]:
        """WebUI管理端：获取某状态的提交列表"""
        sql = "SELECT * FROM submissions WHERE status = ? ORDER BY created_at DESC"
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (status,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_submission_status(
        self: DBInterface, sub_id: int, status: str, reject_reason: str = ""
    ) -> bool:
        """WebUI管理端：更新审核状态"""
        sql = """
            UPDATE submissions 
            SET status = ?, reject_reason = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (status, reject_reason, sub_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_submission_by_id(self: DBInterface, sub_id: int) -> Dict[str, Any] | None:
        """获取单个提交的详细信息"""
        sql = "SELECT * FROM submissions WHERE id = ?"
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (sub_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
