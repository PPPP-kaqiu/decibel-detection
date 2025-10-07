# Noise Monitor GUI

一个简洁的桌面应用，用于监测环境噪音分贝，当噪音超过预设阈值时自动播放警报音。

## ✨ 主要功能

- **实时噪音监控**: 使用麦克风实时捕获音频并计算环境分贝。
- **自定义警报音**: 用户可以随时录制个性化的声音作为警报提示音。
- **阈值触发警报**: 当监测到的分贝值超过设定的阈值时，自动播放录制好的警报音。
- **可视化界面**: 提供简单直观的图形用户界面，包含开始/停止监控和录制警报音的功能。
- **状态提示**: 清晰地向用户展示当前应用的状态（如：正在监控、空闲、未找到警报音等）。

## 🛠️ 技术栈

- **Python 3**: 核心开发语言。
- **Tkinter**: 用于构建图形用户界面的 Python 标准库。
- **SoundDevice** & **NumPy**: 用于录制音频和进行实时音频数据处理。
- **SoundFile**: 用于将录制的警报音保存为 `.wav` 文件。
- **PyInstaller**: 用于将 Python 脚本打包成独立的可执行应用程序。

## 🚀 快速开始

如果您想从源代码运行此项目，请按照以下步骤操作。

### 1. 先决条件

- Python 3.7+
- pip (Python 包管理器)

### 2. 安装步骤

1.  **克隆仓库**
    ```bash
    git clone [https://github.com/your_username/gui_monitor.git](https://github.com/your_username/gui_monitor.git)
    cd gui_monitor
    ```

2.  **创建并激活虚拟环境** (推荐)
    ```bash
    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **安装依赖项**
    首先，在项目根目录下创建一个 `requirements.txt` 文件，内容如下：
    ```
    sounddevice
    numpy
    soundfile
    ```
    然后运行以下命令进行安装：
    ```bash
    pip install -r requirements.txt
    ```

4.  **运行应用**
    ```bash
    python gui_monitor.py
    ```

## 🖥️ 如何使用

1.  **启动应用**: 直接运行 `gui_monitor.py` 或打包后的可执行文件。
2.  **录制警报音**:
    - 点击 **"录制警报音"** 按钮。
    - 程序将开始录制几秒钟的音频（时长在代码中定义）。
    - 录制完成后，音频将自动保存为 `alarm.wav` 文件。
3.  **开始监控**:
    - 点击 **"开始监控"** 按钮。
    - 如果程序检测到 `alarm.wav` 文件，状态将变为“正在监控...”。
    - 如果未找到 `alarm.wav`，程序会提示您先录制警报音。
4.  **停止监控**:
    - 点击 **"停止监控"** 按钮，程序将返回空闲状态。

## 📦 应用打包

本项目使用 PyInstaller 将 Python 脚本打包为单个可执行文件。

1.  确保 PyInstaller 已安装:
    ```bash
    pip install pyinstaller
    ```

2.  使用以下命令进行打包 (在项目根目录下执行):
    ```bash
    # --name: 应用名称
    # --windowed: 运行时不显示命令行终端（GUI应用必备）
    # --onefile: 打包为单个可执行文件
    # --icon: 为你的应用指定一个图标 (macOS用.icns, Windows用.ico)
    pyinstaller --name gui_monitor --windowed --onefile --icon=assets/icon.icns gui_monitor.py
    ```
    **注意**: 对于 macOS，`--onefile` 模式可能会与 `.app` 捆绑包的签名和权限产生冲突。如果遇到问题，推荐使用更稳定的目录模式（去掉 `--onefile` 参数）。

3.  打包完成后，可执行文件将出现在 `dist` 文件夹中。

## 📄 开源许可

本项目采用 MIT 许可证。详情请参阅 `LICENSE` 文件。

---