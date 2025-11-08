# function: 从文件中提取标签（算法开启时刻：第一个12；关闭时刻:第一个15）
# author: Zhangsong
# time: 2025-11-07

markers_path = "D:\\研究生\\project\\整晚心率分析\\SLP012_Day2_up\\23点54分\\points_mark.txt"

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

pairs = [(start/1000/60/60, end/1000/60/60) for start, end in pairs]

print("成对的 (12_time, 15_time) ：")
for p in pairs:
    print(p)

    
    