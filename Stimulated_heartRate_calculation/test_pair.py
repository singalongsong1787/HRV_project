import pandas as pd
import matplotlib.pyplot as plt
import yasa

plt.rcParams['font.sans-serif'] = ['SimHei']  # 优先使用的中文字体列表
plt.rcParams['axes.unicode_minus'] = False  # 解决负号（-）显示为方块的问题


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
