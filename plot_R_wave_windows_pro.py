# functioin: 绘制R波，验证识别准确性（不是画整个夜晚的识别结果，而是输入相应的时间窗口，绘制该时间窗口内的R波）
# author: -ZhangSong
# time: 2025-11-08-0954

import pandas as pd
import os
import mne
import pandas as pd
import matplotlib.pyplot as plt
from ecgdetectors import Detectors
import neurokit2 as nk
import numpy as np
from matplotlib.widgets import Slider
from hrvanalysis  import get_time_domain_features, get_frequency_domain_features, get_poincare_plot_features
from hrvanalysis.preprocessing import (
    remove_outliers,
    remove_ectopic_beats,
    interpolate_nan_values
)
from scipy import signal

plt.rcParams['font.sans-serif'] = ['SimHei']  # 优先使用的中文字体列表
plt.rcParams['axes.unicode_minus'] = False  # 解决负号（-）显示为方块的问题

# ----------------------
# 1. 加载文件及初始化
# ----------------------
edf_file = "D:\\研究生\\project\\整晚心率分析\\SLP012_Day2_up\\23点54分\\SLP012_Day2.edf"
raw = mne.io.read_raw_edf(edf_file, preload=True)
# 获取所有通道数据 (data 是 numpy 数组, times 是时间轴)
data, times = raw[:]
#实验采样率
sampling_rate = raw.info['sfreq']
print(sampling_rate)
ecg_data = data[raw.ch_names.index('ECG'), :]

# ----------------------
# 2. 提取相关事件窗口的数据
# ----------------------

def get_ecg_window(ecg_data: np.ndarray, sampling_rate: float, win_index: int) -> np.ndarray:

    # 窗口长度（秒）
    window_duration_sec = 60
    # 窗口长度（采样点数）
    window_length_samples = int(window_duration_sec * sampling_rate)
    # 窗口起始点在整个数据中的索引
    start_index = win_index * window_length_samples
    
    # 窗口结束点（不包含）在整个数据中的索引
    end_index = start_index + window_length_samples
    
    # 检查索引是否越界
    if start_index >= len(ecg_data):
        print(f"⚠️ 警告: 窗口索引 {win_index} 超出数据范围。")
        return np.array([])
    
    # 提取窗口数据
    # 如果 end_index 超过了数据总长，则取到数据末尾
    win_ecg_data = ecg_data[start_index:min(end_index, len(ecg_data))]
    
    # 检查提取到的数据长度是否满足 1 分钟（除非是最后一个不完整的窗口）
    if len(win_ecg_data) < window_length_samples and end_index <= len(ecg_data):
        print(f"⚠️ 警告: 预期窗口长度为 {window_length_samples} 个点，但实际只提取了 {len(win_ecg_data)} 个点。")

    return win_ecg_data

win_index = 3
win_ecg_data = get_ecg_window(ecg_data, sampling_rate, win_index)

# ----------------------
# （补）. 对数据进行滤波操作
# ----------------------
# 设计参数
fs = 1000 # 采样频率 (Hz) - 根据你的实际数据调整
lowcut = 0.3  # 低频截止频率 (Hz)
highcut = 70  # 高频截止频率 (Hz)
order = 4  # 滤波器阶数
def design_bandpass_filter(lowcut, highcut, fs, order=4):
    '''
    设计IIR带通滤波器（Butterworth）,4阶
    
    参数:
        lowcut: 低频截止频率
        highcut: 高频截止频率
        fs: 采样频率
        order: 滤波器阶数
    
    返回:
        b, a: 滤波器系数
    '''
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a

def zero_phase_filter(data, b, a):
    """
    应用零相位IIR滤波
    
    参数:
        data: 输入信号
        b, a: 滤波器系数
    
    返回:
        filtered_data: 零相位滤波后的信号
    """
    # 使用filtfilt实现零相位滤波（前向-后向滤波）
    filtered_data = signal.filtfilt(b, a, data)
    return filtered_data

b, a = design_bandpass_filter(lowcut, highcut, fs, order)
# 应用零相位滤波
filtered_data = zero_phase_filter(win_ecg_data, b, a)


# ----------------------
# 3. 画出该数据窗口的R峰图
# ----------------------
'''
signals, info = nk.ecg_peaks(win_ecg_data, sampling_rate=sampling_rate)
rpeaks = info["ECG_R_Peaks"]
plt.figure(figsize=(15,4))
plt.plot(win_ecg_data, label="ECG")
plt.plot(rpeaks, win_ecg_data[rpeaks], "ro", label="R peaks")
plt.title("R peak detection")
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.legend()
plt.show()
'''

win_list = [187, 208, 227, 221]
for win_index in win_list:
    win_ecg_data = get_ecg_window(ecg_data, sampling_rate, win_index)
    # 应用零相位滤波
    filtered_data = zero_phase_filter(win_ecg_data, b, a)

    signals, info = nk.ecg_peaks(filtered_data, sampling_rate=sampling_rate)
    rpeaks = info["ECG_R_Peaks"]
    plt.figure(figsize=(15,4))
    plt.plot(filtered_data, label="ECG")
    plt.plot(rpeaks, filtered_data[rpeaks], "ro", label="R peaks")
    plt.title(f"R peak detection (Window {win_index})")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    #plt.legend()
    plt.show()

    # 输出心率，使用hrv库
    rpeaks_times = np.array(rpeaks) / sampling_rate
    rr_intervals_ms = np.diff(rpeaks_times) * 1000

    rr_clean = remove_outliers(rr_intervals_ms, low_rri=300, high_rri=2000)
    rr_clean = remove_ectopic_beats(rr_clean, method="kamath")
    rr_clean = interpolate_nan_values(rr_clean, interpolation_method="linear")

    time_domain_features = get_time_domain_features(rr_clean)
    heart_rate = time_domain_features['mean_hr']  # 平均心率（单位：bpm）
    print(f"Window {win_index}: Heart Rate = {heart_rate:.2f} bpm")





