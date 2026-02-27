#!/usr/bin/env python
"""
为阿里云 Serverless 部署打包代码
"""
import os
import shutil
import zipfile
import sys
from pathlib import Path

def create_deployment_package():
    """创建部署包"""
    
    backend_dir = Path('backend')
    package_dir = Path('backend/package')
    
    print("🔨 开始创建部署包...")
    
    # 清理旧的包目录
    if package_dir.exists():
        print("   清理旧的包目录...")
        shutil.rmtree(package_dir)
    
    # 创建包目录
    package_dir.mkdir(parents=True)
    print(f"   ✓ 创建目录: {package_dir}")
    
    # 复制应用代码
    files_to_copy = [
        'app_serverless.py',
        'config.py',
        'requirements.txt',
    ]
    
    print("\n📋 复制应用代码...")
    for file in files_to_copy:
        src = backend_dir / file
        dst = package_dir / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"   ✓ {file}")
        else:
            print(f"   ⚠ {file} 不存在，跳过")
    
    # 重命名 app_serverless.py 为 app.py
    app_serverless = package_dir / 'app_serverless.py'
    app_file = package_dir / 'app.py'
    if app_serverless.exists():
        os.rename(app_serverless, app_file)
        print("   ✓ 重命名 app_serverless.py → app.py")
    
    # 复制 services 目录
    print("\n📚 复制核心服务...")
    src_services = backend_dir / 'services'
    dst_services = package_dir / 'services'
    if src_services.exists():
        shutil.copytree(src_services, dst_services)
        print(f"   ✓ services/")
    
    # 复制 utils 目录
    src_utils = backend_dir / 'utils'
    dst_utils = package_dir / 'utils'
    if src_utils.exists():
        shutil.copytree(src_utils, dst_utils)
        print(f"   ✓ utils/")
    
    # 安装 Python 依赖
    print("\n📦 安装 Python 依赖...")
    requirements = backend_dir / 'requirements.txt'
    if requirements.exists():
        cmd = f'pip install -q -r {requirements} -t {package_dir}'
        print(f"   运行: {cmd}")
        ret = os.system(cmd)
        if ret == 0:
            print("   ✓ 依赖安装完成")
        else:
            print("   ⚠ 依赖安装可能失败 (继续打包)")
    
    # 清理不必要的文件
    print("\n🧹 清理不必要的文件...")
    excludes = ['*.pyc', '__pycache__', '*.egg-info', '*.dist-info']
    for root, dirs, files in os.walk(package_dir):
        # 删除 __pycache__ 目录
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))
            dirs.remove('__pycache__')
        
        # 删除 .pyc 文件
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    print("   ✓ 清理完成")
    
    # 创建 ZIP 包
    print("\n📦 创建 ZIP 部署包...")
    zip_file = Path('resume-analyzer.zip')
    
    if zip_file.exists():
        zip_file.unlink()
    
    # 使用 Python zipfile 模块创建 ZIP（跨平台兼容）
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zf.write(file_path, arcname)
    
    zip_size = zip_file.stat().st_size / (1024 * 1024)  # MB
    print(f"   ✓ 创建完成: {zip_file} ({zip_size:.2f} MB)")
    
    # 总结
    print("\n" + "="*50)
    print("✅ 部署包创建完成！")
    print("="*50)
    print("\n📤 下一步：上传到阿里云函数计算")
    print(f"   1. ZIP 文件位置: {zip_file.absolute()}")
    print("   2. 访问: https://fc.console.aliyun.com/")
    print("   3. 创建函数 → 上传代码 → 选择此 ZIP 文件")
    print("   4. 设置环境变量和触发器")
    print("   5. 获取函数 URL 并更新前端配置")
    
    return zip_file


if __name__ == '__main__':
    try:
        zip_file = create_deployment_package()
        print("\n💾 部署包已准备就绪！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
