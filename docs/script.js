// API 配置 - 从 localStorage 读取，或使用默认值
let API_BASE_URL = localStorage.getItem('apiUrl') || 'https://api-bidansviue.cn-hangzhou.fcapp.run/api';

// 当前选中的简历 ID
let currentResumeId = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否已配置
    if (!localStorage.getItem('apiConfigured')) {
        // 如果在 GitHub Pages 上，提示用户需要配置
        if (window.location.hostname.includes('github.io')) {
            showDevMessage();
        }
    }
    
    setupEventListeners();
    checkApiStatus();
    listResumes();
});

// 显示开发提示信息
function showDevMessage() {
    const message = document.createElement('div');
    message.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 8px;
        padding: 15px;
        max-width: 300px;
        z-index: 9999;
        font-size: 0.9rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    message.innerHTML = `
        <strong>⚠️ 需要配置后端服务</strong>
        <p style="margin: 10px 0 0 0;">由于您在 GitHub Pages 上访问，需要配置后端 API 地址。</p>
        <a href="config.html" style="display: inline-block; margin-top: 10px; padding: 8px 12px; background: #667eea; color: white; text-decoration: none; border-radius: 4px;">
            前往配置
        </a>
    `;
    document.body.appendChild(message);
}

// 设置事件监听器
function setupEventListeners() {
    // 标签页切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });

    // 上传区域
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            uploadResume();
        }
    });

    fileInput.addEventListener('change', uploadResume);
}

// 切换标签页
function switchTab(tabName) {
    // 隐藏所有标签页内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // 移除所有按钮的 active 类
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // 显示选中的标签页
    document.getElementById(tabName).classList.add('active');

    // 激活对应的按钮
    event.target.classList.add('active');
}

// 检查 API 状态
function checkApiStatus() {
    const healthUrl = API_BASE_URL.replace('/api', '') + '/health';
    
    fetch(healthUrl, { timeout: 5000 })
        .then(response => {
            if (response.ok) {
                document.getElementById('apiStatus').textContent = '正常 ✓';
                document.getElementById('apiStatus').style.color = '#52c41a';
            } else {
                throw new Error('Server error');
            }
        })
        .catch(error => {
            document.getElementById('apiStatus').textContent = '离线 - 需要后端服务';
            document.getElementById('apiStatus').style.color = '#f5222d';
            showApiConfigWarning();
        });
}

// 显示 API 配置警告
function showApiConfigWarning() {
    const currentStatus = document.getElementById('apiStatus');
    if (currentStatus) {
        currentStatus.style.cursor = 'pointer';
        currentStatus.title = '点击重新配置 API 地址';
        currentStatus.onclick = function() {
            const newUrl = prompt('输入后端 API 地址：', API_BASE_URL);
            if (newUrl) {
                API_BASE_URL = newUrl;
                localStorage.setItem('apiUrl', newUrl);
                location.reload();
            }
        };
    }
}

// 上传简历
async function uploadResume() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        showStatus('uploadStatus', 'error', '请选择文件');
        return;
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showStatus('uploadStatus', 'error', '仅支持 PDF 格式文件');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showStatus('uploadStatus', 'loading', '上传中...');

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showStatus('uploadStatus', 'success', '上传成功！');
            currentResumeId = result.data.resume_id;
            displayUploadResult(result.data);
            document.getElementById('uploadResult').classList.remove('hidden');
            fileInput.value = '';
            
            // 刷新简历列表
            setTimeout(listResumes, 500);
        } else {
            showStatus('uploadStatus', 'error', `上传失败: ${result.message}`);
        }
    } catch (error) {
        console.error('上传错误:', error);
        showStatus('uploadStatus', 'error', `错误: ${error.message}`);
    }
}

// 显示上传结果
function displayUploadResult(data) {
    // 基本信息
    let baseInfoHtml = '';
    const baseInfo = data.base_info;
    if (baseInfo.name) baseInfoHtml += `<div class="info-item"><span class="info-label">姓名:</span><span class="info-value">${baseInfo.name}</span></div>`;
    if (baseInfo.phone) baseInfoHtml += `<div class="info-item"><span class="info-label">电话:</span><span class="info-value">${baseInfo.phone}</span></div>`;
    if (baseInfo.email) baseInfoHtml += `<div class="info-item"><span class="info-label">邮箱:</span><span class="info-value">${baseInfo.email}</span></div>`;
    if (baseInfo.address) baseInfoHtml += `<div class="info-item"><span class="info-label">地址:</span><span class="info-value">${baseInfo.address}</span></div>`;
    
    if (!baseInfoHtml) baseInfoHtml = '<p style="color: #999;">未识别到基本信息</p>';
    document.getElementById('baseInfo').innerHTML = baseInfoHtml;

    // 其他信息
    let optionalInfoHtml = '';
    const optionalInfo = data.optional_info;
    if (optionalInfo.job_intention) optionalInfoHtml += `<div class="info-item"><span class="info-label">求职意向:</span><span class="info-value">${optionalInfo.job_intention}</span></div>`;
    if (optionalInfo.work_experience_years) optionalInfoHtml += `<div class="info-item"><span class="info-label">工作年限:</span><span class="info-value">${optionalInfo.work_experience_years} 年</span></div>`;
    if (optionalInfo.education) optionalInfoHtml += `<div class="info-item"><span class="info-label">学历背景:</span><span class="info-value">${optionalInfo.education}</span></div>`;
    
    if (!optionalInfoHtml) optionalInfoHtml = '<p style="color: #999;">未识别到其他信息</p>';
    document.getElementById('optionalInfo').innerHTML = optionalInfoHtml;

    // 技能
    const skills = data.skills || [];
    const skillsHtml = skills.length > 0 
        ? skills.map(skill => `<span class="tag skill">${skill}</span>`).join('')
        : '<p style="color: #999;">未识别到技能</p>';
    document.getElementById('skills').innerHTML = skillsHtml;

    // 关键词
    const keywords = data.keywords || [];
    const keywordsHtml = keywords.length > 0
        ? keywords.map(keyword => `<span class="tag keyword">${keyword}</span>`).join('')
        : '<p style="color: #999;">未提取到关键词</p>';
    document.getElementById('keywords').innerHTML = keywordsHtml;

    // 简历 ID
    document.getElementById('resumeIdInfo').textContent = `简历 ID: ${currentResumeId}`;
}

