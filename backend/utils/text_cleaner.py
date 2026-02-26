"""
文本清洗和处理工具
"""
import re
import jieba

def clean_text(text):
    """
    清洗简历文本
    """
    if not text:
        return ""
    
    # 移除特殊字符但保留中英文、数字和基本标点
    text = re.sub(r'[^\w\s\u4e00-\u9fa5\-+()（）@.#+._]', '', text)
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text)
    
    # 移除换行符前后的空格
    text = re.sub(r'\s*\n\s*', '\n', text)
    
    return text.strip()


def extract_segments(text, min_length=20):
    """
    将文本分段
    """
    lines = text.split('\n')
    segments = [line.strip() for line in lines if len(line.strip()) >= min_length]
    return segments


def extract_keywords(text, top_n=10):
    """
    提取关键词
    """
    try:
        # 使用 jieba 进行中文分词
        words = jieba.cut(text)
        word_list = [w for w in words if len(w) > 1]
        
        # 简单统计频率
        from collections import Counter
        word_freq = Counter(word_list)
        
        # 返回频率最高的 top_n 个词
        keywords = [word for word, freq in word_freq.most_common(top_n)]
        return keywords
    except Exception as e:
        print(f"提取关键词错误: {e}")
        return []


def normalize_phone(phone):
    """
    规范化电话号码
    """
    # 移除所有非数字字符
    phone = re.sub(r'\D', '', phone)
    return phone


def normalize_email(email):
    """
    规范化邮箱
    """
    email = email.strip().lower()
    return email


def extract_numbers(text):
    """
    从文本中提取所有数字
    """
    return re.findall(r'\d+', text)


def is_valid_email(email):
    """
    检查电子邮件格式
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    """
    检查电话号码格式
    """
    # 中国手机号码和固话
    patterns = [
        r'^1[3-9]\d{9}$',  # 手机
        r'^0\d{2,3}\d{7,8}$',  # 固话
    ]
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    return False
