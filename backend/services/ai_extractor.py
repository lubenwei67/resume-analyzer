"""
AI 关键信息提取模块
"""
import re
from utils.text_cleaner import (
    is_valid_email, is_valid_phone, normalize_phone, 
    normalize_email, extract_keywords, clean_text
)


class AIExtractor:
    """AI 信息提取器"""
    
    @staticmethod
    def extract_base_info(resume_text):
        """
        提取基本信息：姓名、电话、邮箱、地址
        """
        base_info = {
            'name': None,
            'phone': None,
            'email': None,
            'address': None
        }
        
        lines = resume_text.split('\n')
        text_for_search = resume_text
        
        # 提取电话号码
        phones = re.findall(r'1[3-9]\d{9}|0\d{2,3}\d{7,8}', text_for_search)
        if phones:
            base_info['phone'] = normalize_phone(phones[0])
        else:
            # 尝试其他电话格式
            phone_patterns = [
                r'电话[：:]\s*([0-9\-\s]+)',
                r'tel[：:]\s*([0-9\-\s]+)',
                r'phone[：:]\s*([0-9\-\s]+)',
            ]
            for pattern in phone_patterns:
                match = re.search(pattern, text_for_search, re.IGNORECASE)
                if match:
                    phone_str = match.group(1)
                    base_info['phone'] = normalize_phone(phone_str)
                    break
        
        # 提取邮箱
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_for_search)
        if emails:
            base_info['email'] = normalize_email(emails[0])
        
        # 提取姓名（通常在文档开头或标注了"姓名"）
        name_patterns = [
            r'姓名[：:]\s*([^\s\n，,]+)',
            r'name[：:]\s*([^\s\n]+)',
            r'^([^\s\n，,]+)\s*[\u4e00-\u9fa5]',  # 开头为名字
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text_for_search, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip()
                # 验证名字长度
                if 2 <= len(potential_name) <= 20 and not potential_name.isdigit():
                    base_info['name'] = potential_name
                    break
        
        # 提取地址
        address_patterns = [
            r'地址[：:]\s*([^\n]+)',
            r'address[：:]\s*([^\n]+)',
            r'现住地[：:]\s*([^\n]+)',
        ]
        for pattern in address_patterns:
            match = re.search(pattern, text_for_search, re.IGNORECASE)
            if match:
                base_info['address'] = match.group(1).strip()
                break
        
        return base_info
    
    @staticmethod
    def extract_optional_info(resume_text):
        """
        提取可选信息：求职意向、工作年限、学历背景
        """
        optional_info = {
            'job_intention': None,
            'work_experience_years': None,
            'education': None
        }
        
        text_lower = resume_text.lower()
        
        # 提取求职意向
        job_patterns = [
            r'求职意向[：:]\s*([^\n]+)',
            r'desired position[：:]\s*([^\n]+)',
            r'目标职位[：:]\s*([^\n]+)',
        ]
        for pattern in job_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                optional_info['job_intention'] = match.group(1).strip()
                break
        
        # 提取工作年限
        years_patterns = [
            r'(\d+)\s*年\s*工作经验',
            r'(\d+)\s*years?\s*(?:of\s+)?(?:work\s+)?experience',
            r'工作年限[：:]\s*(\d+)\s*年',
            r'experience[：:]\s*(\d+)\s*years',
        ]
        for pattern in years_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                try:
                    optional_info['work_experience_years'] = int(match.group(1))
                    break
                except:
                    pass
        
        # 提取学历背景
        education_patterns = [
            r'(博士|硕士|本科|大专|高中)[\s]*[\(（][^\)）]*[\)）]?',
            r'(Ph\.?D|Master|Bachelor|Associate)[\s]*(?:in|of)?\s*([^\n]+)',
            r'学历[：:]\s*([^\n]+)',
            r'education[：:]\s*([^\n]+)',
        ]
        for pattern in education_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                optional_info['education'] = match.group(0).strip()
                break
        
        return optional_info
    
    @staticmethod
    def extract_skills(resume_text):
        """
        提取技能信息
        """
        skills = []
        
        # 常见的技能关键词
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', 'PHP',
            'React', 'Vue', 'Angular', 'Django', 'Flask', 'Spring', 'FastAPI',
            'MySQL', 'MongoDB', 'Redis', 'PostgreSQL', 'Oracle',
            'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
            'Git', 'Linux', 'SQL', 'RESTful', 'API',
            'HTML', 'CSS', 'Webpack', 'Node.js', 'Express',
            'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
            'MQ', 'Kafka', 'RabbitMQ', 'Elasticsearch',
            '微服务', '分布式', '高并发', '数据分析', '机器学习',
            'AI', 'NLP', '深度学习', '计算机视觉', '大数据',
        ]
        
        for skill in skill_keywords:
            if skill.lower() in resume_text.lower():
                skills.append(skill)
        
        # 去重
        skills = list(set(skills))
        
        return skills
    
    @staticmethod
    def extract_all_info(resume_text):
        """
        一次性提取所有信息
        """
        return {
            'base_info': AIExtractor.extract_base_info(resume_text),
            'optional_info': AIExtractor.extract_optional_info(resume_text),
            'skills': AIExtractor.extract_skills(resume_text),
            'keywords': extract_keywords(resume_text, top_n=15)
        }
