# function:对整晚的睡眠数据进行分析，画出趋势图
# author:Zhangsong
# time: 2025-11-03-1842

import os
import mne
import pandas as pd
import matplotlib.pyplot as plt
from ecgdetectors import Detectors
import neurokit2 as nk
import numpy as np
from hrvanalysis  import get_time_domain_features, get_frequency_domain_features, get_poincare_plot_features
from hrvanalysis.preprocessing import (
    remove_outliers,
    remove_ectopic_beats,
    interpolate_nan_values
)

def compute_hrv_features(rr_intervals_ms):
    """清理 RR 间期并计算 HRV 特征"""
    # --- 清理 ---
    
    rr_clean = remove_outliers(rr_intervals_ms, low_rri=300, high_rri=2000)
    rr_clean = remove_ectopic_beats(rr_clean, method="kamath")
    rr_clean = interpolate_nan_values(rr_clean, interpolation_method="linear")

    print(f"rr_clean的数据类型为：{type(rr_clean)}")
    print(f"rr_clean的值为：{rr_clean}")


    # --- HRV 特征 ---
    features = {}
    features.update(get_time_domain_features(rr_intervals_ms))
    return features

def hrv_sliding_windows(ecg_data, sampling_rate, window_minutes=1,step_seconds=60):

    detectors = Detectors(sampling_rate)
    window_len = int(window_minutes * 60 * sampling_rate) #窗口大小
    step_len = int(step_seconds * sampling_rate) #步长大小
    n_windows = (len(ecg_data)-window_len) // step_len + 1 #窗口数量
    print(f"窗口数量: {n_windows}")

    results_time = [] #保存时域结果
    results_freq = [] #保存频域结果
    results_poincare = [] #保存poincare结果
    
    for w in range(n_windows):
        start = w * step_len
        end = start + window_len
        ecg_segment = ecg_data[start:end]


        '''
        #检测R峰
        rpeaks = detectors.pan_tompkins_detector(ecg_segment,MWA_name='cumulative')
        '''

        signals, info = nk.ecg_peaks(ecg_segment, sampling_rate=sampling_rate)
        rpeaks = info["ECG_R_Peaks"]

        '''画图检测R峰'''
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
        
        if len(rpeaks) < 2:
            print(f"窗口 {w}：R 峰太少，跳过")
            continue

        # 计算 RR 间期 (ms)
        rpeaks_times = np.array(rpeaks) / sampling_rate
        rr_intervals_ms = np.diff(rpeaks_times) * 1000

        #   ==== 计算 HRV 时域特征 ===
        features_time = compute_hrv_features(rr_intervals_ms)
        features_time["time"] = w 
        results_time.append(features_time)
       
        #   ==== 计算 HRV 频域特征 ===
        features_freq = get_frequency_domain_features(rr_intervals_ms)
        features_freq["time"] = w 
        results_freq.append(features_freq)

        #   ==== 计算 HRV Poincare 特征 ===
        features_poincare = get_poincare_plot_features(rr_intervals_ms)
        features_poincare["time"] = w
        results_poincare.append(features_poincare)

    #转DataFrame
    df_time = pd.DataFrame(results_time)
    df_freq = pd.DataFrame(results_freq)
    df_poincare = pd.DataFrame(results_poincare)
    #保存到Excel的不同sheet
    # -------- 保存到 Excel 的不同 sheet --------

    save_folder = "D:\\研究生\\project\\整晚心率分析\\result"
    os.makedirs(save_folder, exist_ok=True)  # 如果文件夹不存在则创建
    file_name = fileName(edf_file)
    save_path = os.path.join(save_folder, file_name)

    with pd.ExcelWriter(save_path) as writer:
        df_time.to_excel(writer, sheet_name="Time_Domain", index=False)
        df_freq.to_excel(writer, sheet_name="Frequency_Domain", index=False)
        df_poincare.to_excel(writer, sheet_name="Poincare_Domain", index=False)


    return pd.DataFrame(results_time)

def fileName(edf_file):
    base_name = os.path.splitext(os.path.basename(edf_file))[0]
    file_name = base_name + ".xlsx"
    return file_name


# 读取EDF文件
edf_file = "D:\\研究生\\project\\整晚心率分析\\SLP013_Day1.edf"
raw = mne.io.read_raw_edf(edf_file, preload=True)


# 获取所有通道数据 (data 是 numpy 数组, times 是时间轴)
data, times = raw[:]

#实验采样率
sampling_rate = raw.info['sfreq']
print(sampling_rate)
ecg_data = data[raw.ch_names.index('ECG'), :]

df_hrv = hrv_sliding_windows(ecg_data, sampling_rate, window_minutes=1,step_seconds=60)


