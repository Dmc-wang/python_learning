# D3：交换字典的 key 和 value
#     {"a":1, "b":2} → {1:"a", 2:"b"}

d = {"a" : 1, "b" : 2, "c" : 3, "d" : 4}
print("交换前字典",d)
swapped = {}
for key, value in d.items():
    swapped[value]= key
print("交换后字典",swapped)