// 简历匹配
async function matchResume() {
    const resumeSelect = document.getElementById('resumeSelect');
    const jobDescription = document.getElementById('jobDescription').value.trim();

    if (!resumeSelect.value) {
        showStatus('matchStatus', 'error', '请先选择简历');
        return;
    }

    if (!jobDescription) {
        showStatus('matchStatus', 'error', '请输入岗位描述');
        return;
    }

    showStatus('matchStatus', 'loading', '计算中...');

    try {
        const response = await fetch(`${API_BASE_URL}/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_id: resumeSelect.value,
                job_description: jobDescription
            })
        });

        const result = await response.json();

        if (result.success) {
            showStatus('matchStatus', 'success', '匹配成功！' + (result.from_cache ? '（从缓存读取）' : ''));
            displayMatchResult(result.data);
            document.getElementById('matchResult').classList.remove('hidden');
            
            if (result.from_cache) {
                document.getElementById('cacheInfo').textContent = '💾 此结果已缓存，下次计算会更快';
            } else {
                document.getElementById('cacheInfo').textContent = '已缓存此结果，下次查询会更快';
            }
        } else {
            showStatus('matchStatus', 'error', `匹配失败: ${result.message}`);
        }
    } catch (error) {
        console.error('匹配错误:', error);
        showStatus('matchStatus', 'error', `错误: ${error.message}`);
    }
}

// 显示匹配结果
function displayMatchResult(data) {
    document.getElementById('totalScore').textContent = data.total_score + '%';
    document.getElementById('skillMatch').textContent = data.skill_match + '%';
    document.getElementById('experienceMatch').textContent = data.experience_match + '%';
    document.getElementById('textSimilarity').textContent = data.text_similarity + '%';

    // 设置推荐颜色
    const recommendation = document.getElementById('recommendation');
    recommendation.textContent = data.recommendation;
    recommendation.className = 'recommendation';
    
    if (data.recommendation === '强烈推荐') {
        recommendation.classList.add('strong-recommended');
    } else if (data.recommendation === '推荐') {
        recommendation.classList.add('recommended');
    } else if (data.recommendation === '一般') {
        recommendation.classList.add('normal');
    } else {
        recommendation.classList.add('not-recommended');
    }

    // 匹配的技能
    const matchedSkills = data.matched_skills || [];
    const matchedSkillsHtml = matchedSkills.length > 0
        ? matchedSkills.map(skill => `<span class="tag skill">${skill}</span>`).join('')
        : '<p style="color: #999;">没有匹配的技能</p>';
    document.getElementById('matchedSkills').innerHTML = matchedSkillsHtml;

    // 岗位关键词
    const jobKeywords = data.job_keywords || [];
    const jobKeywordsHtml = jobKeywords.length > 0
        ? jobKeywords.map(keyword => `<span class="tag keyword">${keyword}</span>`).join('')
        : '<p style="color: #999;">未提取到关键词</p>';
    document.getElementById('jobKeywords').innerHTML = jobKeywordsHtml;
}

// 信息提取
async function extractInfo() {
    const text = document.getElementById('extractText').value.trim();

    if (!text) {
        showStatus('extractStatus', 'error', '请输入简历文本');
        return;
    }

    showStatus('extractStatus', 'loading', '提取中...');

    try {
        const response = await fetch(`${API_BASE_URL}/extract`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_text: text
            })
        });

        const result = await response.json();

        if (result.success) {
            showStatus('extractStatus', 'success', '提取成功！');
            displayExtractResult(result.data);
            document.getElementById('extractResult').classList.remove('hidden');
        } else {
            showStatus('extractStatus', 'error', `提取失败: ${result.message}`);
        }
    } catch (error) {
        console.error('提取错误:', error);
        showStatus('extractStatus', 'error', `错误: ${error.message}`);
    }
}

// 显示提取结果
function displayExtractResult(data) {
    // 基本信息
    let baseInfoHtml = '';
    const baseInfo = data.base_info;
    if (baseInfo.name) baseInfoHtml += `<div class="info-item"><span class="info-label">姓名:</span><span class="info-value">${baseInfo.name}</span></div>`;
    if (baseInfo.phone) baseInfoHtml += `<div class="info-item"><span class="info-label">电话:</span><span class="info-value">${baseInfo.phone}</span></div>`;
    if (baseInfo.email) baseInfoHtml += `<div class="info-item"><span class="info-label">邮箱:</span><span class="info-value">${baseInfo.email}</span></div>`;
    if (baseInfo.address) baseInfoHtml += `<div class="info-item"><span class="info-label">地址:</span><span class="info-value">${baseInfo.address}</span></div>`;
    
    if (!baseInfoHtml) baseInfoHtml = '<p style="color: #999;">未识别到基本信息</p>';
    document.getElementById('extractBaseInfo').innerHTML = baseInfoHtml;

    // 其他信息
    let optionalInfoHtml = '';
    const optionalInfo = data.optional_info;
    if (optionalInfo.job_intention) optionalInfoHtml += `<div class="info-item"><span class="info-label">求职意向:</span><span class="info-value">${optionalInfo.job_intention}</span></div>`;
    if (optionalInfo.work_experience_years) optionalInfoHtml += `<div class="info-item"><span class="info-label">工作年限:</span><span class="info-value">${optionalInfo.work_experience_years} 年</span></div>`;
    if (optionalInfo.education) optionalInfoHtml += `<div class="info-item"><span class="info-label">学历背景:</span><span class="info-value">${optionalInfo.education}</span></div>`;
    
    if (!optionalInfoHtml) optionalInfoHtml = '<p style="color: #999;">未识别到其他信息</p>';
    document.getElementById('extractOptionalInfo').innerHTML = optionalInfoHtml;

    // 技能
    const skills = data.skills || [];
    const skillsHtml = skills.length > 0
        ? skills.map(skill => `<span class="tag skill">${skill}</span>`).join('')
        : '<p style="color: #999;">未识别到技能</p>';
    document.getElementById('extractSkills').innerHTML = skillsHtml;

    // 关键词
    const keywords = data.keywords || [];
    const keywordsHtml = keywords.length > 0
        ? keywords.map(keyword => `<span class="tag keyword">${keyword}</span>`).join('')
        : '<p style="color: #999;">未提取到关键词</p>';
    document.getElementById('extractKeywords').innerHTML = keywordsHtml;
}

// 列出所有简历
async function listResumes() {
    try {
        const response = await fetch(`${API_BASE_URL}/resumes`);
        const result = await response.json();

        if (result.success) {
            const resumes = result.data;

            // 更新简历选择器
            const resumeSelect = document.getElementById('resumeSelect');
            resumeSelect.innerHTML = '<option value="">-- 选择简历 --</option>';
            resumes.forEach(resume => {
                const option = document.createElement('option');
                option.value = resume.resume_id;
                option.textContent = `${resume.candidate_name} - ${resume.filename}`;
                resumeSelect.appendChild(option);
            });

            // 更新简历列表
            if (resumes.length > 0) {
                const tableBody = document.getElementById('listBody');
                tableBody.innerHTML = resumes.map(resume => `
                    <tr>
                        <td><code>${resume.resume_id}</code></td>
                        <td>${resume.filename}</td>
                        <td>${resume.candidate_name}</td>
                        <td>${resume.candidate_email}</td>
                        <td>${new Date(resume.upload_time).toLocaleString('zh-CN')}</td>
                    </tr>
                `).join('');

                document.getElementById('resumeList').classList.remove('hidden');
                document.getElementById('emptyList').classList.add('hidden');
            } else {
                document.getElementById('resumeList').classList.add('hidden');
                document.getElementById('emptyList').classList.remove('hidden');
            }
        }
    } catch (error) {
        console.error('获取简历列表错误:', error);
    }
}

// 清空所有数据
async function clearData() {
    if (!confirm('确定要清空所有数据吗？此操作不可撤销！')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/clear`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            alert('数据已清空');
            listResumes();
            currentResumeId = null;
        }
    } catch (error) {
        console.error('清空数据错误:', error);
        alert('清空失败: ' + error.message);
    }
}

// 显示状态消息
function showStatus(elementId, type, message) {
    const element = document.getElementById(elementId);
    element.className = `status-message ${type}`;
    
    let icon = '';
    if (type === 'success') {
        icon = '✓ ';
    } else if (type === 'error') {
        icon = '✗ ';
    } else if (type === 'loading') {
        icon = '<span class="loading-spinner"></span> ';
    }

    element.innerHTML = icon + message;
    element.classList.remove('hidden');

    // 自动隐藏成功和错误消息
    if (type !== 'loading') {
        setTimeout(() => {
            element.classList.add('hidden');
        }, 3000);
    }
}
