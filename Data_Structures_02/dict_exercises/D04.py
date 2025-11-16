# D4（应用）：把一个英文句子按单词频率统计
#     输入："hello world hello" → 输出词频字典
#sentence = input("请输入一个英文句子：")  #变量
sentence = "hello world hello"
print(sentence)
words = sentence.split()
print(words)
fred = {}

for word in words:
    if word in fred:
        fred[word] += 1
    else:
        fred[word] = 1
print(fred)
