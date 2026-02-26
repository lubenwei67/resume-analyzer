# 部署指南

本文档提供了多种部署方式的详细步骤。

## 目录

1. [本地开发](#本地开发)
2. [Docker 部署](#docker-部署)
3. [GitHub Pages 部署](#github-pages-部署)
4. [生产环境部署](#生产环境部署)

---

## 本地开发

### 前置要求

- Python 3.8+
- Node.js 12+ (可选，用于 HTTP 服务)
- Git

### 快速开始（Windows）

1. **双击运行启动脚本**
   ```
   start.bat
   ```

2. **在浏览器中打开前端**
   ```
   frontend/index.html
   ```

### 快速开始（Linux/macOS）

1. **运行启动脚本**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

2. **在浏览器中打开前端**
   ```bash
   # 如果有 Python
   python -m http.server 8000 --directory frontend
   # 或使用 Node.js
   npx http-server frontend
   ```

3. **访问应用**
   - 前端：http://localhost:8000
   - 后端：http://localhost:5000
   - 配置 API：http://localhost:8000/config.html

### 手动启动（详细步骤）

#### 安装后端依赖

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

#### 启动后端服务

```bash
python app.py
```

输出应该显示：
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

#### 启动前端服务（可选）

在另一个终端中：

**使用 Python**
```bash
cd frontend
python -m http.server 8000
```

**或使用 Node.js**
```bash
cd frontend
npx http-server
```

#### 访问应用

打开浏览器访问：
- 前端首页：http://localhost:8000（如果使用 HTTP 服务器）
- 直接打开文件：`frontend/index.html`
- API 配置页：http://localhost:8000/config.html（如果使用 HTTP 服务器）

### 本地开发常见问题

**Q: CORS 错误？**
A: 确保后端已启动，且前端正确配置了 API 地址。使用 config.html 进行配置。

**Q: PDF 解析失败？**
A: 确保安装了 `pdfplumber`。在 Windows 上可能需要 Visual C++ Build Tools。

---

## Docker 部署

### 前置要求

- Docker
- Docker Compose

### 启动 Docker 容器

```bash
docker-compose up -d
```

### 访问应用

- 前端：http://localhost:80
- 后端 API：http://localhost:5000
- Redis：localhost:6379

### 查看日志

```bash
docker-compose logs -f backend
docker-compose logs -f redis
```

### 停止服务

```bash
docker-compose down
```

### 清理数据

```bash
docker-compose down -v  # 删除数据卷
```

---

## GitHub Pages 部署

GitHub Pages 用于部署**前端应用**。后端需要单独部署到其他服务。

### 步骤 1: 创建 GitHub 仓库

```bash
git init
git add .
git commit -m "初始提交：AI 智能简历分析系统"
git branch -M main
git remote add origin https://github.com/yourusername/resume-analyzer.git
git push -u origin main
```

### 步骤 2: 配置 GitHub Pages

1. 进入 GitHub 仓库设置
2. 找到 **Pages** 部分（在左侧菜单 Code and automation 下）
3. 选择 **Deploy from a branch**
4. 选择分支：`main`
5. 选择文件夹：`/docs`
6. 点击 **Save**

### 步骤 3: 复制前端文件到 docs 目录

```bash
# 创建 docs 目录
mkdir docs

# 复制前端文件
cp frontend/* docs/

# 提交更改
git add docs/
git commit -m "部署前端到 GitHub Pages"
git push
```

### 步骤 4: 配置后端 API 地址

前端应用将在 GitHub Pages 上运行，但需要连接到后端 API。

#### 选项 A: 用户手动配置（推荐用于演示）

用户访问应用时：
1. 点击页面右上方 **API 状态**
2. 或打开 `/config.html` 配置页面
3. 输入后端 API 地址

#### 选项 B: 配置固定的后端地址

编辑 `frontend/script.js`：

```javascript
// 改这一行
let API_BASE_URL = localStorage.getItem('apiUrl') || 'http://localhost:5000/api';

// 为：
let API_BASE_URL = localStorage.getItem('apiUrl') || 'https://your-backend.com/api';
```

### GitHub Pages 访问 URL

应用将在以下地址可用：

```
https://yourusername.github.io/resume-analyzer/
```

---

## 生产环境部署

### 后端部署到阿里云 Serverless

#### 安装 Serverless Framework

```bash
npm install -g serverless
```

#### 配置阿里云凭证

编辑 `~/.serverless/credentials.yml`（或运行 `serverless configure`）：

```yaml
alibaba:
  credentials:
    AccessKeyID: your_access_key
    AccessKeySecret: your_access_secret
```

#### 创建 serverless.yml

在项目根目录创建 `serverless.yml`：

```yaml
service: resume-analyzer

provider:
  name: alibaba
  runtime: python3.9
  region: cn-shanghai

functions:
  app:
    handler: backend.app.app
    events:
      - http:
          path: /
          method: ANY
      - http:
          path: /{proxy+}
          method: ANY

plugins:
  - serverless-python-requirements

package:
  individually: true
  patterns:
    - backend/**
    - '!backend/venv/**'
    - '!backend/__pycache__/**'
```

#### 部署

```bash
serverless deploy
```

### 后端部署到其他云服务

#### Heroku（如果仍可用）

```bash
heroku create your-app-name
git push heroku main
```

#### PythonAnywhere

1. 上传代码到 PythonAnywhere
2. 创建 Web 应用
3. 配置 WSGI 文件

#### AWS Lambda

使用 `zappa` 部署：

```bash
pip install zappa
zappa init
zappa deploy production
```

#### 自有服务器 (CentOS/Ubuntu)

```bash
# 安装依赖
sudo yum install python3 python3-pip nginx

# 创建虚拟环境
python3 -m venv /var/www/resume-analyzer/venv
source /var/www/resume-analyzer/venv/bin/activate

# 安装应用依赖
pip install -r requirements.txt
pip install gunicorn

# 使用 Gunicorn 运行
gunicorn --workers 4 --bind 0.0.0.0:5000 backend.app:app

# 配置 Nginx 反向代理
sudo cp nginx.conf /etc/nginx/sites-available/resume-analyzer
sudo ln -s /etc/nginx/sites-available/resume-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 启用 HTTPS

使用 Let's Encrypt：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 环境变量配置

生产环境应设置：

```bash
export DEBUG=False
export REDIS_ENABLED=True
export REDIS_HOST=your-redis-host
export REDIS_PORT=6379
```

---

## 监控和维护

### 检查服务状态

```bash
curl http://localhost:5000/health
```

### 查看日志

```bash
# Docker
docker-compose logs -f backend

# Linux 系统日志
journalctl -u resume-analyzer -f
```

### 清理上传的文件

```bash
rm -rf backend/uploads/*
```

### 更新应用

```bash
git pull origin main
pip install -r backend/requirements.txt
systemctl restart resume-analyzer
```

---

## 故障排查

### API 连接失败

1. 检查后端是否运行：`curl http://localhost:5000/health`
2. 检查防火墙设置
3. 检查前端配置的 API 地址是否正确

### CORS 错误

确保 Flask 应用启用了 CORS：
```python
from flask_cors import CORS
CORS(app)  # 应在 app.py 中
```

### PDF 解析失败

- 检查 PDF 文件是否损坏
- 某些扫描版本 PDF 需要 OCR 支持
- 检查依赖：`pip install pdfplumber`

### 性能问题

1. 启用 Redis 缓存
2. 增加 Gunicorn worker 数量
3. 启用 Nginx 缓存

---

## 安全建议

1. **生产环境**：设置 `DEBUG=False`
2. **HTTPS**：使用 SSL 证书加密通信
3. **速率限制**：添加 Flask-Limiter 限制请求速率
4. **文件验证**：验证上传的 PDF 文件
5. **输入清消**：防止注入攻击

---

## 成本估算（如果使用云服务）

- **阿里云 Serverless**：按调用次数计费，基本免费额度内足以支撑演示
- **GitHub Pages**：完全免费
- **Redis 缓存**：可选，演示环境可不用

---

有问题？查看 [README.md](../README.md) 或创建 Issue。
