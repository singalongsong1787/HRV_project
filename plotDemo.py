import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

xlsx_file = "D:\\研究生\\HR_trend_pro1\\result_hrv\\SLP012_Day2.xlsx"
# 读取 Excel 文件
df = pd.read_excel(xlsx_file)  # 替换为你的文件路径
hr_column = df['mean_hr']
hr_column = hr_column.rolling(window=5, center=True).median()

plt.plot(hr_column)
plt.title("HR")
plt.xlabel("Time (min)")
plt.ylabel("HR (bpm)")
plt.show()
