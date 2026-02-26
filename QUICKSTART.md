# 快速开始指南

## ⚡ 5 分钟快速开始

### 1. 启动后端服务

#### Windows
```bash
start.bat
```

#### Linux/macOS
```bash
./start.sh
```

### 2. 打开前端应用

直接在浏览器中打开：
```
frontend/index.html
```

或使用 Python 简单服务器：
```bash
cd frontend
python -m http.server 8000
```

然后访问：`http://localhost:8000`

### 3. 配置 API 地址（如果需要）

点击首页右上方的 **API 状态**，或访问：
```
http://localhost:8000/config.html
```

输入：`http://localhost:5000/api`

---

## 🚀 核心功能演示

### 功能 1: 上传和解析简历

1. 点击 **"上传简历"** 标签
2. 选择或拖拽一个 PDF 简历文件
3. 系统自动解析并提取信息
4. 查看提取的姓名、邮箱、技能等

### 功能 2: 简历与岗位匹配

1. 点击 **"简历匹配"** 标签
2. 从下拉菜单选择已上传的简历
3. 输入岗位描述，例如：
   ```
   岗位：Python 后端开发工程师
   需要 3 年以上工作经验
   熟悉 Django/FastAPI
   了解分布式系统、微服务架构
   掌握 Docker、Kubernetes
   优先考虑 AI/ML 背景
   ```
4. 点击 **"计算匹配度"**
5. 查看综合评分、技能匹配率等

### 功能 3: 信息提取

1. 点击 **"信息提取"** 标签
2. 粘贴简历文本
3. 点击 **"提取信息"**
4. 系统自动识别姓名、电话、邮箱等

### 功能 4: 简历管理

1. 点击 **"简历列表"** 标签
2. 查看所有已上传的简历
3. 可选：点击 **"清空所有数据"** 清理测试数据

---

## 📊 API 接口总览

### 上传简历
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@resume.pdf"
```

### 简历匹配
```bash
curl -X POST http://localhost:5000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": "resume_20240226_120000",
    "job_description": "需要 Python 开发工程师..."
  }'
```

### 列出简历
```bash
curl http://localhost:5000/api/resumes
```

### 健康检查
```bash
curl http://localhost:5000/health
```

---

## 🐳 Docker 快速开始

```bash
docker-compose up -d
```

然后访问：`http://localhost`

停止服务：
```bash
docker-compose down
```

---

## 🌍 部署到 GitHub Pages

查看 [DEPLOYMENT.md](DEPLOYMENT.md) 获取完整的部署步骤。

简要步骤：

1. **创建 GitHub 仓库**
   ```bash
   git init
   git add .
   git commit -m "初始提交"
   git remote add origin https://github.com/yourusername/resume-analyzer.git
   git push -u origin main
   ```

2. **复制前端文件到 docs 目录**
   ```bash
   mkdir docs
   cp frontend/* docs/
   git add docs/
   git commit -m "部署前端"
   git push
   ```

3. **启用 GitHub Pages**
   - 仓库 Settings → Pages
   - 选择 `main` 分支
   - 选择 `/docs` 目录

4. **应用将在以下地址可用：**
   ```
   https://yourusername.github.io/resume-analyzer/
   ```

---

## ❓ 常见问题

**Q: 无法连接到后端？**
A: 检查后端是否运行（`http://localhost:5000/health`），或使用 config.html 重新配置 API 地址。

**Q: PDF 文件上传失败？**
A: 确保文件是有效的 PDF 格式，文件大小不超过 10MB。

**Q: 如何在云服务上运行？**
A: 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 中的生产环境部署部分。

**Q: 可以离线使用吗？**
A: 信息提取功能可以离线使用，但上传/匹配需要后端服务。

---

## 📈 下一步

- 📖 阅读 [README.md](README.md) 了解项目详情
- 🚀 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 学习如何部署到生产环境
- 🔧 修改 `backend/config.py` 自定义 API 配置
- 🎨 编辑 `frontend/style.css` 自定义样式

---

**祝你使用愉快！** 🎉
