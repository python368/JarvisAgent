# Jarvis Agent V2

An elite, autonomous AI agent for computer control, built with PyQt6 and supporting multiple LLM providers.

## 🎯 Core Mission

Jarvis is designed to use AI to operate computers like a human:
- **Observe** the screen through vision models
- **Understand** current computer state
- **Think** about goals and plan actions
- **Execute** mouse and keyboard controls
- **Complete** real-world computer tasks autonomously

## ✨ Features

### Multi-Provider LLM Support
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **Google**: Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama**: Run open-source models locally (Llama, Mistral, etc.)

### Computer Control Tools
- **Screenshot**: Full screen and region capture
- **Mouse**: Move, click, scroll, drag operations
- **Keyboard**: Typing, hotkeys, special key presses
- **App Control**: Launch apps, switch windows, manage UI

### Agent Capabilities
- **Planning**: Task decomposition into executable steps
- **Memory**: Short-term conversation context + long-term persistent storage
- **Execution**: Action verification and retry mechanisms
- **Dialog**: Natural conversation management

### Modern UI
- Dark theme with glass-morphism effects
- Streaming AI responses
- Real-time status indicators
- Intuitive settings management

## 📁 Project Structure

```
JarvisAgent/
├── agent/              # Core agent logic
│   ├── agent.py        # Main ComputerAgent class
│   ├── planner.py      # Task planning
│   ├── task_manager.py # Task execution management
│   ├── dialog_manager.py # Conversation handling
│   └── memory.py       # Short and long-term memory
├── app/               # PyQt6 GUI
│   ├── main_window.py  # Main application window
│   ├── chat_widget.py  # Chat interface with streaming
│   ├── sidebar_widget.py # Navigation sidebar
│   └── settings_window.py # Configuration UI
├── models/             # LLM client implementations
│   ├── base_client.py  # Abstract interface
│   ├── openai_client.py
│   ├── anthropic_client.py
│   ├── ollama_client.py
│   ├── google_client.py
│   └── model_router.py # Provider routing
├── tools/              # Computer control tools
│   ├── screenshot.py   # Screen capture
│   ├── mouse.py       # Mouse control
│   ├── keyboard.py     # Keyboard control
│   ├── app_control.py  # Application management
│   └── file_manager.py # File operations
├── config/             # Configuration
│   └── app_config.py   # Settings management
├── tests/              # Test suite
├── main.py             # Application entry point
└── requirements.txt    # Dependencies
```

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/JarvisAgent.git
cd JarvisAgent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

1. **Launch the application**
2. **Open Settings** (⚙️ button in sidebar)
3. **Configure your LLM provider**:
   - For cloud providers (OpenAI, Anthropic, Google): Enter your API key
   - For Ollama: Ensure the server is running locally
4. **Select active provider** and model
5. **Save settings**

## 💻 Usage

### Basic Chat
1. Type your request in the chat input
2. Press Enter or click Send
3. Jarvis will respond and execute tasks

### Computer Control Tasks
Example tasks Jarvis can handle:
- "Open Safari and search for..."
- "Click the button in the top-right corner"
- "Create a new folder called Projects"
- "Open the settings and change the theme to dark"

### Provider Switching
Use Settings to switch between:
- **OpenAI**: Fast, reliable, good vision
- **Anthropic**: Excellent reasoning, long context
- **Google**: Free tier available, good performance
- **Ollama**: Privacy-focused, runs locally

## 🔨 Building for Distribution

```bash
# Install PyInstaller
pip install pyinstaller

# Build the application
pyinstaller JarvisAgent.spec

# The .app bundle will be in dist/JarvisAgent.app
```

## 📋 Requirements

- Python 3.10+
- PyQt6 6.6+
- Supported LLM providers or Ollama

## ⚠️ macOS Permissions

For full functionality, Jarvis needs:
- **Accessibility**: Required for mouse/keyboard control
- **Screen Recording**: Required for screenshots

Grant these in System Settings > Privacy & Security > Accessibility/Screen Recording

## 🧪 Testing

```bash
# Run test suite
python -m pytest tests/ -v
```

## 📄 License

MIT License - See LICENSE file for details

---

*Jarvis: Your AI-powered computer assistant* 🤖
