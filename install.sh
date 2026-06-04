#!/bin/bash
# install.sh - 一键安装 JarvisAgent
# 用法: bash install.sh

set -e

echo "🚀 正在安装 JarvisAgent..."

# 检测 macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ 检测到 macOS 系统"
    
    # 检查 Python 版本
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    if [[ $(echo "$PYTHON_VERSION < 3.10" | bc -l) -eq 1 ]]; then
        echo "❌ 需要 Python 3.10 或更高版本，当前: $PYTHON_VERSION"
        echo "请从 https://www.python.org/downloads/mac-osx/ 安装"
        exit 1
    fi
    
    # 检查 Homebrew (推荐)
    if ! command -v brew &> /dev/null; then
        echo "⚠️  建议安装 Homebrew: https://brew.sh"
    fi
    
    # 创建虚拟环境 (推荐)
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    
    # 激活虚拟环境
    source venv/bin/activate
    
    echo "📥 安装依赖包..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ 安装完成！"
    echo ""
    echo "启动方式："
    echo "  source venv/bin/activate"
    echo "  python main.py"
    echo ""
    echo "或者双击运行 dist/JarvisAgent.app (如已构建)"
    
else
    echo "⚠️  警告: JarvisAgent 专为 macOS 设计"
    echo "检测到系统: $OSTYPE"
    echo ""
    
    # 仍然尝试安装 (用户可能有交叉开发需求)
    echo "📥 继续安装依赖..."
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        echo "❌ 需要 pip3，请安装 Python 3.10+"
        exit 1
    fi
    
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    
    echo "✅ 安装完成！"
    echo ""
    echo "启动方式："
    echo "  python3 main.py"
fi

echo ""
echo "========================================"
echo "  JarvisAgent 安装完成！🎉"
echo "========================================"