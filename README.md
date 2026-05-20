# Jarvis: Autonomous Agentic Workspace

An elite, localized autonomous agentic workspace engineered for multi-provider LLM orchestration, fluid high-fidelity interactions, and professional-grade development environments. 

Developed and structured by the **Student Union (学联)**.

---

## 🛠️ Core Architecture

- **Host Environment**: Highly tailored and computationally optimized for Apple Silicon (M1 Architecture).
- **Core Engine**: Asynchronous dual-engine runtime built on PyQt6, delivering a hardware-accelerated fluid visual interface.
- **Provider Orchestration**: Dynamic, decoupled model switching layer seamlessly bridging Localized LLM instances (via Ollama) and hyperscale cloud providers (via custom API clients).
- **Design Language**: Hardcore industrial geometric aesthetics, featuring custom borderless windows, micro-shadow rendering, and fluid dark-mode transitions.

---

## 📂 Project Structure

```text
JarvisAgent/
├── app/                  # High-fidelity visual interface & GUI runtime
│   ├── main_window.py    # Primary agent workspace shell
│   ├── chat_widget.py    # Fluid message streaming engine
│   └── settings_window.py# Decoupled control and configuration interface
├── config/               # Secure persistence & schema definition
│   └── app_config.py     # Environment variable mappings & static states
├── models/               # Multi-vendor protocol translation layers
│   ├── model_router.py   # Adaptive provider routing matrix
│   └── openai_client.py  # High-throughput client implementation
└── main.py               # Absolute execution entrypoint