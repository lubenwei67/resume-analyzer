# 阿里云 Serverless 部署指南

## 快速部署（推荐）

本项目已准备好部署到阿里云函数计算（Function Compute）。

### 前置条件

1. **阿里云账号** - 注册地址：https://www.aliyun.com/
2. **函数计算体验版权限** - 免费额度充足（每月 100 万次调用免费）
3. **Serverless 工具** - 可选，使用 Serverless Framework 简化部署

### 方案 A：手动部署（通过阿里云控制台）

#### 步骤 1：创建函数

1. 登录 [阿里云控制台](https://console.aliyun.com/)
2. 导航至 **函数计算** → **服务及函数**
3. 点击 **创建服务**
   - 服务名：`resume-analyzer`
   - 描述：`AI-Powered Resume Analysis System`
   - 其他选项：默认

4. 在服务中创建函数
   - 函数名：`api`
   - 运行环境：`Python 3.9`
   - 函数处理程序：`app.handler`
   - 代码上传方式：**上传代码**

#### 步骤 2：准备代码包

```bash
# 1. 进入 backend 目录
cd backend

# 2. 创建部署包目录
mkdir -p package

# 3. 复制应用代码
cp app_serverless.py package/app.py
cp config.py package/
cp -r services package/
cp -r utils package/

# 4. 安装依赖到包目录
pip install -r requirements.txt -t package/

# 5. 创建 ZIP 包
cd package
zip -r ../resume-analyzer.zip .
cd ..

# 6. 上传 resume-analyzer.zip 到函数
```

#### 步骤 3：配置环境变量

在函数详情页面，设置环境变量：

```
ALIYUN_QWEN_API_KEY=sk-fa9248d9096f44d385501939bdc99c6b
FLASK_ENV=production
DEBUG=False
```

#### 步骤 4：配置触发器

1. 在函数详情中点击 **触发器** → **创建触发器**
2. 选择触发器类型：**HTTP 触发器**
3. 认证方式：**无认证**（公开 API）
4. HTTP 方法：**POST, GET**
5. 记下生成的函数 URL，如：
   ```
   https://xxx.fc.aliyuncs.com/2016-08-15/proxy/resume-analyzer/api/
   ```

#### 步骤 5：更新前端配置

修改前端的 `config.html`，将后端 API 地址改为：

```javascript
const API_BASE_URL = 'https://xxx.fc.aliyuncs.com/2016-08-15/proxy/resume-analyzer/api';
```

---

### 方案 B：Serverless Framework 部署（最简单）

#### 1. 安装 Serverless Framework

```bash
npm install -g serverless
```

#### 2. 创建部署配置

项目已包含 `serverless.yml` 配置文件：

```yaml
service: resume-analyzer

provider:
  name: aliyun
  runtime: python3.9
  region: cn-beijing  # 可改为其他地区
  memorySize: 512
  timeout: 60
  environment:
    ALIYUN_QWEN_API_KEY: sk-fa9248d9096f44d385501939bdc99c6b

functions:
  api:
    handler: app.handler
    events:
      - http:
          path: /api
          method: ANY

plugins:
  - serverless-aliyun-function-compute
```

#### 3. 部署

```bash
# 设置 AccessKey
serverless config credentials --provider aliyun \
  --key YOUR_ACCESS_KEY_ID \
  --secret YOUR_ACCESS_KEY_SECRET

# 部署函数
serverless deploy

# 部署完成后会显示函数 URL
```

---

### 方案 C：Docker 容器部署

使用容器化部署到 ECS 或 ACR：

```bash
# 构建 Docker 镜像
docker build -t resume-analyzer:latest .

# 推送到阿里云容器镜像服务 (ACR)
docker tag resume-analyzer:latest registry.cn-beijing.aliyuncs.com/resume/analyzer:latest
docker push registry.cn-beijing.aliyuncs.com/resume/analyzer:latest

# 在 ECS 或 K8s 中运行
docker run -d -p 5000:5000 registry.cn-beijing.aliyuncs.com/resume/analyzer:latest
```

---

## 配置说明

### 环境变量

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `ALIYUN_QWEN_API_KEY` | 通义千问 API Key | `sk-fa9248d...` |
| `FLASK_ENV` | Flask 环境 | `production` |
| `DEBUG` | 调试模式 | `False` |
| `REDIS_ENABLED` | 是否启用 Redis 缓存 | `False`（Serverless 环境推荐关闭） |

### Serverless 环境特殊注意

1. **临时文件存储**
   - 使用 `/tmp` 目录（限制 512MB）
   - 不能持久化存储已上传的 PDF

2. **性能优化**
   - 冷启动时间：2-3 秒
   - 建议内存配置：512MB 或更高
   - 超时设置：30-60 秒

3. **成本考虑**
   - 函数计算免费额度：100 万次/月
   - 按使用量计费，月成本可能 < $1
   - 存储费用：仅在保留长期文件时产生

---

## 部署后验证

1. **测试健康检查**
   ```bash
   curl https://xxx.fc.aliyuncs.com/2016-08-15/proxy/resume-analyzer/api/health
   ```

2. **测试信息提取**
   ```bash
   curl -X POST https://xxx.fc.aliyuncs.com/2016-08-15/proxy/resume-analyzer/api/extract \
     -H "Content-Type: application/json" \
     -d '{"resume_text":"姓名：张三\n电话：13812345678\n邮箱：test@example.com"}'
   ```

3. **更新前端配置**
   - 编辑 `frontend/config.html`
   - 修改 `API_BASE_URL` 为实际的函数 URL
   - 重新部署到 GitHub Pages

---

## 故障排除

### 函数日志查看

```bash
# 使用阿里云 CLI 查看日志
aliyun fc get-function-logs resume-analyzer api

# 或在阿里云控制台查看：
# 函数详情 → 日志 → 查询
```

### 常见问题

1. **超时错误**
   - 增加函数超时时间（最多 600 秒）
   - 优化 PDF 解析性能

2. **内存不足**
   - 增加内存配置（512MB 或更高）
   - 清理临时文件

3. **API Key 失效**
   - 检查环境变量是否正确设置
   - 重新生成或更新 API Key

---

## 项目结构

```
backend/
├── app.py                      # 本地开发版（Flask 直接运行）
├── app_serverless.py           # Serverless 版（阿里云函数计算）
├── config.py                   # 配置文件
├── serverless.yml              # Serverless Framework 配置
├── Dockerfile                  # Docker 容器配置
└── services/
    ├── pdf_parser.py           # PDF 解析
    ├── ai_hybrid_extractor.py  # 混合 AI 提取器（LLM + 正则）
    ├── ai_llm_extractor.py     # 通义千问 LLM 提取器
    ├── resume_matcher.py       # 简历匹配引擎
    └── cache.py                # 缓存管理
```

---

## 后续优化

1. **缓存优化**
   - 集成 Redis 或使用阿里云 Memcache
   - 缓存 LLM 提取结果

2. **性能优化**
   - 异步处理 PDF 解析
   - 预加载模型

3. **安全加固**
   - 添加请求签名验证
   - 限制上传文件大小
   - 实现速率限制

4. **监控告警**
   - 配置函数性能监控
   - 设置错误告警

---

**需要帮助？** 查看阿里云函数计算官方文档：
https://help.aliyun.com/product/50127.html
