#判断一个单词是否是回文（palindrome）
#方法一:字符串反转
word = input("请输入一个单词: ")

print("方法一:字符串反转")
cleaned = word.lower().replace(" ", "")
if cleaned == cleaned[::-1]:
    print("是回文数")
else:
    print("不是回文数")

#双指针法
print("方法2：双指针法")
left,right=0,len(cleaned)-1

while left < right:
    if cleaned[left] != cleaned[right]:
        print("不是回文数")
    left += 1
    right -= 1
print("是回文数")




