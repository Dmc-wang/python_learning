# 统计字符串中字符出现次数

def count_char(s: str, char: str) -> int:
    if len(char) != 1:
        raise ValueError("char must be a single character")
    return s.count(char)

print(count_char("abc", "a"))
