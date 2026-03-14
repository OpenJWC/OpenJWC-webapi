# app/core/security.py
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext

# 加密密钥, 决定了密码的安全线，不可泄露
# 应通过环境变量设置
SECRET_KEY = "your-super-secret-key-change-this-in-production"
# 加密算法
ALGORITHM = "HS256"
# JWT 手环的有效期，单位为分钟，默认是 120 分钟
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """核对明文密码和数据库里加密后的密码是否一致"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """将明文密码变成哈希值（用于初始化管理员账号）"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """生成 JWT 认证token"""
    to_encode = data.copy()
    # 设置过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 用 SECRET_KEY 进行签名加密
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
