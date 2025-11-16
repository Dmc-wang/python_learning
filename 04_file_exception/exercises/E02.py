#练习 2：读取文件并统计行数
def count_files(filename: str) -> int:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        print("File not found")
        return 0

if __name__ == '__main__':
    print(count_files("e01_test.txt"))
    print(count_files("e02_test.txt"))