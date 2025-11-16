# F2：实现一个统计单词数的函数
# 输入一段文字 → 返回单词数量
# （提示：用 split()）

def count_words(text):
    words = text.split()
    return len(words)

sentence = input("请输入一段英文文字：")
num = count_words(sentence)
print(num)