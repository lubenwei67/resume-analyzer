"""
Flask 主应用 - AI 赋能的智能简历分析系统
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

from config import (
    DEBUG, UPLOAD_FOLDER, MAX_FILE_SIZE, REDIS_ENABLED, 
    REDIS_HOST, REDIS_PORT, REDIS_DB
)
from services.pdf_parser import PDFParser
from services.ai_hybrid_extractor import HybridExtractor  # 使用混合提取器（优先LLM，备选正则）
from services.resume_matcher import ResumeMatcher
from services.cache import CacheManager

# 初始化 Flask 应用
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 启用 CORS
CORS(app)

# 初始化缓存
redis_config = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB
}
cache_manager = CacheManager(use_redis=REDIS_ENABLED, redis_config=redis_config)

# 存储已上传简历信息（内存存储，用于演示）
uploaded_resumes = {}


@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Resume Analysis System'
    }), 200


@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """
    上传简历接口
    
    接收 PDF 格式的简历文件，解析内容并提取关键信息
    """
    try:
        # 检查是否上传了文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '未找到文件',
                'error': 'No file part'
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '文件名为空',
                'error': 'Empty filename'
            }), 400
        
        # 检查文件类型
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'message': '仅支持 PDF 格式',
                'error': 'Only PDF files are supported'
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        # 验证 PDF 文件
        is_valid, error_msg = PDFParser.validate_pdf(filepath)
        if not is_valid:
            os.remove(filepath)  # 删除无效文件
            return jsonify({
                'success': False,
                'message': f'PDF 验证失败: {error_msg}',
                'error': error_msg
            }), 400
        
        # 解析 PDF
        parse_result = PDFParser.extract_text(filepath)
        if not parse_result['success']:
            os.remove(filepath)
            return jsonify({
                'success': False,
                'message': f'PDF 解析失败: {parse_result["error"]}',
                'error': parse_result['error']
            }), 500
        
        # 提取关键信息（使用混合提取器：优先LLM，失败时回退）
        resume_text = parse_result['data']['raw_text']
        extracted_info = HybridExtractor.extract_all_info(resume_text)
        
        # 生成简历 ID
        resume_id = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 存储简历信息
        resume_data = {
            'resume_id': resume_id,
            'filename': filename,
            'filepath': filepath,
            'upload_time': datetime.now().isoformat(),
            'resume_text': resume_text,
            'pdf_info': parse_result['data'],
            'extracted_info': extracted_info
        }
        
        uploaded_resumes[resume_id] = resume_data
        
        # 缓存简历信息
        cache_key = CacheManager.generate_key('resume', {'filename': filename})
        cache_manager.set(cache_key, resume_data)
        
        return jsonify({
            'success': True,
            'message': '简历上传成功',
            'data': {
                'resume_id': resume_id,
                'filename': filename,
                'base_info': extracted_info['base_info'],
                'optional_info': extracted_info['optional_info'],
                'skills': extracted_info['skills'],
                'keywords': extracted_info['keywords']
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'处理错误: {str(e)}',
            'error': str(e)
        }), 500


@app.route('/api/resume/<resume_id>', methods=['GET'])
def get_resume(resume_id):
    """
    获取已解析的简历信息
    """
    if resume_id not in uploaded_resumes:
        return jsonify({
            'success': False,
            'message': '简历不存在',
            'error': f'Resume with ID {resume_id} not found'
        }), 404
    
    resume_data = uploaded_resumes[resume_id]
    
    return jsonify({
        'success': True,
        'data': {
            'resume_id': resume_data['resume_id'],
            'filename': resume_data['filename'],
            'upload_time': resume_data['upload_time'],
            'extracted_info': resume_data['extracted_info']
        }
    }), 200


@app.route('/api/match', methods=['POST'])
def match_resume():
    """
    简历与岗位匹配接口
    
    接收简历 ID 和岗位描述，返回匹配度评分
    """
    try:
        data = request.get_json()
        
        # 检查必要参数
        if not data or 'resume_id' not in data or 'job_description' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数',
                'error': 'Missing resume_id or job_description'
            }), 400
        
        resume_id = data['resume_id']
        job_description = data['job_description']
        
        # 检查简历是否存在
        if resume_id not in uploaded_resumes:
            return jsonify({
                'success': False,
                'message': '简历不存在',
                'error': f'Resume with ID {resume_id} not found'
            }), 404
        
        resume_data = uploaded_resumes[resume_id]
        
        # 生成缓存键
        cache_key = CacheManager.generate_key('match', {
            'resume_id': resume_id,
            'job_description': job_description
        })
        
        # 检查缓存
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return jsonify({
                'success': True,
                'message': '匹配结果（来自缓存）',
                'data': cached_result,
                'from_cache': True
            }), 200
        
        # 执行匹配
        match_result = ResumeMatcher.match_resume_to_job(
            {
                'skills': resume_data['extracted_info']['skills'],
                'resume_text': resume_data['resume_text'],
                'optional_info': resume_data['extracted_info']['optional_info']
            },
            job_description
        )
        
        # 缓存结果
        cache_manager.set(cache_key, match_result)
        
        return jsonify({
            'success': True,
            'message': '匹配成功',
            'data': match_result,
            'from_cache': False
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'处理错误: {str(e)}',
            'error': str(e)
        }), 500


@app.route('/api/extract', methods=['POST'])
def extract_info():
    """
    直接从文本中提取信息的接口
    
    用于测试，不需要上传 PDF 文件
    """
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify({
                'success': False,
                'message': '缺少 resume_text 参数',
                'error': 'Missing resume_text'
            }), 400
        
        resume_text = data['resume_text']
        
        # 提取信息（使用混合提取器）
        extracted_info = HybridExtractor.extract_all_info(resume_text)
        
        return jsonify({
            'success': True,
            'message': '信息提取成功',
            'data': extracted_info
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'处理错误: {str(e)}',
            'error': str(e)
        }), 500


@app.route('/api/resumes', methods=['GET'])
def list_resumes():
    """
    列出所有已上传的简历
    """
    resume_list = []
    
    for resume_id, resume_data in uploaded_resumes.items():
        resume_list.append({
            'resume_id': resume_id,
            'filename': resume_data['filename'],
            'upload_time': resume_data['upload_time'],
            'candidate_name': resume_data['extracted_info']['base_info'].get('name', '未知'),
            'candidate_email': resume_data['extracted_info']['base_info'].get('email', '未知')
        })
    
    return jsonify({
        'success': True,
        'message': f'共 {len(resume_list)} 份简历',
        'data': resume_list
    }), 200


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """
    清空所有数据（测试用）
    """
    global uploaded_resumes
    uploaded_resumes.clear()
    cache_manager.clear()
    
    return jsonify({
        'success': True,
        'message': '数据已清空'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'message': '端点不存在',
        'error': 'Not Found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'success': False,
        'message': '服务器内部错误',
        'error': str(error)
    }), 500


if __name__ == '__main__':
    print(f"启动简历分析系统...")
    print(f"Debug 模式: {DEBUG}")
    print(f"Redis 缓存: {'已启用' if REDIS_ENABLED else '已禁用'}")
    print(f"监听地址: http://0.0.0.0:5000")
    
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
