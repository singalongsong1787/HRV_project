import pandas as pd
import yasa
import matplotlib.pyplot as plt


'''
m = 7  # 这里可以修改为需要的 slp0 序号
d = 2
n = 2  # 这里可以修改为需要的 expert 序号

# 读取睡眠数据
nd_1 = pd.read_csv(f"E:\\luna process\\label\\tutorial{d}\\sleep_day{d}_expert{n}_label\\SLP0{m:02d}_D{d}_E{n}.csv")
# nd_1 = pd.read_csv(f"E:\时相图\时相图\陈丽飞\AST166_Labels.csv")
'''

file_path = "D:\\研究生\\project\\整晚心率分析\\时相图分析\\result_csv\\Up_SLP012.csv"
nd_1 = pd.read_csv(file_path)

# 获取数据
final_list_1 = nd_1.iloc[:, 0]
n = 1
d = 2


# 创建图形和轴，设置为三行一列的布局
fig, axs = plt.subplots(1, 1, figsize=(9, 2), constrained_layout=True)

# 绘制每个睡眠曲线在不同的图上
if n ==1:
    yasa.plot_hypnogram(final_list_1, fill_color="plum", ax=axs)
    axs.set_title(f"Hypnogram for Day {d}")
elif n==2:
    yasa.plot_hypnogram(final_list_1, fill_color="white", ax=axs)
    # axs.set_title(f"Hypnogram for Day {d}")
elif n==3:
    yasa.plot_hypnogram(final_list_1, fill_color="palegreen", ax=axs)
    axs.set_title(f"Hypnogram for Day {d}")

plt.tight_layout(pad=0.1)
# plt.savefig(f"E:\\expert{n}_hypno\\SLP0{m:02d}_E{n}.png")
# 显示图形
plt.show()
# plt.savefig(f"E:\\sleep_Pic\\SVG\\ex\\D{d}\\SLP0{m:02d}_E{n}.svg", format="svg", bbox_inches='tight')
#
# # 保存为 PNG 格式
# plt.savefig(f"E:\\sleep_Pic\\SVG\\ex\\D{d}\\SLP0{m:02d}_E{n}.png")
