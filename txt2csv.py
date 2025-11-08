import os
import csv

# 定义文件夹路径
input_folder_path = 'D:\\研究生\\project\\整晚心率分析\\睡眠分期标签txt\\睡眠分期标签txt'
output_folder_path = 'D:\\研究生\\project\\整晚心率分析\\时相图分析\\result_csv'

# 定义映射字典
mapping = {
    'Wake': 0,
    'NonREM1': 1,
    'NonREM2': 2,
    'NonREM3': 3,
    'REM': 4
}

# 遍历01到20的文件
for n in range(1, 21):
    # 格式化文件名为两位数
    input_file_name = f'Up_SLP0{n:02d}.txt'  # 使用 {n:02d} 格式
    input_file_path = os.path.join(input_folder_path, input_file_name)
    output_file_name = f'Up_SLP0{n:02d}.csv'
    output_file_path = os.path.join(output_folder_path, output_file_name)

    # 检查输入文件是否存在
    if os.path.exists(input_file_path):
        # 打开输入文件并读取内容
        output_data = []
        with open(input_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # 分割每一行，假设以制表符为分隔符
                columns = line.strip().split('\t')
                if len(columns) >= 3:  # 确保至少有三列
                    first_column_value = columns[0]
                    try:
                        start_time = float(columns[1])  # 第二列
                        end_time = float(columns[2])  # 第三列
                        total_time = end_time - start_time  # 计算总时间
                        n_count = int(total_time / 30)  # 计算次数n
                        # 将标签增加n_count个
                        output_data.extend([first_column_value] * n_count)
                    except ValueError:
                        # 如果转换失败，忽略该行
                        continue

        # 根据映射字典将标签映射为数字
        mapped_output = [mapping.get(label, -1) for label in output_data]  # 默认值为-1，表示未知状态

        # 将映射后的值写入新的CSV文件
        with open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
            writer = csv.writer(output_file)
            for mapped_value in mapped_output:
                writer.writerow([mapped_value])  # 每个映射值单独一行

        print(f"处理后的数据已保存到 {output_file_path}")
    else:
        print(f"输入文件 {input_file_path} 不存在，跳过。")
