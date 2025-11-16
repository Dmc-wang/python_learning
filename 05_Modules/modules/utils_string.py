#功能：把列表里每个字符串都转换成大写，返回新列表。
def upper_all(strings):
    return [s.upper() for s in strings]

#功能：统计字符串 s 中字符 ch 出现了多少次。
def count_char(s,ch):
    return s.count(ch)