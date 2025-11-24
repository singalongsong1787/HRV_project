import pandas as pd
import numpy as np
import re


def process_heart_rate_data(file_path):
    # 1. 读取 Excel 文件
    # engine='openpyxl' 是读取 xlsx 的常用引擎
    df = pd.read_excel(file_path, engine='openpyxl')

    # 2. 初始化结果字典
    # 目标格式: { '14': ([base数据], [up数据]), ... }
    result_dict = {}

    # 临时字典用于匹配 base 和 up
    temp_group = {}

    # 3. 遍历所有列名
    for col_name in df.columns:
        # 使用正则表达式解析列名
        # 假设格式为 "数字_base" 或 "数字_up"
        # (\d+) 捕获数字ID, (base|up) 捕获类型
        match = re.match(r"(\d+)_(base|up)", str(col_name))

        if match:
            p_id = match.group(1)  # 例如 '14'
            p_type = match.group(2)  # 'base' 或 'up'

            # 提取数据并去除 NaN (空值)
            # values 返回 numpy 数组，tolist() 转为列表
            clean_data = df[col_name].dropna().tolist()

            # 初始化该ID的字典
            if p_id not in temp_group:
                temp_group[p_id] = {}

            # 存入对应类型的数据
            temp_group[p_id][p_type] = clean_data

    # 4. 组装最终结果，确保 base 和 up 成对出现
    for p_id, data_map in temp_group.items():
        if 'base' in data_map and 'up' in data_map:
            # 只有当两者都存在时才存入结果
            result_dict[p_id] = (data_map['base'], data_map['up'])
        else:
            print(f"警告: 实验者 {p_id} 数据不完整 (缺少 base 或 up)")

    return result_dict

def plot_figure(data1, data2, title)


if __name__ == "__main__":
    excel_filename = 'D:\\研究生\\HR_trend_pro1\\result_R\\R_number.xlsx'

    # 2. 处理数据
    try:
        final_data = process_heart_rate_data(excel_filename)

        # 3. 打印结果验证
        print("\n处理结果:")
        for pid, (base_data, up_data) in final_data.items():
            '''
            print(f"实验者 ID: {pid}")
            print(f"  Base ({len(base_data)}个): {base_data}")
            print(f"  Up   ({len(up_data)}个): {up_data}")
            print("-" * 30)
            '''

    except FileNotFoundError:
        print(f"错误: 找不到文件 {excel_filename}")



