"""
简历与岗位匹配模块
"""
import re
from collections import Counter
from difflib import SequenceMatcher


class ResumeMatcher:
    """简历和岗位匹配器"""
    
    @staticmethod
    def extract_job_keywords(job_description):
        """
        从岗位描述中提取关键词
        """
        # 常见的岗位相关关键词
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
            '实习', '校招', '社招', '全职', '兼职', '远程',
        ]
        
        keywords = []
        for keyword in skill_keywords:
            if keyword.lower() in job_description.lower():
                keywords.append(keyword)
        
        return list(set(keywords))
    
    @staticmethod
    def calculate_skill_match(resume_skills, job_keywords):
        """
        计算技能匹配率
        """
        if not job_keywords:
            return 0.0
        
        matched_skills = [skill for skill in resume_skills if skill in job_keywords]
        match_rate = len(matched_skills) / len(job_keywords) if job_keywords else 0
        
        return round(match_rate * 100, 2)
    
    @staticmethod
    def calculate_text_similarity(text1, text2):
        """
        计算两个文本的相似度（基于 SequenceMatcher）
        """
        if not text1 or not text2:
            return 0.0
        
        # 转换为小写
        text1 = str(text1).lower()
        text2 = str(text2).lower()
        
        # 计算相似度
        similarity = SequenceMatcher(None, text1, text2).ratio()
        return round(similarity * 100, 2)
    
    @staticmethod
    def calculate_experience_match(resume_years, job_requirements):
        """
        计算工作经验匹配度
        """
        if resume_years is None:
            return 50.0  # 未指定工作年限，给予中等评分
        
        # 从岗位描述中判断需要的经验年限
        experience_patterns = [
            (r'(\d+)\s*年\s*(?:以上)?工作经验', 'years'),
            (r'(\d+)\s*\+\s*years?\s+(?:of\s+)?experience', 'years'),
            (r'experienced|senior|junior|entry', 'level'),
        ]
        
        required_years = 0
        for pattern, exp_type in experience_patterns:
            match = re.search(pattern, job_requirements, re.IGNORECASE)
            if match and exp_type == 'years':
                try:
                    required_years = int(match.group(1))
                    break
                except:
                    pass
        
        # 简单的匹配逻辑
        if required_years == 0:
            return 100.0  # 无明确要求
        
        if resume_years >= required_years:
            return 100.0
        elif resume_years >= required_years - 1:
            return 80.0
        elif resume_years >= required_years - 2:
            return 60.0
        else:
            return max(0, (resume_years / required_years) * 100)
    
    @staticmethod
    def match_resume_to_job(resume_info, job_description):
        """
        将简历与岗位进行匹配，计算总体评分
        
        Args:
            resume_info: 提取的简历信息字典
            job_description: 岗位描述文本
            
        Returns:
            匹配结果字典
        """
        # 提取岗位关键词
        job_keywords = ResumeMatcher.extract_job_keywords(job_description)
        
        # 计算各项匹配度
        skill_match = ResumeMatcher.calculate_skill_match(
            resume_info.get('skills', []),
            job_keywords
        )
        
        # 计算文本相似度
        resume_text = resume_info.get('resume_text', '')
        text_similarity = ResumeMatcher.calculate_text_similarity(
            resume_text,
            job_description
        )
        
        # 计算工作经验匹配度
        work_years = resume_info.get('optional_info', {}).get('work_experience_years')
        experience_match = ResumeMatcher.calculate_experience_match(
            work_years,
            job_description
        )
        
        # 计算综合评分（加权平均）
        total_score = (
            skill_match * 0.4 +      # 技能匹配权重 40%
            experience_match * 0.3 +  # 工作经验权重 30%
            text_similarity * 0.3     # 文本相似度权重 30%
        )
        
        total_score = round(total_score, 2)
        
        return {
            'total_score': total_score,
            'skill_match': skill_match,
            'experience_match': experience_match,
            'text_similarity': text_similarity,
            'matched_skills': [skill for skill in resume_info.get('skills', []) if skill in job_keywords],
            'job_keywords': job_keywords,
            'recommendation': get_recommendation(total_score)
        }


def get_recommendation(score):
    """
    根据分数给出推荐意见
    """
    if score >= 80:
        return '强烈推荐'
    elif score >= 60:
        return '推荐'
    elif score >= 40:
        return '一般'
    else:
        return '不推荐'
