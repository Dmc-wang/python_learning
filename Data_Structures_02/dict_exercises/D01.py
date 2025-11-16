#统计字符串中每个字符出现的次数
s=input("请输入一个字符串")
counts={}

# for char in s:
#     if char in counts:
#         counts[char]+=1
#     else:
#         counts[char]=1
# print("每个字符出现的次数",counts)

for char in s:                #[a,b,c]
    if char in counts:        #'a'  {'a':1,'b':1}
        counts[char] += 1
    else:
        counts[char] = 1      #增键，赋值
    print(counts[char])
