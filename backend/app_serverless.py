import json
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# 导入核心服务
from services.pdf_parser import PDFParser
from services.ai_hybrid_extractor import HybridExtractor
from services.resume_matcher import ResumeMatcher
from services.cache import CacheManager

# 初始化 Flask
app = Flask(__name__)

# 启用 CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 初始化缓存管理器（本地缓存，支持 Redis）
cache_manager = CacheManager(use_redis=False, redis_config=None)

# 内存存储
sessions = {}
max_sessions = 100

def handler(event, context):
    """
    阿里云函数计算入口点
    与 Flask WSGI 兼容
    """
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    body = event.get('body', '')
    headers = event.get('headers', {})
    
    # 构建 WSGI 环境
    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': event.get('queryString', ''),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.input': None,
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # 添加请求头
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
            key = 'HTTP_' + key
        environ[key] = value
    
    # 处理请求体
    if body:
        import io
        environ['wsgi.input'] = io.BytesIO(body.encode() if isinstance(body, str) else body)
        environ['CONTENT_LENGTH'] = len(body)
    
    # 调用 Flask 应用
    response = []
    
    def start_response(status, response_headers):
        response.append((status, response_headers))
        return lambda x: None
    
    app_iter = app(environ, start_response)
    body = b''.join(app_iter)
    
    if response:
        status_code = int(response[0][0].split()[0])
        headers_dict = dict(response[0][1])
    else:
        status_code = 200
        headers_dict = {}
    
    return {
        'statusCode': status_code,
        'headers': headers_dict,
        'body': body.decode() if isinstance(body, bytes) else body
    }


# API 路由
@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """上传并解析简历"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Empty filename'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'message': 'Only PDF files are supported'}), 400
    
    try:
        # 保存临时文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_path = f'/tmp/{timestamp}_{file.filename}'
        file.save(temp_path)
        
        # 验证和解析 PDF
        is_valid, error = PDFParser.validate_pdf(temp_path)
        if not is_valid:
            return jsonify({'success': False, 'message': f'PDF validation failed: {error}'}), 400
        
        parse_result = PDFParser.extract_text(temp_path)
        if not parse_result['success']:
            return jsonify({'success': False, 'message': f'PDF parsing failed: {parse_result["error"]}'}), 500
        
        # 提取信息
        resume_text = parse_result['data']['raw_text']
        extracted_info = HybridExtractor.extract_all_info(resume_text)
        
        # 生成 session ID
        session_id = f"session_{timestamp}"
        sessions[session_id] = {
            'filename': file.filename,
            'upload_time': datetime.now().isoformat(),
            'resume_text': resume_text,
            'extracted_info': extracted_info
        }
        
        # 清理旧 session
        if len(sessions) > max_sessions:
            oldest = min(sessions.keys())
            del sessions[oldest]
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'filename': file.filename,
                'base_info': extracted_info['base_info'],
                'skills': extracted_info['skills']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # 清理临时文件
        try:
            os.remove(temp_path)
        except:
            pass


@app.route('/api/match', methods=['POST'])
def match_resume():
    """匹配简历与岗位（带缓存机制）"""
    data = request.get_json()
    
    if not data or 'session_id' not in data or 'job_description' not in data:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    session_id = data['session_id']
    if session_id not in sessions:
        return jsonify({'success': False, 'message': 'Session not found'}), 404
    
    session = sessions[session_id]
    job_desc = data['job_description']
    
    try:
        # 生成缓存键（基于简历文本 + 岗位描述）
        cache_key = CacheManager.generate_key('match', {
            'resume_text': session['resume_text'],
            'job_description': job_desc
        })
        
        # 尝试从缓存获取
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            # 处理缓存结果（可能是 dict 或 JSON 字符串）
            if isinstance(cached_result, str):
                cached_data = json.loads(cached_result)
            else:
                cached_data = cached_result
            
            return jsonify({
                'success': True,
                'data': cached_data,
                'from_cache': True
            }), 200
        
        # 缓存未命中，执行匹配
        match_result = ResumeMatcher.match_resume_to_job({
            'skills': session['extracted_info']['skills'],
            'resume_text': session['resume_text'],
            'optional_info': session['extracted_info']['optional_info']
        }, job_desc)
        
        # 缓存结果（同时支持本地和 Redis 缓存）
        cache_manager.set(cache_key, match_result)
        
        return jsonify({
            'success': True,
            'data': match_result,
            'from_cache': False
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/extract', methods=['POST'])
def extract_info():
    """提取简历信息（带缓存机制）"""
    data = request.get_json()
    
    if not data or 'resume_text' not in data:
        return jsonify({'success': False, 'message': 'Missing resume_text'}), 400
    
    try:
        # 生成缓存键
        cache_key = CacheManager.generate_key('extract', {'resume_text': data['resume_text']})
        
        # 尝试从缓存获取
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            # 处理缓存结果（可能是 dict 或 JSON 字符串）
            if isinstance(cached_result, str):
                cached_data = json.loads(cached_result)
            else:
                cached_data = cached_result
            
            return jsonify({
                'success': True,
                'data': cached_data,
                'from_cache': True
            }), 200
        
        # 缓存未命中，执行提取
        extracted = HybridExtractor.extract_all_info(data['resume_text'])
        
        # 缓存结果（同时支持本地和 Redis 缓存）
        cache_manager.set(cache_key, extracted)
        
        return jsonify({
            'success': True,
            'data': extracted,
            'from_cache': False
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'Resume Analyzer API',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
