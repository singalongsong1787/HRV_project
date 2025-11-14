# function: 绘制睡眠分期与心率的对应时刻图
# author: Zhangsong
# time: 2025-11-06

## time:2025-11-04-1420
# 将刺激时刻标签画在心率图上，刺激标签为14
## time: 2025-11-04-2053
# 将刺激时刻的阴影画出来

import pandas as pd
import matplotlib.pyplot as plt
import yasa

plt.rcParams['font.sans-serif'] = ['SimHei']  # 优先使用的中文字体列表
plt.rcParams['axes.unicode_minus'] = False  # 解决负号（-）显示为方块的问题

# ----------------------
# pre1: 提取刺激时刻的标签，提取开始12和结束15的时刻
markers_path = "E:\\Auditory Sleep Stimulation Data\\3588_data\\SLP014_Day2_up\\23点31分\\points_mark.txt"
pairs = []  # 用于保存 (12_time, 15_time)
waiting_for = 12  # 初始状态：先寻找 12
current_12_time = None

with open(markers_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        time_str, label_str = line.split(',')
        time = float(time_str)
        label = int(label_str)

        # 状态机逻辑
        if waiting_for == 12:
            if label == 12:
                current_12_time = time
                waiting_for = 15  # 找到12后，下一步找15

        elif waiting_for == 15:
            if label == 15:
                pairs.append((current_12_time, time))
                waiting_for = 12  # 成对结束，再找下一个12

print(pairs)

pairs = [(start / 1000 / 60 / 60, end / 1000 / 60 / 60) for start, end in pairs]
# ----------------------


# ----------------------
# 1. 读取睡眠分期数据（30秒/点）
# ----------------------
sleep_file = "D:\\研究生\\HR_trend_pro1\\result_csv\\Up_SLP014.csv"
nd_1 = pd.read_csv(sleep_file)
final_list_1 = nd_1.iloc[:, 0]  # 睡眠分期数据（0=清醒、1=浅睡等）

# 计算睡眠数据总时长（小时）：每个点30秒=0.5分钟=1/120小时
sleep_total_hours = len(final_list_1) * 0.5 / 60  # 转换为小时

# ----------------------
# 2. 读取心率数据（1分钟/点）
# ----------------------
hr_file = "D:\\研究生\\HR_trend_pro1\\result_hrv\\SLP014_Day2_up.xlsx"
df_hr = pd.read_excel(hr_file)
hr_data = df_hr['mean_hr'].rolling(window=5, center=True).median()  # 平滑后的心率
hr_data = df_hr['mean_hr']  #原始心率数据

# 心率时间轴转换为“小时”：1分钟=1/60小时，第i个点对应 i/60 小时
hr_time_hours = [i / 60 for i in range(len(hr_data))]  # 单位：小时

# ----------------------
# 3. 创建共享x轴的图（单位：小时）
# ----------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)  # 共享x轴（小时）

# 绘制睡眠分期图（上半部分）
yasa.plot_hypnogram(final_list_1, fill_color="plum", ax=ax1)
ax1.set_title("睡眠分期与心率趋势（时间单位：小时）")
ax1.set_ylabel("睡眠阶段")
# 强制睡眠图的x轴标签为小时（yasa默认可能已为小时，这里确认）
ax1.set_xlabel("")  # 暂时隐藏，避免与下方重复

# 绘制心率图（下半部分，时间轴已转换为小时）
ax2.plot(hr_time_hours, hr_data, color='blue')
ax2.set_xlabel("时间（小时）")  # 统一单位为小时
ax2.set_ylabel("心率（bpm）")
ax2.grid(alpha=0.3)

# 添加刺激时刻阴影和标注
for start, end in pairs:
    # 绘制阴影区域表示刺激时间段
    ax2.axvspan(start, end, color='lightcoral', alpha=0.3, label='刺激时段' if pairs.index((start, end)) == 0 else "")
    # 标注刺激开始和结束点
    ax2.axvline(x=start, color='red', linestyle='--', alpha=0.7)
    ax2.axvline(x=end, color='red', linestyle='--', alpha=0.7)

ax2.legend(loc='upper right')

# 对齐时间范围：取两者中较短的时长作为x轴上限
max_hours = min(sleep_total_hours, len(hr_data) / 60)  # 心率总时长=点数/60小时
ax2.set_xlim(0, max_hours)  # 确保两者时间范围一致

plt.tight_layout()
plt.show()