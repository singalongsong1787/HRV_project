import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def extract_columns(
    excel_path: str,
    columns=("14_base", "14_up"),
    sheet_name=0,
    output_path=None
):
    """
    读取 Excel 文件并提取指定列。

    参数:
        excel_path (str): xlsx 文件路径。
        columns (tuple|list): 需要提取的列名序列。
        sheet_name (int|str): 需要读取的工作表，默认第一个工作表.
    返回:
        pd.DataFrame: 仅包含目标列的数据框。
    """
    excel_file = Path(excel_path)
    if not excel_file.is_file():
        raise FileNotFoundError(f"未找到文件: {excel_path}")

    # 读取
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # 检查列是否存在
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"下列列名不存在于工作表中: {missing}\n现有列: {list(df.columns)}")

    # 选取列
    result = df[list(columns)].copy()
    return result

plt.rcParams['font.sans-serif'] = ['SimHei']  # 优先使用的中文字体列表
plt.rcParams['axes.unicode_minus'] = False  # 解决负号（-）显示为方块的问题

if __name__ == "__main__":
    excel_path = 'D:\\研究生\\HR_trend_pro1\\result_R\\R_number.xlsx'
    base_data = extract_columns(excel_path, {"17_base"}).dropna()
    up_data = extract_columns(excel_path, {"17_up"}).dropna()
    print(base_data)
    print(up_data)

    # 生成原始横坐标（假设数据是按顺序采集的，索引从0开始）
    x_original = np.arange(len(base_data))  # 0,1,2,...,n-1
    x_scaled = x_original * 0.5  # 横坐标整体乘以0.5
    x_original_up = np.arange(len(up_data))
    x_scaled_up = x_original_up * 0.5

    plt.plot(x_scaled, base_data, label = "base夜晚心率")
    plt.plot(up_data, label = "up夜晚心率")
    plt.ylim(10, 50)
    plt.legend()
    plt.show()


