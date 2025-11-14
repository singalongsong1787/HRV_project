import os
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
from pathlib import Path


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


def hrv_sliding_windows(ecg_data, sampling_rate, window_minutes=1, step_seconds=60):
    detectors = Detectors(sampling_rate)
    window_len = int(window_minutes * 60 * sampling_rate)  # 窗口大小
    step_len = int(step_seconds * sampling_rate)  # 步长大小
    n_windows = (len(ecg_data) - window_len) // step_len + 1  # 窗口数量
    print(f"窗口数量: {n_windows}")

    results_time = []  # 保存时域结果
    results_freq = []  # 保存频域结果
    results_poincare = []  # 保存poincare结果

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

    # 转DataFrame
    df_time = pd.DataFrame(results_time)
    df_freq = pd.DataFrame(results_freq)
    df_poincare = pd.DataFrame(results_poincare)
    # 保存到Excel的不同sheet
    # -------- 保存到 Excel 的不同 sheet --------

    save_folder = "D:\\研究生\\HR_trend_pro1\\result_hrv"
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

def find_files(source_folder, prefix='SLP', suffix='.edf'):
    """
    在源文件夹及其子文件夹中查找符合特定前缀和后缀的文件。

    参数:
    source_folder (str): 要搜索的源文件夹的路径。
    prefix (str): 文件名应有的前缀，默认为 'SLP'。
    suffix (str): 文件名应有的后缀（文件扩展名），默认为 '.edf'。

    返回:
    list: 包含所有找到的文件完整路径的列表。
    """
    found_files_paths = []
    # os.walk() 会递归地遍历目录树
    for dirpath, _, filenames in os.walk(source_folder):
        for filename in filenames:
            # 检查文件名是否同时满足前缀和后缀条件
            if filename.startswith(prefix) and filename.endswith(suffix):
                # 构建文件的完整路径并添加到列表中
                full_path = os.path.join(dirpath, filename)
                found_files_paths.append(full_path)
    return found_files_paths

def file_exists_in_dir(filename: str, folder: str) -> bool:
    """
    判断文件名是否存在于指定文件夹（不搜索子文件夹）。

    参数:
        filename: 纯文件名，例如 'SLP01.edf'
        folder:   要检查的文件夹路径

    返回:
        True 如果该文件位于该文件夹中；否则 False
    """
    dir_path = Path(folder)
    if not dir_path.is_dir():
        return False
    return (dir_path / filename).is_file()


source_folder = "E:\\Auditory Sleep Stimulation Data\\3588_data"


edf_files = find_files(source_folder)
xlsx_folder = "D:\\研究生\\HR_trend_pro1\\result_hrv"
if edf_files:
    for edf_file in edf_files:
        print(f"正在处理文件{edf_file}")
        target_xlsx = fileName(edf_file)
        is_exists_xlsx = file_exists_in_dir(target_xlsx, xlsx_folder)
        if is_exists_xlsx == True:
            print("文件已经存在，无需处理")
            continue

        raw = mne.io.read_raw_edf(edf_file, preload=True)
        # 获取所有通道数据 (data 是 numpy 数组, times 是时间轴)
        data, times = raw[:]
        # 实验采样率
        sampling_rate = raw.info['sfreq']
        print(sampling_rate)
        ecg_data = data[raw.ch_names.index('ECG'), :]
        df_hrv = hrv_sliding_windows(ecg_data, sampling_rate, window_minutes=1, step_seconds=60)
else:
    print("没有找到符合条件的文件。")
