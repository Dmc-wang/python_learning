#字符串反转（不用函数）
s = input("请输入一个字符串：")
print(s)
reversed_s=""
for char in s:
    reversed_s = char + reversed_s
print(reversed_s)

"""
"a" + "" = "a"
"b" + "a" = "ba"
"c" + "ba" = "cba"
"""