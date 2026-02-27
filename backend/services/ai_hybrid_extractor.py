"""
混合信息提取模块 - 优先使用LLM，失败时回退到正则表达式
"""
import json
import re
from typing import Dict, List, Optional
from utils.text_cleaner import (
    is_valid_email, is_valid_phone, normalize_phone, 
    normalize_email, extract_keywords, clean_text
)


class HybridExtractor:
    """混合信息提取器 - 优先 LLM，失败时回退"""
    
    # 导入 LLM 提取器
    llm_available = False
    try:
        from services.ai_llm_extractor import LLMExtractor
        llm_available = True
    except Exception as e:
        print(f"[HybridExtractor] LLM 模块加载失败，将使用备选方案: {e}")
    
    @staticmethod
    def extract_base_info(resume_text: str) -> Dict:
        """提取基本信息 - LLM优先，备选方案"""
        base_info = {
            'name': None,
            'phone': None,
            'email': None,
            'address': None
        }
        
        # 首先尝试 LLM 提取
        if HybridExtractor.llm_available:
            try:
                from services.ai_llm_extractor import LLMExtractor
                llm_result = LLMExtractor.extract_base_info_with_llm(resume_text)
                if llm_result.get('phone') or llm_result.get('email'):
                    return llm_result
            except Exception as e:
                print(f"[HybridExtractor] LLM 提取失败，使用备选方案: {e}")
        
        # 备选方案：正则表达式提取
        lines = resume_text.split('\n')
        text_for_search = resume_text
        
        # 提取电话号码
        phones = re.findall(r'1[3-9]\d{9}|0\d{2,3}\d{7,8}', text_for_search)
        if phones:
            base_info['phone'] = normalize_phone(phones[0])
        
        # 提取邮箱
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_for_search)
        if emails:
            base_info['email'] = normalize_email(emails[0])
        
        # 提取姓名
        name_patterns = [
            r'姓名[：:]\s*([^\s\n，,]+)',
            r'name[：:]\s*([^\s\n]+)',
            r'^([^\s\n，,]+)\s*[\u4e00-\u9fa5]',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text_for_search, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip()
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
    def extract_optional_info(resume_text: str) -> Dict:
        """提取可选信息 - LLM优先，备选方案"""
        optional_info = {
            'job_intention': None,
            'work_experience_years': None,
            'education_background': None
        }
        
        # 首先尝试 LLM 提取
        if HybridExtractor.llm_available:
            try:
                from services.ai_llm_extractor import LLMExtractor
                llm_result = LLMExtractor.extract_optional_info_with_llm(resume_text)
                if llm_result.get('job_intention') or llm_result.get('work_experience_years'):
                    return llm_result
            except Exception as e:
                print(f"[HybridExtractor] LLM 可选信息提取失败，使用备选方案")
        
        # 备选方案：正则表达式提取
        
        # 求职意向
        job_patterns = [
            r'求职意向[：:]\s*([^\n]+)',
            r'目标岗位[：:]\s*([^\n]+)',
            r'应聘岗位[：:]\s*([^\n]+)',
        ]
        for pattern in job_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                optional_info['job_intention'] = match.group(1).strip()
                break
        
        # 工作年限
        years_patterns = [
            r'(\d+)\s*年\s*(?:以上)?工作经验',
            r'工作年限[：:]\s*(\d+)',
        ]
        for pattern in years_patterns:
            match = re.search(pattern, resume_text)
            if match:
                try:
                    optional_info['work_experience_years'] = int(match.group(1))
                    break
                except:
                    pass
        
        # 学历背景
        edu_patterns = [
            r'学历[：:]\s*([^\n]+)',
            r'最高学历[：:]\s*([^\n]+)',
            r'(博士|硕士|本科|专科|高中)',
        ]
        for pattern in edu_patterns:
            match = re.search(pattern, resume_text)
            if match:
                optional_info['education_background'] = match.group(1).strip()
                break
        
        return optional_info
    
    @staticmethod
    def extract_skills(resume_text: str) -> List[str]:
        """提取技能 - LLM优先，备选方案"""
        
        # 首先尝试 LLM 提取
        if HybridExtractor.llm_available:
            try:
                from ai_llm_extractor import LLMExtractor
                llm_skills = LLMExtractor.extract_skills_with_llm(resume_text)
                if llm_skills and len(llm_skills) > 0:
                    return llm_skills
            except Exception as e:
                print(f"[HybridExtractor] LLM 技能提取失败，使用备选方案")
        
        # 备选方案：关键词提取
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
        
        skills = []
        for keyword in skill_keywords:
            if keyword.lower() in resume_text.lower():
                skills.append(keyword)
        
        return list(set(skills))
    
    @staticmethod
    def generate_summary(resume_text: str) -> str:
        """生成总结 - LLM优先，备选方案"""
        
        # 首先尝试 LLM 提取
        if HybridExtractor.llm_available:
            try:
                from ai_llm_extractor import LLMExtractor
                llm_summary = LLMExtractor.generate_summary_with_llm(resume_text)
                if llm_summary:
                    return llm_summary
            except Exception as e:
                print(f"[HybridExtractor] LLM 总结生成失败")
        
        # 备选方案：简单的前几句摘录
        sentences = re.split(r'[。！？\n]', resume_text)
        summary = '。'.join([s.strip() for s in sentences[:3] if s.strip()])
        return summary if summary else ''
    
    @staticmethod
    def extract_all_info(resume_text: str) -> Dict:
        """提取所有信息 - 混合方案"""
        cleaned_text = clean_text(resume_text)
        
        return {
            'base_info': HybridExtractor.extract_base_info(cleaned_text),
            'optional_info': HybridExtractor.extract_optional_info(cleaned_text),
            'skills': HybridExtractor.extract_skills(cleaned_text),
            'keywords': extract_keywords(cleaned_text),
            'summary': HybridExtractor.generate_summary(cleaned_text)
        }
