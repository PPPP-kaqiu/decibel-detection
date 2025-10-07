import sounddevice as sd
import soundfile as sf

def record_and_save_sound(filename, duration, samplerate):
    """
    执行录音并保存到文件的核心函数。

    参数:
        filename (str): 要保存到的文件名 (例如 'warning_sound.wav')。
        duration (int): 录音时长（秒）。
        samplerate (int): 采样率 (例如 44100)。

    返回:
        bool: 如果成功则返回 True, 否则返回 False。
    """
    try:
        print(f"库函数调用：开始录制 {duration} 秒音频...")
        
        # 录制音频
        recording = sd.rec(int(duration * samplerate), 
                           samplerate=samplerate, 
                           channels=1, 
                           dtype='float32')
        sd.wait()  # 等待录制完成
        
        # 保存到 .wav 文件
        sf.write(filename, recording, samplerate)
        
        print(f"库函数调用：音频成功保存到 {filename}")
        return True
        
    except Exception as e:
        print(f"错误：在录音或保存过程中发生异常: {e}")
        return False