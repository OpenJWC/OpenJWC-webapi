from pydantic import BaseModel


class SysinfoData(BaseModel):
    """返回的一堆数据"""

    """CPU使用率"""
    cpu_percent: str
    """服务器总内存"""
    ram_total_mb: str
    """服务占用内存"""
    ram_used_mb: str
    """服务运行时间"""
    uptime_seconds: str


class SubmissionData(BaseModel):
    """资讯提交数据"""

    label: str
    title: str
    date: str
    detail_url: str
    is_page: bool
    content_text: str
    attachments: str
    submitter_id: str
    status: str
    review: str
