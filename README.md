# AI 赋能的智能简历分析系统

一个基于 Python Flask 后端和现代前端的智能简历分析平台，能够自动解析简历、提取关键信息、并与岗位需求进行匹配。

## 功能特性

### ✨ 核心功能

1. **简历上传与解析**
   - 支持 PDF 格式简历上传
   - 多页简历智能识别
   - PDF 文本自动提取和清洗

2. **关键信息提取**
   - 基本信息：姓名、电话、邮箱、地址
   - 可选信息：求职意向、工作年限、学历背景
   - 技能识别和关键词提取

3. **简历与岗位匹配**
   - 智能技能匹配（40%权重）
   - 工作经验匹配（30%权重）
   - 文本相似度分析（30%权重）
   - 综合评分和推荐意见

4. **性能优化**
   - 本地内存缓存机制
   - 可选 Redis 缓存支持
   - 快速重复查询响应

### 🚀 技术栈

**后端**
- Python 3.8+
- Flask 2.3+
- pdfplumber (PDF 解析)
- jieba (中文分词)
- Flask-CORS (跨域资源共享)

**前端**
- HTML5
- CSS3
- JavaScript (原生)
- 响应式设计

**部署**
- GitHub Pages (前端)
- 任意 Python 服务器 (后端)
- 可选：Docker 容器化

## 项目结构

```
.
├── backend/                    # Python 后端服务
│   ├── app.py                 # Flask 主应用
│   ├── config.py              # 配置文件
│   ├── requirements.txt        # Python 依赖
│   ├── services/              # 业务逻辑模块
│   │   ├── pdf_parser.py      # PDF 解析
│   │   ├── ai_extractor.py    # 信息提取
│   │   ├── resume_matcher.py  # 简历匹配
│   │   └── cache.py           # 缓存管理
│   └── utils/
│       └── text_cleaner.py    # 文本处理
├── frontend/                   # 前端应用
│   ├── index.html             # 主页面
│   ├── style.css              # 样式表
│   └── script.js              # JavaScript 逻辑
├── README.md                  # 项目文档
└── .github/
    └── workflows/
        └── deploy.yml         # GitHub Actions 部署配置
```

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- Node.js 12+ (可选，用于本地开发)
- Git

### 后端安装与运行

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **运行服务**
```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

3. **API 端点**

#### 上传简历
```bash
POST /api/upload
Content-Type: multipart/form-data

Body: file (PDF 文件)
```

**返回示例**
```json
{
  "success": true,
  "message": "简历上传成功",
  "data": {
    "resume_id": "resume_20240226_120000",
    "filename": "resume.pdf",
    "base_info": {
      "name": "张三",
      "phone": "13800138000",
      "email": "zhangsan@example.com",
      "address": "北京市朝阳区"
    },
    "skills": ["Python", "Flask", "Docker"],
    "keywords": ["后端开发", "API设计", "数据库"]
  }
}
```

#### 简历匹配
```bash
POST /api/match
Content-Type: application/json

{
  "resume_id": "resume_20240226_120000",
  "job_description": "我们需要一个 Python 后端开发工程师，需要 3 年以上工作经验..."
}
```

**返回示例**
```json
{
  "success": true,
  "message": "匹配成功",
  "data": {
    "total_score": 85.5,
    "skill_match": 90,
    "experience_match": 80,
    "text_similarity": 75,
    "matched_skills": ["Python", "Flask"],
    "job_keywords": ["Python", "Flask", "Django"],
    "recommendation": "强烈推荐"
  }
}
```

#### 信息提取
```bash
POST /api/extract
Content-Type: application/json

{
  "resume_text": "姓名: 张三\n电话: 13800138000\n邮箱: zhangsan@example.com\n..."
}
```

#### 获取简历列表
```bash
GET /api/resumes
```

#### 健康检查
```bash
GET /health
```

### 前端部署

#### 选项 1: 部署到 GitHub Pages

1. **创建 GitHub 仓库**
```bash
git init
git add .
git commit -m "初始提交"
git branch -M main
git remote add origin https://github.com/yourusername/resume-analyzer.git
git push -u origin main
```

2. **启用 GitHub Pages**
   - 在 GitHub 仓库设置中，找到 Pages 部分
   - 选择 `main` 分支作为源
   - 选择 `/frontend` 作为根目录
   - 保存

3. **配置前端 API 地址**
   
   编辑 `frontend/script.js`，更改 API_BASE_URL：
```javascript
const API_BASE_URL = 'https://your-backend-server.com/api';
```

#### 选项 2: 部署到阿里云 Serverless

1. **安装 Serverless Framework**
```bash
npm install -g serverless
```

2. **配置阿里云凭证**
```bash
serverless configure
```

3. **部署**
```bash
serverless deploy
```

## 使用示例

### 1. 上传简历

1. 点击"上传简历"标签页
2. 选择或拖拽 PDF 简历文件
3. 系统自动解析并提取关键信息

### 2. 匹配岗位

1. 点击"简历匹配"标签页
2. 从下拉菜单选择已上传的简历
3. 输入岗位描述
4. 点击"计算匹配度"按钮
5. 查看匹配评分和推荐意见

### 3. 直接提取信息

1. 点击"信息提取"标签页
2. 粘贴或输入简历文本
3. 点击"提取信息"按钮
4. 查看提取的结构化信息

## API 文档详解

### 请求/响应格式

所有 API 返回 JSON 格式，统一的响应结构：

```json
{
  "success": true|false,
  "message": "描述信息",
  "data": {...},
  "error": "错误信息（仅在失败时存在）"
}
```

### 错误处理

| HTTP 状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

## 配置

编辑 `backend/.env` 文件进行配置：

```env
DEBUG=True
HOST=0.0.0.0
PORT=5000

# AI 提供商配置
AI_PROVIDER=local
OPENAI_API_KEY=your_key_here

# Redis 缓存配置
REDIS_ENABLED=False
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760  # 10MB
```

## 性能优化

### 缓存机制

- **本地缓存**：默认启用，支持最多 100 条记录，24 小时过期
- **Redis 缓存**：可选，需要安装 Redis 服务器

启用 Redis 缓存：
```env
REDIS_ENABLED=True
REDIS_HOST=your-redis-host
REDIS_PORT=6379
```

### 响应时间优化

- 首次解析某份简历：~500ms
- 重复查询（缓存命中）：~50ms
- 匹配计算：~100ms

## 扩展功能

### 可选实现

1. **数据库存储**
   - 使用 SQLAlchemy 存储简历记录
   - 历史查询记录保存

2. **多人协作**
   - 用户认证和授权
   - 简历分享功能

3. **高级 AI 功能**
   - 集成 GPT/Claude API
   - 更精准的文本相似度计算
   - 个性化推荐

4. **数据分析**
   - 简历数据大盘
   - 匹配度分布分析
   - 热门技能统计

## 常见问题

**Q: PDF 解析失败？**
A: 检查 PDF 文件是否损坏或加密。某些扫描版本的 PDF 无法直接提取文本。

**Q: 信息提取不准确？**
A: 系统基于规则和关键词匹配。复杂格式的简历需要手动调整正则表达式。

**Q: 跨域请求失败？**
A: 确保后端已启用 CORS，前端配置了正确的 API_BASE_URL。

**Q: 如何在生产环境部署？**
A: 使用 Gunicorn + Nginx + Docker 的组合。参考 `docker-compose.yml`。

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交 Issues 或 Pull Requests。

---

**开发时间**: 2024年2月26日  
**版本**: 1.0.0  
**作者**: 后端实习岗位候选人
