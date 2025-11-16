#打印乘法表（9×9）
for i in range(1,10):
    for j in range(1,i + 1):
        print(f"{j}x{i}={j*i:2}", end=" ")
    print()