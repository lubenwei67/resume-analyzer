"""
使用通义千问 LLM 的 AI 信息提取模块
"""
import json
import re
import requests
from typing import Dict, List, Optional
from utils.text_cleaner import (
    is_valid_email, is_valid_phone, normalize_phone, 
    normalize_email, extract_keywords, clean_text
)


class LLMExtractor:
    """使用大语言模型的信息提取器"""
    
    # 通义千问 API 配置
    API_KEY = "sk-fa9248d9096f44d385501939bdc99c6b"
    API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    MODEL = "qwen-plus"
    
    @staticmethod
    def call_qwen_api(prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        调用通义千问 API
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成长度
            
        Returns:
            API 返回的文本内容或 None
        """
        try:
            headers = {
                "Authorization": f"Bearer {LLMExtractor.API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": LLMExtractor.MODEL,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "max_tokens": max_tokens,
                    "temperature": 0.3
                }
            }
            
            response = requests.post(
                LLMExtractor.API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("output", {}).get("choices"):
                    content = result["output"]["choices"][0]["message"]["content"]
                    print(f"[LLM API] 成功获取响应: {content[:100]}")
                    return content
            else:
                print(f"[LLM API] HTTP 错误: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"[LLM API] 异常: {str(e)}")
            return None
    
    @staticmethod
    def extract_base_info_with_llm(resume_text: str) -> Dict:
        """
        使用 LLM 提取基本信息（姓名、电话、邮箱、地址）
        
        Args:
            resume_text: 简历文本
            
        Returns:
            包含基本信息的字典
        """
        base_info = {
            'name': None,
            'phone': None,
            'email': None,
            'address': None
        }
        
        # 构建提示词
        prompt = f"""请从以下简历文本中提取以下信息，并以JSON格式返回（如果找不到某项信息，值设为null）：
- name: 姓名
- phone: 电话号码（仅返回数字和-）
- email: 邮箱地址
- address: 地址

简历文本：
{resume_text[:2000]}

返回格式如下（仅返回JSON，不要其他文本）：
{{"name": "...", "phone": "...", "email": "...", "address": "..."}}"""
        
        # 调用 API
        result_text = LLMExtractor.call_qwen_api(prompt)
        
        if result_text:
            try:
                # 尝试解析 JSON
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group())
                    base_info['name'] = result_json.get('name')
                    base_info['phone'] = normalize_phone(result_json.get('phone')) if result_json.get('phone') else None
                    base_info['email'] = normalize_email(result_json.get('email')) if result_json.get('email') else None
                    base_info['address'] = result_json.get('address')
            except json.JSONDecodeError:
                pass
        
        # 备用：如果 LLM 提取失败，使用正则表达式备选方案
        if not base_info['phone'] or not base_info['email']:
            phones = re.findall(r'1[3-9]\d{9}|0\d{2,3}\d{7,8}', resume_text)
            if phones and not base_info['phone']:
                base_info['phone'] = normalize_phone(phones[0])
            
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
            if emails and not base_info['email']:
                base_info['email'] = normalize_email(emails[0])
        
        return base_info
    
    @staticmethod
    def extract_optional_info_with_llm(resume_text: str) -> Dict:
        """
        使用 LLM 提取可选信息（求职意向、工作年限、学历背景）
        
        Args:
            resume_text: 简历文本
            
        Returns:
            包含可选信息的字典
        """
        optional_info = {
            'job_intention': None,
            'work_experience_years': None,
            'education_background': None
        }
        
        prompt = f"""请从以下简历文本中提取以下信息，并以JSON格式返回（如果找不到某项信息，值设为null）：
- job_intention: 求职意向（职位名称）
- work_experience_years: 工作年限（返回数字）
- education_background: 学历背景（如：本科、硕士等）

简历文本：
{resume_text[:2000]}

返回格式如下（仅返回JSON，不要其他文本）：
{{"job_intention": "...", "work_experience_years": ..., "education_background": "..."}}"""
        
        result_text = LLMExtractor.call_qwen_api(prompt)
        
        if result_text:
            try:
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group())
                    optional_info['job_intention'] = result_json.get('job_intention')
                    optional_info['work_experience_years'] = result_json.get('work_experience_years')
                    optional_info['education_background'] = result_json.get('education_background')
            except json.JSONDecodeError:
                pass
        
        return optional_info
    
    @staticmethod
    def extract_skills_with_llm(resume_text: str) -> List[str]:
        """
        使用 LLM 提取技能列表
        
        Args:
            resume_text: 简历文本
            
        Returns:
            技能列表
        """
        prompt = f"""请从以下简历文本中提取所有技能和专业技术栈（如编程语言、框架、工具等）。
以JSON数组格式返回，格式如：["Python", "Flask", "Django", "MySQL"]

简历文本：
{resume_text[:2000]}

返回格式（仅返回JSON数组，不要其他文本）：
["技能1", "技能2", "技能3", ...]"""
        
        result_text = LLMExtractor.call_qwen_api(prompt)
        skills = []
        
        if result_text:
            try:
                json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                if json_match:
                    skills = json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return skills if isinstance(skills, list) else []
    
    @staticmethod
    def generate_summary_with_llm(resume_text: str) -> Optional[str]:
        """
        使用 LLM 生成简历摘要
        
        Args:
            resume_text: 简历文本
            
        Returns:
            简历摘要
        """
        prompt = f"""请为以下简历生成一个简洁的摘要（不超过100字），总结候选人的主要资质和特点。

简历文本：
{resume_text[:2000]}

摘要："""
        
        return LLMExtractor.call_qwen_api(prompt, max_tokens=300)
    
    @staticmethod
    def extract_all_info(resume_text: str) -> Dict:
        """
        使用 LLM 提取所有信息
        
        Args:
            resume_text: 简历文本
            
        Returns:
            包含所有信息的字典
        """
        # 清洗文本
        cleaned_text = clean_text(resume_text)
        
        return {
            'base_info': LLMExtractor.extract_base_info_with_llm(cleaned_text),
            'optional_info': LLMExtractor.extract_optional_info_with_llm(cleaned_text),
            'skills': LLMExtractor.extract_skills_with_llm(cleaned_text),
            'keywords': extract_keywords(cleaned_text),
            'summary': LLMExtractor.generate_summary_with_llm(cleaned_text)
        }
