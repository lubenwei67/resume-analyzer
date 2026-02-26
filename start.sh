#!/bin/bash
# 快速启动脚本

echo "=== 启动 AI 智能简历分析系统 ==="

# 检查是否安装了 Docker
if command -v docker &> /dev/null; then
    echo "使用 Docker Compose 启动..."
    docker-compose up -d
    echo "✓ 服务已启动"
    echo "前端地址: http://localhost:80"
    echo "后端 API: http://localhost:5000"
else
    echo "未找到 Docker。使用本地 Python 启动..."
    
    # 检查 Python 依赖
    if [ ! -d "backend/venv" ]; then
        echo "创建虚拟环境..."
        python -m venv backend/venv
    fi
    
    # 激活虚拟环境
    source backend/venv/bin/activate
    
    # 安装依赖
    echo "安装依赖..."
    pip install -r backend/requirements.txt
    
    # 启动后端
    echo "启动后端服务..."
    cd backend
    python app.py &
    cd ..
    
    echo "✓ 后端服务已启动: http://localhost:5000"
    echo ""
    echo "在浏览器中打开 frontend/index.html 或使用 Python 简单服务器："
    echo "  python -m http.server 8000 --directory frontend"
fi
