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

# --- 使用示例 ---

# 1. 设置您的源文件夹路径
#    请确保将 'path/to/your/source_folder' 替换为实际的路径
#    例如: '/home/user/documents/data' 或 'C:\\Users\\User\\Desktop\\data'
source_folder_path = 'E:\\Auditory Sleep Stimulation Data\\3588_data'

# 2. 设置要查找的目标文件名
target_file = 'points_mark.txt'

# 3. 调用函数并获取结果
file_dictionary = build_folder_file_dict(source_folder_path, target_file)
output_json_path = "D:\\JetBrains\\PyCharm Community Edition 2019.2.4\\project\\SleepPic\\HRV_SleepStage(Zhangsong)\\mark_path.json"

# 4. 打印生成的字典
if file_dictionary:
    print("成功构建字典：")
    for folder, path in file_dictionary.items():
        print(f"  '{folder}': '{path}'")
else:
    print("未能构建字典，请检查源文件夹路径和内容。")



# 5. 检查字典是否非空，然后保存它
if file_dictionary:
    print("\n成功构建字典：")
    for folder, path in file_dictionary.items():
        print(f"  '{folder}': '{path}'")

    print("\n正在保存字典...")
    save_dict_to_json(file_dictionary, output_json_path)
else:
    print("\n未能构建字典，请检查源文件夹路径和内容。")

# 示例输出（假设文件结构如您所述）:
# 成功构建字典：
#   'SLP031_Day1': 'path/to/your/source_folder/SLP031_Day1/subfolder/points_marks'
#   'SLP032_Day2': 'path/to/your/source_folder/SLP032_Day2/another_subfolder/points_marks'