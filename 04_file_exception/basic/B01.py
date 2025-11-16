#打开文件
f = open("read.txt", "r", encoding="utf-8")
contents = f.read()
f.close()

print(contents)