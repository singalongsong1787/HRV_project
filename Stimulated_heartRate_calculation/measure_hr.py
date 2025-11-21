# function: 统计刺激时刻的心率并进行画图，分析显著性
# author: Zhangsong
# time：2025-11-17

import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
excel_path = "D:\\研究生\\HR_trend_pro1\\result_R\\R_number - 副本.xlsx"
# 读取 Excel
df = pd.read_excel(excel_path)

# 三个结果列表
base_list = []
up_list = []
down_list = []
num_list = []

# 解析列名，例如 "14_base"
pattern = r"(\d+)_(base|up|down)"

# 临时字典存储：{ 编号 : {type: mean} }
tmp = {}

for col in df.columns:
    match = re.match(pattern, col)
    if match:
        num = int(match.group(1))  # 例如 14
        stim = match.group(2)  # base / up / down

        mean_val = df[col].mean(skipna=True)

        if num not in tmp:
            tmp[num] = {}
        tmp[num][stim] = mean_val
print(tmp)

# 按编号排序，确保一一对应
for num in sorted(tmp.keys()):
    num_list.append(num)
    base_list.append(tmp[num].get("base"))
    up_list.append(tmp[num].get("up"))
    down_list.append(tmp[num].get("down"))

plt.figure(figsize=(10, 6))

# 绘图
plt.plot(num_list, base_list, marker='o', label='Base')
plt.plot(num_list, down_list, marker='s', label='Up')
# plt.plot(num_list, down_list, marker='^', label='Down')

# 坐标轴标签
plt.xlabel("Number (num_list)")
plt.ylabel("Mean Value")
plt.title("Base / Up  Mean Values by Number")

plt.xticks(num_list)

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()

#

def mean_and_std(lst):
    arr = np.array(lst, dtype=float)
    if arr.size == 0:
        return 0.0, 0.0
    mean = arr.mean()
    std = arr.std(ddof=1) if arr.size > 1 else 0.0  # ddof=1 用样本标准差；单样本时设为0
    return mean, std

mean_base, std_base = mean_and_std(base_list)
mean_up,   std_up   = mean_and_std(up_list)

means = np.array([mean_base, mean_up])
stds  = np.array([std_base, std_up])

x = np.arange(len(means))
labels = ['base', 'down']

fig, ax = plt.subplots(figsize=(6,4.5))

# 画条形（不使用 bar 的 yerr），用不同颜色区分
bars = ax.bar(x, means, color=['C0', 'C1'], alpha=0.85, width=0.5)

# 用 plt.errorbar 绘制误差棒（在条形顶端）
# fmt='none' 表示不绘制点，只绘制误差线
plt.errorbar(x, means, yerr=stds, fmt='none', ecolor='k', capsize=8, elinewidth=2)

# 在每个柱子上显示均值数字
y_offset = (stds.max() if stds.max() > 0 else means.max()*0.05)
for xi, m in zip(x, means):
    ax.text(xi, m + y_offset*0.1, f'{m:.3f}', ha='center', va='bottom', fontsize=10)

ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel('Mean value')
ax.set_title('Means with standard deviation (error bars via plt.errorbar)')
ax.yaxis.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.show()


t_stat, p_value = stats.ttest_rel(base_list, up_list)
print(p_value)



