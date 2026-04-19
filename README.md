# 🧠 JarvisAgent 项目说明（完整结构 + 目标 + 当前进度）

## 一、项目目标（Project Goal）

JarvisAgent 是一个运行在 macOS 上的本地 AI Agent 桌面应用，目标是实现类似 “Jarvis / AGI Assistant” 的能力：

* 🧠 使用多模型（本地 + API）进行智能决策
* 🖥️ 能像人一样操作电脑（应用控制、文件操作、输入设备）
* 💬 提供类似 ChatGPT / 豆包 的桌面交互体验
* 🧩 支持插件扩展（工具、服务）
* 🧠 具备短期记忆 + 长期记忆能力
* ⚙️ 可执行复杂任务（任务拆解 + 自动执行）

---

## 二、技术路线（Tech Stack）

* 语言：Python
* UI：PyQt6（原生桌面应用）
* 模型：

  * 本地模型：Ollama（主）
  * 可扩展：OpenAI / 其他 API
* 系统控制：

  * subprocess / AppleScript / 系统工具封装
* 架构风格：

  * 分层架构（UI / Agent / Tools / Models / Services）
  * 模块解耦（可扩展 AGI 架构）

---

## 三、项目整体架构（Project Structure）

```plaintext
JarvisAgent/
│
├── app/                       # UI 层（用户交互）
│   ├── main_window.py          # 主窗口（入口UI）
│   ├── chat_widget.py          # 聊天界面
│   ├── sidebar_widget.py       # 侧边栏（任务/工具）
│   ├── settings_window.py      # 设置界面
│   ├── model_selector.py       # 模型选择
│   ├── history_window.py       # 聊天历史
│   └── notifications.py        # 通知系统
│
├── agent/                     # Agent 核心（大脑）
│   ├── agent.py               # 主Agent调度
│   ├── planner.py             # 任务规划
│   ├── memory.py              # 统一记忆接口
│   ├── short_term_memory.py   # 短期记忆
│   ├── long_term_memory.py    # 长期记忆
│   ├── dialog_manager.py      # 对话管理
│   └── task_manager.py        # 任务执行管理
│
├── tools/                     # “手和脚”（系统操作能力）
│   ├── keyboard.py            # 键盘控制
│   ├── mouse.py               # 鼠标控制
│   ├── app_control.py         # 应用控制
│   ├── screenshot.py          # 截图
│   └── file_manager.py        # 文件操作
│
├── services/                  # 外部服务层
│   ├── agent_service.py       # Agent接口层
│   ├── plugin_service.py      # 插件系统
│   ├── notification_service.py
│   └── file_service.py
│
├── models/                    # 模型抽象层
│   ├── ollama_client.py       # 本地模型
│   ├── openai_client.py       # API模型
│   ├── model_router.py        # 多模型调度
│   └── model_cache.py         # 缓存
│
├── config/                    # 配置管理
│   ├── app_config.py
│   ├── agent_config.py
│   └── model_config.py
│
├── utils/                     # 通用工具
│   ├── logger.py
│   ├── helpers.py
│   ├── decorators.py
│   └── validators.py
│
├── tests/                     # 测试
│   ├── test_agent.py
│   ├── test_tools.py
│   ├── test_services.py
│   └── test_models.py
│
├── main.py                    # 应用入口（启动UI）
├── requirements.txt
└── README.md
```

---

## 四、系统运行流程（Core Flow）

### 1️⃣ 用户输入

UI（chat_widget）接收用户输入：

```
用户 → 输入文本
```

---

### 2️⃣ UI → Agent

```
ChatWidget → Agent
```

---

### 3️⃣ Agent 决策流程

```
Agent
 ├── DialogManager（理解上下文）
 ├── Planner（是否需要拆任务）
 ├── Memory（读取历史）
 ├── ModelRouter（选择模型）
```

---

### 4️⃣ 执行判断

Agent 判断：

* 💬 直接回答 → 模型生成
* 🛠️ 需要操作 → 调用 tools

---

### 5️⃣ Tools 执行（关键能力）

例如：

```
打开浏览器
→ app_control.py

创建文件
→ file_manager.py
```

---

### 6️⃣ 返回结果

```
Tools / Model → Agent → UI
```

---

## 五、当前开发进度（Current Status）

### ✅ 已完成

* ✔ 项目架构设计（完整）
* ✔ GitHub 仓库初始化
* ✔ UI 基础结构（主窗口 + 聊天 + 侧边栏）
* ✔ 本地运行环境搭建

---

### 🚧 进行中

* UI 功能完善（聊天体验）
* Agent 基础逻辑实现
* Ollama 接入

---

### ❌ 未完成（核心能力）

* 多模型调度（1+4架构）
* 记忆系统（短期 + 长期）
* Tools 实际控制（Mac操作）
* 自动任务执行（Planner）
* 插件系统

---

## 六、未来规划（Roadmap）

### 阶段 1（当前）

* UI完成
* 基础Agent可用

---

### 阶段 2（关键）

* 接入 Ollama
* 实现 Tools（控制电脑）
* 实现简单任务执行

---

### 阶段 3（进阶）

* 多模型（主模型 + 工具模型）
* Memory系统
* 自动任务链

---

### 阶段 4（AGI方向）

* 多Agent协作
* 自主决策
* 插件生态

---

## 七、项目定位总结

JarvisAgent ≠ 普通聊天机器人

它是：

👉 一个「本地运行的 AI 操作系统助手」
👉 一个「具备行动能力的智能 Agent」
👉 一个「向 AGI 演进的架构基础」

---

## 八、当前关键问题

* 本地模型性能受限（M1 + 8GB）
* Agent逻辑尚未打通
* Tools层尚未真正接入系统

---

## 九、下一步关键任务（最重要）

1. ChatWidget 接入 Agent
2. Agent 调用 Ollama
3. 实现第一个 Tool：
   👉 打开应用（Mac）

---

## 十、一句话总结

JarvisAgent 当前处于：

👉 “架构完成 + UI初步完成 + 即将进入核心能力开发阶段”
这是我现在的开发任务
