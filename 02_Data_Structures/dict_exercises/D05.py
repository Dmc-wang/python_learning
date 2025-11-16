# D5：模拟一个“学生成绩登记管理系统”：
#     添加学生和他的成绩
#     删除学生和他的成绩
#     查询学生和他的成绩
students = {}

while True:
    print("\n学生成绩管理系统")
    print("1. 添加学生和成绩")
    print("2. 删除学生和成绩")
    print("3. 查询学生和成绩")
    print("4. 退出")
    choice = input("请输入操作编号：")

    if choice == "1":
        while True:
            name = input("请输入学生姓名：")
            score = input("请输入学生成绩：")
            students[name] = score
            print(f"已添加：{name}的成绩{score}")
            print(students)
            cont = input("是否继续添加？（y/s）：")
            if cont != 'y':
                break

    elif choice == "2":
        name = input("请输入要删除的学生姓名：")
        if name in students:
            del students[name]
            print(f"已删除{name}")
        print(students)
    elif choice == "3":
        name = input("请输入要查询的学生姓名：")
        if name in students:
            print(f"{name}的成绩为{students[name]}")
        else:
            print("未找到该学生")
    elif choice == "4":
        print("系统退出")
        break
    else:
        print("无效操作，请重试")