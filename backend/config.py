"""
配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Flask 配置
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# AI 模型配置
AI_PROVIDER = os.getenv('AI_PROVIDER', 'local')  # local, openai, huggingface
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')

# Redis 配置（可选，用于缓存）
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'False').lower() == 'true'
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# 上传配置
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB

# 创建上传文件夹
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
