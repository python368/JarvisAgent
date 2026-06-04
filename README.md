# JarvisAgent V2

AI 计算机控制代理 for macOS - 开箱即用 🚀

## ⚡ 快速开始

### 方式一：一键安装（推荐）

```bash
# 下载项目后，在终端运行：
chmod +x install.sh
./install.sh
```

安装完成后，运行：
```bash
source venv/bin/activate
python main.py
```

### 方式二：手动安装

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py
```

### 方式三：打包应用安装

下载源码后构建 .app：
```bash
chmod +x build.sh
./build.sh
```

构建成功后，双击 `dist/JarvisAgent.app` 即可运行。

---

## ✨ 功能

### 🤖 AI 模型支持
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **Google**: Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama**: 本地运行开源模型（Llama, Mistral 等）

### 🖥️ 计算机控制
- 截图捕获
- 鼠标控制（移动、点击、滚动）
- 键盘控制（打字、快捷键）
- 应用启动和窗口管理

### 🎨 界面
- 深色主题
- 流式响应
- 现代化 UI

---

## 📋 依赖要求

- macOS 10.15+ (Apple Silicon 或 Intel)
- Python 3.10+

---

## ⚙️ 配置

首次运行后，在设置中配置你的 API Key：

1. 点击左侧 "⚙️ 设置"
2. 选择你的 AI 提供商
3. 输入 API Key
4. 保存

---

## 🔧 开发

```bash
# 开发模式安装
pip install -e .

# 运行测试
python -m pytest tests/ -v

# 构建 .app
./build.sh
```

---

## 📁 项目结构

```
JarvisAgent/
├── main.py              # 应用入口
├── requirements.txt     # 依赖列表
├── setup.py            # 安装配置
├── install.sh         # 一键安装脚本
├── build.sh           # 构建脚本
├── agent/              # AI 代理核心
├── app/               # PyQt6 GUI
├── models/             # LLM 客户端
├── tools/              # 计算机控制工具
├── config/            # 配置管理
└── tests/              # 测试套件
```

---

## ⚠️ 权限说明

macOS 需要以下权限才能正常工作：

| 权限 | 用途 | 授予位置 |
|------|------|----------|
| 辅助功能 | 鼠标/键盘控制 | 系统设置 > 隐私与安全 > 辅助功能 |
| 屏幕录制 | 截图功能 | 系统设置 > 隐私与安全 > 屏幕录制 |

---

## 🐛 故障排除

**Q: 提示 "无法打开，因为来自身份不明的开发者"**
A: 在 macOS 设置中允许：系统设置 > 隐私与安全 > 安全性 > 仍要打开

**Q: 截图不工作**
A: 确保已在系统设置中授予屏幕录制权限

**Q: 鼠标/键盘不响应**
A: 确保已在系统设置中授予辅助功能权限

---

MIT License - 2024 JarvisAgent
