#with 上下文管理器（推荐）
with open("read.txt", "r", encoding = "utf-8") as f:
    content = f.read()

print(content)