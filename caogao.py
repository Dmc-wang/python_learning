extensions = 'pNg,jpg,jpeg'
ext_list0 = extensions.lower()
print(ext_list0)
ext_list1 = extensions.lower().split(',')
print(ext_list1)
extensions = {f'.{ext.strip()}' for ext in ext_list1} #
print(extensions)