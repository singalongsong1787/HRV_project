# function: 统计刺激时刻的心率并进行画图，分析显著性
# author: Zhangsong
# time：2025-11-17

import pandas as pd
import re
import matplotlib.pyplot as plt
from scipy import stats

import pandas as pd
import re

def extract_hr_lists_from_excel(excel_path, sheet_name="firstWave"):
    """
    从 Excel 中读取列名如 '14_base'、'14_up'、'14_down' 的数据，
    并按编号整理成列表。

    返回：
        num_list, base_list, up_list, down_list
    """

    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # 匹配列名：例如 14_base
    pattern = r"(\d+)_(base|up|down)"

    tmp = {}  # { 14 : {"base": x, "up": y, "down": z} }

    for col in df.columns:
        match = re.match(pattern, col)
        if match:
            num = int(match.group(1))
            stim = match.group(2)
            mean_val = df[col].mean(skipna=True)

            if num not in tmp:
                tmp[num] = {}
            tmp[num][stim] = mean_val

    # 最终四个输出列表
    num_list = []
    base_list = []
    up_list = []
    down_list = []

    # 按编号排序输出
    for num in sorted(tmp.keys()):
        num_list.append(num)
        base_list.append(tmp[num].get("base"))
        up_list.append(tmp[num].get("up"))
        down_list.append(tmp[num].get("down"))

    return num_list, base_list, up_list, down_list



def remove_by_numbers(remove_nums, num_list, base_list, up_list, down_list):
    """
    remove_nums: 要删除的编号列表，例如 [14, 37]
    num_list, base_list, up_list, down_list: 四个列表（长度一致）
    返回：删除后的四个列表
    """

    # 新列表（过滤后保留的数据）
    new_num = []
    new_base = []
    new_up = []
    new_down = []

    for n, b, u, d in zip(num_list, base_list, up_list, down_list):
        if n not in remove_nums:
            new_num.append(n)
            new_base.append(b)
            new_up.append(u)
            new_down.append(d)

    return new_num, new_base, new_up, new_down


import matplotlib.pyplot as plt
import numpy as np


def plot_bar_with_error(data1, data2, title, label1="first", label2="second"):
    """
    data1, data2: 输入两个列表（如 base_list 和 up_list）
    label1, label2: 图中两组的名称
    """

    colors = ['#8AC4FF', '#FFB8B8']

    # 转为 numpy 数组
    d1 = np.array(data1)
    d2 = np.array(data2)

    # 计算均值
    mean1 = np.mean(d1)
    mean2 = np.mean(d2)
    print(mean1, mean2)

    # 计算标准差 (std) 或标准误差 (sem)
    sem1 = np.std(d1, ddof=1) / np.sqrt(len(d1))  # SEM
    sem2 = np.std(d2, ddof=1) / np.sqrt(len(d2))

    # 用于绘图
    means = [mean1, mean2]
    errors = [sem1, sem2]
    labels = [label1, label2]

    # 绘图
    plt.figure(figsize=(3, 3.5))
    x = np.arange(2)

    plt.bar(x, means, yerr=errors, color=colors, capsize=8, width=0.5)

    plt.xticks(x, labels)
    plt.ylabel("Mean Value ± SEM")
    plt.title("Group Comparison")
    plt.title(title)

    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


def plot_normal_check(data, bins=30, title="数据正态性检验（直方图+正态曲线）",
                      xlabel="数值", ylabel="密度", color='lightblue', curve_color='red'):
    """
    绘制数据的直方图并叠加理论正态分布曲线，验证数据是否近似符合正态分布

    参数:
    data: 待检验的一维数组（列表或numpy数组）
    bins: 直方图的分箱数，默认30
    title: 图表标题
    xlabel: x轴标签
    ylabel: y轴标签
    color: 直方图颜色
    curve_color: 正态曲线颜色
    """
    # 确保数据为numpy数组
    data = np.asarray(data)

    # 计算数据的均值和标准差（用于构建理论正态分布）
    mu = np.mean(data)
    sigma = np.std(data)

    # 创建画布
    plt.figure(figsize=(8, 5))

    # 绘制直方图（density=True使直方图面积和为1，与概率密度曲线匹配）
    n, bins, patches = plt.hist(data, bins=bins, density=True, alpha=0.7, color=color)

    # 生成理论正态分布的x值（覆盖数据均值±3倍标准差范围，保证曲线完整）
    x = np.linspace(mu - 3 * sigma, mu + 3 * sigma, 1000)

    # 绘制理论正态分布曲线
    plt.plot(x, stats.norm.pdf(x, loc=mu, scale=sigma), color=curve_color, linewidth=2, linestyle='--')

    # 添加标签和标题
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14)

    # 添加网格线（可选）
    plt.grid(alpha=0.3)

    # 显示图像
    plt.show()


