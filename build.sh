#!/bin/bash
# build.sh - 构建 JarvisAgent .app 打包文件
# 用法: bash build.sh

set -e

echo "🔨 正在构建 JarvisAgent.app..."

# 检查 pyinstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "📥 安装 pyinstaller..."
    pip install pyinstaller
fi

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf build dist *.spec

# 构建
echo "📦 执行 PyInstaller 构建..."
pyinstaller JarvisAgent.spec --noconfirm

# 检查结果
if [ -d "dist/JarvisAgent.app" ]; then
    echo ""
    echo "========================================"
    echo "  构建成功！✅"
    echo "  位置: dist/JarvisAgent.app"
    echo "========================================"
    echo ""
    echo "安装方式："
    echo "  1. 双击 dist/JarvisAgent.app 运行"
    echo "  2. 或复制到应用程序文件夹："
    echo "     cp -r dist/JarvisAgent.app /Applications/"
else
    echo "❌ 构建失败，请检查错误信息"
    exit 1
fi