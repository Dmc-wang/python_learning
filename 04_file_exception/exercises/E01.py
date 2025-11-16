# 练习 1：写入 100 行随机数据到文件（含实用技巧）
# 工程级写法：
#     用 with
#     使用异常处理
#     使用 uuid 或 random 生成随机字符串
#     保证可读性

import uuid
def write_random_data(filename: str,lines: int = 100):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for _ in range(lines):
                f.write(str(uuid.uuid4()) + "\n")

    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == '__main__':
    write_random_data("e01_test.txt",100)
