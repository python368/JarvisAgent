#!/bin/bash
# build.sh - Build JarvisAgent .app bundle for macOS
# Usage: ./build.sh

set -e

echo "🔨 正在构建 JarvisAgent..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check for macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  警告: 不是 macOS 系统，构建可能无法正常工作${NC}"
fi

# Check pyinstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "📥 安装 pyinstaller..."
    pip install pyinstaller
fi

# Clean old builds
echo "🧹 清理旧构建..."
rm -rf build dist

# Build
echo "📦 执行 PyInstaller 构建..."
pyinstaller JarvisAgent.spec --noconfirm --clean

# Check result
if [ -d "dist/JarvisAgent.app" ]; then
    APP_SIZE=$(du -sh dist/JarvisAgent.app | cut -f1)
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✅ 构建成功！${NC}"
    echo -e "${GREEN}  位置: dist/JarvisAgent.app${NC}"
    echo -e "${GREEN}  大小: $APP_SIZE${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "安装方式："
    echo "  1. 双击 dist/JarvisAgent.app 运行"
    echo ""
    echo "  2. 或复制到应用程序文件夹："
    echo "     cp -r dist/JarvisAgent.app /Applications/"
    echo ""
    echo "⚠️  首次运行需要授权辅助功能权限"
else
    echo -e "${RED}❌ 构建失败，请检查错误信息${NC}"
    exit 1
fi
