# 任务 2：日志分析脚本
# （E3)
# 目标：
#     从 log 文件中提取所有 IP 地址，统计出现频率。
# 常见 log 示例行：
#     2023-07-21 10:00:01 - INFO - Connection from 192.168.1.15 port 443
#     2023-07-21 10:00:05 - ERROR - Connection timeout from 10.0.0.2
# 功能要求
#     从文件中提取所有 IPv4
#     用正则表达式（工程必备）
#     提供异常处理
#     输出统计结果到一个新文件（如 ip_report.txt）

import re
from collections import Counter

IP_PATTERN = r"(?:\d{1,3}\.){3}\d{1,3}"

#统计IP数量函数
def extract_ips(log_file:str) -> Counter:
    try:
        with open(log_file, "r", encoding = "utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Log file not found!")
        return Counter()

    ips = re.findall(IP_PATTERN, text)
    return Counter(ips)

#保存统计的数据到新的文件中
def save_report(counter: Counter, output_file: str):
    try:
        with open(output_file, "w", encoding = "utf-8") as f:
            for ip, count in counter.items():
                f.write(f"{ip} : {count}\n")
    except Exception as e:
        print("Error writing report:", e)

if __name__ == "__main__":
    counters = extract_ips("access.log")
    save_report(counters, "ip_report.txt")
    print("Done!")