# excel_path = "D:\\研究生\\project\\整晚心率分析\\result\\R_num\\R_number - 副本.xlsx"
'''
# 读取 Excel
df = pd.read_excel(excel_path,sheet_name="firstWave")
#df = pd.read_excel(excel_path, sheet_name="secondWave")

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
'''

sheet_name="firstWave"
sheet_name = "secondWave"

# 加载数据
excel_rmssd_path = "D:\\研究生\\HR_trend_pro1\\result_R\\RMSSD.xlsx"
num_list_r, base_list_r, up_list_r, down_list_r = extract_hr_lists_from_excel(
    excel_rmssd_path,
    sheet_name
)


excel_sdnn_path = "D:\\研究生\\HR_trend_pro1\\result_R\\SDNN.xlsx"
num_list_s, base_list_s, up_list_s, down_list_s = extract_hr_lists_from_excel(
    excel_sdnn_path,
    sheet_name
)

r_number__path = "D:\\研究生\\HR_trend_pro1\\result_R\\R_number.xlsx"
num_list_R, base_list_R, up_list_R, down_list_R = extract_hr_lists_from_excel(
    r_number__path,
    sheet_name
)

# 对数据进行剔除
'''
down的数据剔除

'''

remove_list = []
remove_list = [6, 11, 12, 28, 37, 8, 30, 21, 31, 23]
#remove_list = [6, 8, 11, 12, 28, 37, 29, 38]
#remove_list = [6, 29, 30, 37, 19, 21, 8]

num_list_s, base_list_s, up_list_s, down_list_s = remove_by_numbers(remove_list, num_list_s, base_list_s, up_list_s, down_list_s )
num_list_r, base_list_r, up_list_r, down_list_r= remove_by_numbers(remove_list, num_list_r, base_list_r, up_list_r, down_list_r)
num_list_R, base_list_R, up_list_R, down_list_R  = remove_by_numbers(remove_list, num_list_R, base_list_R, up_list_R, down_list_R)

#num_list_r, base_list_r, up_list_r, down_list_r = remove_by_numbers(remove_list, num_list_r, base_list_r, up_list_r, down_list_r )


if num_list_s == num_list_r == num_list_R:
    print("三个 num_list 完全相同")
else:
    print("三个 num_list 不相同")

print(len(num_list_s))

print(num_list_s)
print(num_list_r)
print(num_list_R)

print(base_list_r)
print(up_list_r)

'''
对down情况下进行分析，去除
36： down计算有问题
'''
# remove_list = []
# remove_list = [29, 36]
# remove_list = [11, 12, 19, 23, 26, 28, 37]
'''
11  12 28 37
8 29 20 
'''

'''
remove_list = [8, 11, 12, 28, 37, 29, 38, 20]
num_list, base_list, up_list, down_list = remove_by_numbers(remove_list, num_list, base_list, up_list, down_list)
'''

plt.figure(figsize=(10, 6))

# 绘图

# 第一组

plt.plot(num_list_R, base_list_R, marker='o', color='C0', label='Base R')
plt.plot(num_list_R, up_list_R,   marker='^', color='C0', linestyle='--', label='Up R')

plt.plot(num_list_R, base_list_r, marker='o', color='C1', label='Base r')
plt.plot(num_list_R, up_list_r,   marker='^', color='C1', linestyle='--', label='Up r')



plt.plot(num_list_R, base_list_s, marker='o', color='C2', label='Base s')
plt.plot(num_list_R, up_list_s,   marker='^', color='C2', linestyle='--', label='Up s')



'''
# 第二组（原始数据）
plt.plot(num_list_r, base_list_r, marker='s', linestyle='--', label='Base_r')
plt.plot(num_list_r, up_list_r, marker='d', linestyle='--', label='Up_r')
'''

# 坐标轴标签
plt.xlabel("Number (num_list)")
plt.ylabel("Mean Value")
plt.title("Base / down Mean Values by Number")

plt.xticks(num_list_r)

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()

'''
diff_data = [up_list[i] - base_list[i] for i in range(len(num_list))]
plot_normal_check(diff_data)
'''

# 转换为 Series，用 isna() 检测 nan，再用 index 取索引

import numpy as np
from scipy import stats



t_stat, p_value = stats.ttest_rel(base_list_R, up_list_R)
print(f"hrv的p值: {p_value:.4f}")

t_stat, p_value = stats.ttest_rel(base_list_r, up_list_r)
print(p_value)
print(f"RMSSD的p值: {p_value:.4f}")
t_stat, p_value = stats.ttest_rel(base_list_s, up_list_s)
print(f"SDNN的p值: {p_value:.4f}")
# t_stat, p_value = stats.wilcoxon(base_list, up_list)、

plot_bar_with_error(base_list_r, up_list_r, "RMSSD", "base", "up")
plot_bar_with_error(base_list_s, up_list_s, "SDNN", "base", "up")
plot_bar_with_error(base_list_R, up_list_R, "hrv", "base", "up")








