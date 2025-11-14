import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import yasa
from typing import Optional

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


def convert_name(name):
    # 使用下划线分割名称为多个部分
    parts = name.split('_')
    #print(parts[1])

    # 检查是否有部分包含'Day'
    has_day = any('Day1' in part for part in parts)
    # 检查是否有部分为'up'
    has_up = any(part.lower() == 'up' for part in parts)

    if has_day:
        # 返回 Base_ 加上分割后的第一部分
        return f"Base_{parts[0]}"
    elif has_up:
        # 返回 Up_ 加上分割后的第一部分
        return f"Up_{parts[0]}"
    else:
        # 不满足两种情况则返回 None
        return None

def combine_path(a, b):
    # 拼接路径并添加.csv后缀
    return os.path.join(a, f"{b}.csv")

def load_dict_from_json(file_path: str) -> dict:
    """
    从 JSON 文件加载字典。

    :param file_path: JSON 文件的路径。
    :return: 加载后的字典，如果文件不存在或出错则返回空字典。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        print(f"字典已从 {file_path} 加载。")
        return data
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到。")
        return {}
    except json.JSONDecodeError:
        print(f"错误: 文件 '{file_path}' 不是有效的 JSON 格式。")
        return {}


def plot_sleep_hr_with_stimulation(markers_path: str, sleep_file: str, hr_file: str, title: Optional[str] = None):
    """
    读取并绘制睡眠分期、心率以及刺激标记的组合图。

    :param markers_path: 刺激标记文件（.txt）的路径。
                         文件格式应为: 时间戳(ms),标签 (例如: 12345,12)。
    :param sleep_file: 睡眠分期文件（.csv）的路径。
                       要求第一列为睡眠分期数据。
    :param hr_file: 心率数据文件（.xlsx）的路径。
                    要求包含名为 'mean_hr' 的列。
    :param title: 图像的自定义标题。如果为 None，则使用默认标题。
    """
    # -- 全局绘图设置 --
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    try:
        # ----------------------
        # pre1: 提取刺激时刻的标签
        # ----------------------
        pairs = []
        waiting_for = 12
        current_12_time = None

        with open(markers_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                time_str, label_str = line.split(',')
                time = float(time_str)
                label = int(label_str)

                if waiting_for == 12 and label == 12:
                    current_12_time = time
                    waiting_for = 15
                elif waiting_for == 15 and label == 15:
                    pairs.append((current_12_time, time))
                    waiting_for = 12

        # 将刺激时间从毫秒转换为小时
        pairs_hours = [(start / 3600000, end / 3600000) for start, end in pairs]

        # ----------------------
        # 1. 读取睡眠分期数据
        # ----------------------
        df_sleep = pd.read_csv(sleep_file)
        hypno_data = df_sleep.iloc[:, 0]
        sleep_total_hours = len(hypno_data) * 0.5 / 60

        # ----------------------
        # 2. 读取心率数据
        # ----------------------
        df_hr = pd.read_excel(hr_file)
        hr_data = df_hr['mean_hr']
        hr_time_hours = [i / 60 for i in range(len(hr_data))]

        # ----------------------
        # 3. 创建并绘制图形
        # ----------------------
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

        # 设置图表标题
        main_title = title if title else "睡眠分期与心率趋势（时间单位：小时）"
        ax1.set_title(main_title)

        # 绘制睡眠分期图
        yasa.plot_hypnogram(hypno_data, fill_color="plum", ax=ax1)
        ax1.set_ylabel("睡眠阶段")
        ax1.set_xlabel("")

        # 绘制心率图
        ax2.plot(hr_time_hours, hr_data, color='blue')
        ax2.set_xlabel("时间（小时）")
        ax2.set_ylabel("心率（bpm）")
        ax2.grid(alpha=0.3)

        # 添加刺激时刻阴影和标注
        for i, (start, end) in enumerate(pairs_hours):
            label = '刺激时段' if i == 0 else ""  # 仅为第一个阴影添加图例标签
            ax2.axvspan(start, end, color='lightcoral', alpha=0.3, label=label)
            ax2.axvline(x=start, color='red', linestyle='--', alpha=0.7)
            ax2.axvline(x=end, color='red', linestyle='--', alpha=0.7)

        if pairs_hours:  # 仅在有刺激时段时显示图例
            ax2.legend(loc='upper right')

        # 对齐时间范围
        max_hours = min(sleep_total_hours, len(hr_data) / 60)
        ax2.set_xlim(0, max_hours)

        plt.tight_layout()
        # plt.show()
        figure_folder = "D:\\研究生\\HR_trend_pro1\\result_figure"
        figname = title + '.png'
        figure_path = os.path.join(figure_folder, figname)
        plt.savefig(figure_path)
        plt.close(fig)

    except FileNotFoundError as e:
        print(f"错误：文件未找到。请检查路径是否正确。\n详细信息: {e}")
    except Exception as e:
        print(f"处理过程中发生错误：\n{e}")

# 读取xlsx文件
source_foler = "D:\\研究生\\HR_trend_pro1\\result_hrv"
xlxs_pahts = find_files(source_foler, 'SLP', '.xlsx')
csv_folder = "D:\\研究生\\HR_trend_pro1\\result_csv"
output_json_path = "D:\\JetBrains\\PyCharm Community Edition 2019.2.4\\project\\SleepPic\\HRV_SleepStage(Zhangsong)\\mark_path.json"

# test:加载json数据
loaded_dictionary = load_dict_from_json(output_json_path)
if loaded_dictionary:
    print("加载的字典内容:")
    print(loaded_dictionary)

for xlsx_p in xlxs_pahts:
    ##### 读取睡眠标签文件.csv
    # 去掉名称
    xlsx_name = os.path.basename(xlsx_p)
    xlsx_name,_ = os.path.splitext(xlsx_name)
    csv_name = convert_name(xlsx_name)
    csv_path = combine_path(csv_folder, csv_name)
    ##### 读取points_marker文件
    marker_path = loaded_dictionary.get(xlsx_name)
    print(marker_path)

    ### 画图
    if marker_path == "None":
        continue

    plot_sleep_hr_with_stimulation(marker_path, csv_path, xlsx_p, csv_name)




