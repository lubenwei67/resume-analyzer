#!/usr/bin/env python3
"""
准备 GitHub Pages 部署
将前端文件复制到 docs 目录
"""

import os
import shutil
from pathlib import Path

def setup_github_pages():
    """为 GitHub Pages 部署准备文件"""
    
    # 获取项目根目录
    root_dir = Path(__file__).parent
    frontend_dir = root_dir / 'frontend'
    docs_dir = root_dir / 'docs'
    
    print("🚀 准备 GitHub Pages 部署...")
    
    # 创建 docs 目录
    if docs_dir.exists():
        print(f"  ⚠️  {docs_dir} 已存在，删除旧文件...")
        shutil.rmtree(docs_dir)
    
    print(f"  📁 创建 {docs_dir}...")
    docs_dir.mkdir(exist_ok=True)
    
    # 复制前端文件
    files_to_copy = ['index.html', 'config.html', 'style.css', 'script.js']
    
    for file in files_to_copy:
        src = frontend_dir / file
        dst = docs_dir / file
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ 复制 {file}")
        else:
            print(f"  ✗ 未找到 {file}")
    
    # 创建 .nojekyll 文件（防止 GitHub Pages 处理 CSS）
    nojekyll = docs_dir / '.nojekyll'
    nojekyll.touch()
    print(f"  ✓ 创建 .nojekyll")
    
    print("\n✅ 准备完成！")
    print("\n📝 下一步:")
    print("  1. git add docs/")
    print("  2. git commit -m '部署前端到 GitHub Pages'")
    print("  3. git push")
    print("\n🌍 应用将在以下地址可用:")
    print("  https://yourusername.github.io/resume-analyzer/")

if __name__ == '__main__':
    setup_github_pages()
