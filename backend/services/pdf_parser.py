"""
PDF 解析模块
"""
import os
import pdfplumber
from ..utils.text_cleaner import clean_text, extract_segments


class PDFParser:
    """PDF 解析器"""
    
    @staticmethod
    def extract_text(pdf_path):
        """
        从 PDF 文件中提取文本
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            提取的文本内容
        """
        try:
            text_content = {
                'raw_text': '',
                'pages': [],
                'total_pages': 0
            }
            
            with pdfplumber.open(pdf_path) as pdf:
                text_content['total_pages'] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取页面文本
                    page_text = page.extract_text()
                    
                    # 清理文本
                    cleaned_text = clean_text(page_text)
                    
                    text_content['pages'].append({
                        'page_num': page_num,
                        'text': cleaned_text
                    })
                    
                    text_content['raw_text'] += cleaned_text + '\n'
            
            return {
                'success': True,
                'data': text_content,
                'error': None
            }
        
        except FileNotFoundError:
            return {
                'success': False,
                'data': None,
                'error': f'文件不存在: {pdf_path}'
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': f'PDF 解析错误: {str(e)}'
            }
    
    @staticmethod
    def validate_pdf(file_path):
        """
        验证 PDF 文件
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, "文件不存在"
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return False, "文件过大"
            
            # 尝试打开 PDF 文件
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF 文件为空"
            
            return True, "验证通过"
        except Exception as e:
            return False, f"验证失败: {str(e)}"
