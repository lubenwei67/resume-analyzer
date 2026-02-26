@echo off
REM 快速启动脚本（Windows）

echo === 启动 AI 智能简历分析系统 ===

REM 检查虚拟环境
if not exist "backend\venv" (
    echo 创建虚拟环境...
    python -m venv backend\venv
)

REM 激活虚拟环境
call backend\venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r backend\requirements.txt

REM 启动后端
echo 启动后端服务...
cd backend
python app.py
cd ..

echo.
echo 在浏览器中打开 frontend\index.html
echo 或使用 Python 简单服务器:
echo   python -m http.server 8000 --directory frontend
