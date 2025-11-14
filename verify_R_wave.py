'''
author: Zhangsong
time: 2025-09-30
function: 验证R波检测是否准确
'''

import plotly.express as px
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
import plotly.graph_objects as go

import ipywidgets as widgets
from IPython.display import display

plt.rcParams['font.sans-serif'] = ['SimHei']  # 优先使用的中文字体列表
plt.rcParams['axes.unicode_minus'] = False  # 解决负号（-）显示为方块的问题

# 读取EDF文件
edf_file = "D:\\研究生\\project\\整晚心率分析\\SLP013_Day1.edf"
#edf_file = "D:\\研究生\\project\\整晚心率分析\\SLP012_Day2_up\\23点54分\\SLP012_Day2.edf"
raw = mne.io.read_raw_edf(edf_file, preload=True)

# 打印文件信息
print(raw.info)

# 获取所有通道数据 (data 是 numpy 数组, times 是时间轴)
data, times = raw[:]

#实验采样率
sampling_rate = raw.info['sfreq']

#提取心电数据
ecg_data = data[raw.ch_names.index('ECG'), :]
ecg_segment = ecg_data[:int(sampling_rate * 60)] #去前60s数据
# 移除 RR 间期数据中的异常值（离群点）
ecg_cleaned = nk.ecg_clean(ecg_data, sampling_rate=sampling_rate)

signals, info = nk.ecg_peaks(ecg_cleaned, sampling_rate=sampling_rate)
rpeaks = info["ECG_R_Peaks"]

'''画图'''
'''
plt.figure(figsize=(15,4))
plt.plot(ecg_segment, label="ECG")
plt.plot(rpeaks, ecg_segment[rpeaks], "ro", label="R peaks")
plt.title("R peak detection")
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.legend()
plt.show()
'''


# 转换为时间轴（秒）
time = np.arange(0, len(ecg_data)) / sampling_rate

# 设置滑动窗口大小（秒）
window_duration = 60  # 每次显示10秒数据
window_size = int(window_duration * sampling_rate)  # 转换为样本数

# 创建图形和轴
fig, ax = plt.subplots(figsize=(12, 6))
plt.subplots_adjust(bottom=0.2)  # 底部留出空间放滑块

# 初始窗口数据
initial_start = 0
initial_end = min(window_size, len(ecg_data))

# 绘制ECG信号
line, = ax.plot(time[initial_start:initial_end], ecg_data[initial_start:initial_end], 
                color='blue', linewidth=0.8, label='ECG Signal')

# 标记初始窗口内的R波峰值
initial_rpeaks = rpeaks[(rpeaks >= initial_start) & (rpeaks < initial_end)]
ax.scatter(time[initial_rpeaks], ecg_data[initial_rpeaks], 
           color='red', s=50, zorder=3, label='R Peaks')

# 设置图表属性
ax.set_title('ECG Signal with R Peaks (滑动窗口查看)')
ax.set_ylabel('Amplitude')
ax.set_xlabel('Time (s)')
ax.set_xlim(time[initial_start], time[initial_end-1])
ax.grid(True, alpha=0.3)
#ax.legend()

# 添加滑动条
ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])  # 位置和大小 [left, bottom, width, height]
max_pos = len(ecg_data) - window_size
slider = Slider(ax_slider, 'Time Position', 0, max_pos/sampling_rate, 
                valinit=0, valstep=0.5)  # 步长0.5秒

# 更新函数：当滑动条移动时更新图表
def update(val):
    # 获取滑动条位置（秒）并转换为样本索引
    start_sec = slider.val
    start_idx = int(start_sec * sampling_rate)
    end_idx = start_idx + window_size
    
    # 确保不超过数据范围
    if end_idx > len(ecg_data):
        end_idx = len(ecg_data)
        start_idx = end_idx - window_size
    
    # 更新ECG曲线数据
    line.set_xdata(time[start_idx:end_idx])
    line.set_ydata(ecg_data[start_idx:end_idx])
    
    # 清除之前的R波标记
    for artist in ax.collections:
        artist.remove()
    
    # 标记当前窗口内的R波
    current_rpeaks = rpeaks[(rpeaks >= start_idx) & (rpeaks < end_idx)]
    ax.scatter(time[current_rpeaks], ecg_data[current_rpeaks],
               color='red', s=50, zorder=3, label='R Peaks')
    
    # 更新x轴范围
    ax.set_xlim(time[start_idx], time[end_idx-1])
    fig.canvas.draw_idle()

# 绑定滑动条事件
slider.on_changed(update)

plt.show()
