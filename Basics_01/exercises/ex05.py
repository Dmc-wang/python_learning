#打印 1–100 中所有能被 3 整除的数
#每行输出4个，多的下一行
count=0
for i in range(1,100):
    if i % 3 == 0:
        print(f"{i:3}", end=" ")
        count +=1
        if count % 4 == 0:
            print()
if count % 4 !=0:
    print()
