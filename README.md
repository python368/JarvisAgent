JarvisAgent 项目白皮书 (2026 纯净版)
定位：专为 macOS 打造的轻量级、全能型 AGI 桌面助手。
使命：将复杂的 AI 技术封装进极简的原生体验，让每位 Mac 用户都拥有自己的“贾维斯”。

🌟 一、 项目愿景 (The Vision)
真正的“零门槛”：无需终端操作，无需配置环境，安装即用。

深耕 Apple 生态：利用 macOS 的底层能力（AppleScript, Swift 接口），做 Windows 助手做不到的深度控制。

1+4 动力矩阵：以本地模型保护隐私，以云端顶级模型（通过 OpenRouter）处理复杂逻辑。

🏗️ 二、 纯净版架构图 (System Architecture)
Plaintext
JarvisAgent/
├── app/          # 【感知层】原生 macOS 风格 UI，追求毛玻璃效果与极简交互
├── agent/        # 【决策层】Planner(规划) + Memory(记忆) + Router(调度)
├── tools/        # 【执行层】Mac 系统控制（键盘/鼠标/应用控制/文件操作）
├── services/     # 【扩展层】插件系统，连接天气、日历、提醒事项等服务
└── models/       # 【动力层】本地 Ollama 与 云端 API 的智能切换
🚦 三、 开发进度看板 (Status Dashboard)
✅ 已达成 (Milestones)
[x] 全模块解耦架构：代码结构已具备支撑复杂 AGI 逻辑的基础。

[x] 多引擎配置：完成 Google Gemini + OpenRouter 的高可用 API 矩阵。

[x] 基础 UI 交互：Zed 协作环境下已搭建起主窗口与侧边栏。

🚧 正在进行 (WIP)
[ ] Agent 逻辑闭环：让 AI 能够理解“帮我打开备忘录并记录...”这种复合指令。

[ ] macOS 视觉适配：去除原生窗口边框，实现符合 Apple 审美的圆角半透明界面。

[ ] Toolbox 开发：编写第一个真正能控制系统的工具 —— app_control.py。
