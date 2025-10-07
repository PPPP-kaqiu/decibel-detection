import sys
import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QSpinBox
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal, Qt
from PyQt6.QtGui import QFont

# --- 导入我们自己的录音库 ---
import record_sound_lib

# --- 配置参数 ---
SAMPLE_RATE = 44100
CHUNK_DURATION = 0.5
WARNING_SOUND_FILE = 'warning_sound.wav'
RECORD_DURATION = 2

# --- 后端音频处理线程 (与之前版本相同) ---
class MonitorWorker(QObject):
    db_updated = pyqtSignal(float)
    is_running = True
    
    def __init__(self, threshold, warning_sound_data):
        super().__init__()
        self.threshold = threshold
        self.warning_sound_data = warning_sound_data

    def run(self):
        last_play_time = 0
        while self.is_running:
            try:
                audio_chunk = sd.rec(int(CHUNK_DURATION * SAMPLE_RATE), 
                                    samplerate=SAMPLE_RATE, channels=1, dtype='float32')
                sd.wait()
                rms = np.sqrt(np.mean(audio_chunk**2))
                decibels = self._calculate_db(rms)
                self.db_updated.emit(decibels)

                if decibels > self.threshold and (time.time() - last_play_time > 2):
                    sd.play(self.warning_sound_data, SAMPLE_RATE)
                    sd.wait()
                    last_play_time = time.time()
            except Exception as e:
                print(f"音频线程出错: {e}")
                break

    def stop(self):
        self.is_running = False

    def _calculate_db(self, rms_value, max_possible_val=1.0):
        if rms_value < 1e-10: return -np.inf
        db = 20 * np.log10(rms_value / max_possible_val)
        calibration_offset = 85
        return db + calibration_offset

# --- 主窗口界面 (恢复了录音按钮，但调用库函数) ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("分贝噪音监视器")
        self.setGeometry(100, 100, 400, 300)

        self.thread = None
        self.worker = None

        # --- UI 组件 (恢复录音按钮) ---
        self.status_label = QLabel("状态: 待机")
        self.db_display = QLabel("0.00 dB")
        self.db_display.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.db_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.record_button = QPushButton("录制警示音")
        self.toggle_button = QPushButton("开始监听")
        
        self.threshold_label = QLabel("触发分贝阈值:")
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(30, 120)
        self.threshold_spinbox.setValue(50)
        self.threshold_spinbox.setSuffix(" dB")

        # --- 布局 (恢复录音按钮) ---
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(self.threshold_label)
        threshold_layout.addWidget(self.threshold_spinbox)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.status_label)
        main_layout.addStretch()
        main_layout.addWidget(self.db_display)
        main_layout.addStretch()
        main_layout.addLayout(threshold_layout)
        main_layout.addLayout(button_layout)
        self.setCentralWidget(central_widget)

        # --- 连接信号和槽 ---
        self.record_button.clicked.connect(self.record_warning_sound)
        self.toggle_button.clicked.connect(self.toggle_monitoring)
        self._check_sound_file_status()

    def _check_sound_file_status(self):
        if os.path.exists(WARNING_SOUND_FILE):
            self.status_label.setText(f"状态: 警示音 '{WARNING_SOUND_FILE}' 已就绪")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("状态: 未找到警示音，请先录制")
            self.status_label.setStyleSheet("color: red;")
            
    def record_warning_sound(self):
        """处理录制警示音的按钮点击事件"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("准备录制")
        msg_box.setText(f"即将开始录制，时长为 {RECORD_DURATION} 秒。\n请在点击 'OK' 后立即发出声音。")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        
        if msg_box.exec() == QMessageBox.StandardButton.Ok:
            self.status_label.setText("状态: 正在录音...")
            QApplication.processEvents()

            # --- 调用库函数来执行录音和保存 ---
            success = record_sound_lib.record_and_save_sound(
                filename=WARNING_SOUND_FILE,
                duration=RECORD_DURATION,
                samplerate=SAMPLE_RATE
            )
            
            if success:
                QMessageBox.information(self, "完成", f"警示音已成功保存到 '{WARNING_SOUND_FILE}'")
            else:
                QMessageBox.critical(self, "错误", "录制或保存警示音失败，请查看终端输出。")
            
            self._check_sound_file_status()

    def toggle_monitoring(self):
        if self.thread is not None and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.thread = None
            self.toggle_button.setText("开始监听")
            self.record_button.setEnabled(True)
            self.threshold_spinbox.setEnabled(True)
        else:
            if not os.path.exists(WARNING_SOUND_FILE):
                QMessageBox.warning(self, "操作失败", "未找到警示音文件。\n请先点击 '录制警示音' 按钮进行录制。")
                return
            warning_sound_data, _ = sf.read(WARNING_SOUND_FILE, dtype='float32')
            current_threshold = self.threshold_spinbox.value()
            self.thread = QThread()
            self.worker = MonitorWorker(threshold=current_threshold, warning_sound_data=warning_sound_data)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.db_updated.connect(self.update_db_display)
            self.thread.start()
            self.toggle_button.setText("停止监听")
            self.record_button.setEnabled(False)
            self.threshold_spinbox.setEnabled(False)

    def update_db_display(self, db_value):
        self.db_display.setText(f"{db_value:.2f} dB")
        if db_value > self.threshold_spinbox.value():
            self.db_display.setStyleSheet("color: red;")
        else:
            self.db_display.setStyleSheet("color: black;")
            
    def closeEvent(self, event):
        if self.thread is not None and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        event.accept()

# --- 程序入口 ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())