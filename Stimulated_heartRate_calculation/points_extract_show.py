# function: 提取ponits_marker，转换为一个字典（并非所有的pair都是两个，需要合并间隔非常短的）
# author: Zhangsong
# time: 2025-11-16(周日)-1122
import os
import json

def build_folder_file_dict(source_folder: str, target_filename: str) -> dict:
    """
    构建一个字典，键为源文件夹下的子文件夹名称，值为在这些子文件夹中找到的目标文件的路径。

    :param source_folder: 要搜索的源文件夹路径。
    :param target_filename: 要在子文件夹中搜索的目标文件名。
    :return: 一个以文件夹名为键，文件路径为值的字典。
    """
    result_dict = {}

    # 检查源文件夹是否存在
    if not os.path.isdir(source_folder):
        print(f"错误：源文件夹 '{source_folder}' 不存在或不是一个目录。")
        return result_dict

    # 遍历源文件夹下的第一级目录
    for folder_name in os.listdir(source_folder):

        if folder_name == "3588_data":
            continue

        folder_path = os.path.join(source_folder, folder_name)

        # 确保它是一个文件夹
        if os.path.isdir(folder_path):
            # 使用 os.walk() 递归地遍历文件夹和子文件夹
            for root, dirs, files in os.walk(folder_path):
                if target_filename in files:
                    # 找到了文件，构建完整路径并存入字典
                    file_path = os.path.join(root, target_filename)
                    result_dict[folder_name] = file_path
                    # 找到后即可停止对当前文件夹的搜索，继续下一个
                    break
            else:
                # 如果循环正常结束（没有break），说明没找到文件
                print(f"警告：在文件夹 '{folder_name}' 及其子文件夹中未找到文件 '{target_filename}'。")

    return result_dict

def extract_pairs(marker_path, start_label=12, end_label=15, encoding='utf-8'):
    """
    读取 marker 文件，提取 (start_label, end_label) 成对出现的时间戳。

    文件格式要求：每一行形如
        <time(float)>,<label(int)>
    例如：
        123.45,12
        128.90,15

    参数:
        marker_path : str
            文本文件路径
        start_label : int, 默认 12
            起始标签（先出现的）
        end_label   : int, 默认 15
            结束标签（跟随出现的）
        encoding    : str, 默认 'utf-8'
            文件编码

    返回:
        list[tuple[float, float]]
            形如 [(t_start, t_end), ...] 的列表
            若出现多个 start_label 连续而没有 end_label，只有遇到 end_label 才记录配对
    """
    pairs = []
    waiting_for = start_label
    current_start_time = None

    with open(marker_path, 'r', encoding=encoding) as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            try:
                time_str, label_str = line.split(',')
            except ValueError:
                # 行格式不正确，跳过
                continue
            try:
                time = float(time_str)
                label = int(label_str)
            except ValueError:
                # 数据类型不正确，跳过
                continue

            if waiting_for == start_label:
                if label == start_label:
                    current_start_time = time
                    waiting_for = end_label  # 转换状态：等待结束标签
            elif waiting_for == end_label:
                if label == end_label:
                    # 成对
                    pairs.append((current_start_time, time))
                    waiting_for = start_label  # 回到寻找新的起点

    return pairs

def merge_by_gap(pairs, gap_threshold):
    """当 (下一段开始 - 当前段结束) < gap_threshold 时合并"""
    if not pairs:
        return []
    pairs = sorted(pairs, key=lambda x: x[0])
    merged = []
    cur_start, cur_end = pairs[0]
    for s, e in pairs[1:]:
        gap = s - cur_end
        if gap < gap_threshold:
            cur_end = max(cur_end, e)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = s, e
    merged.append((cur_start, cur_end))
    return merged

def save_dict_to_json(data_dict: dict, file_path: str):
    """
    将字典保存到 JSON 文件中。

    :param data_dict: 要保存的字典。
    :param file_path: 保存文件的路径 (例如 'output.json')。
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data_dict, json_file, indent=4, ensure_ascii=False)
        print(f"字典已成功保存到: {file_path}")
    except Exception as e:
        print(f"保存文件时出错: {e}")




source_folder_path = 'E:\\Auditory Sleep Stimulation Data'
# 2. 设置要查找的目标文件名
target_file = 'points_mark.txt'
file_dictionary = build_folder_file_dict(source_folder_path, target_file)
print(file_dictionary)

pairs_dictionary = {}
for  key, i in file_dictionary.items():
    file_path = file_dictionary[key]
    pairs = extract_pairs(file_path)
    # 对pairs进行预处理
    threshold_min = 15* 60 * 1000;
    pairs_filter = merge_by_gap(pairs, threshold_min)
    pairs_dictionary[key] = pairs_filter


for key,value in pairs_dictionary.items():
    print(key,value)

output_path = 'D:\\JetBrains\PyCharm Community Edition 2019.2.4\\project\\SleepPic\\HRV_SleepStage(Zhangsong)\\Stimulated_heartRate_calculation\\pairs_path_1.json'
save_dict_to_json(pairs_dictionary, output_path)


